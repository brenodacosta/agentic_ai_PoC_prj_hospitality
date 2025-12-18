from langchain_community.document_loaders import JSONLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
import json
import asyncio
from langchain_core.documents import Document

from util.configuration import PROJECT_ROOT
from util.logger_config import logger
from config.agent_config import get_agent_config, _load_config_file

# Path to hotel data files (relative to project root)
# First try local data directory (for Docker), then fallback to bookings-db
HOTELS_DATA_PATH_LOCAL = PROJECT_ROOT / "data" / "hotels"
HOTELS_DATA_PATH_EXTERNAL = PROJECT_ROOT.parent / "bookings-db" / "output_files" / "hotels"

def _get_hotels_data_path():
    """
    Determine the correct path to hotel data files.
    Tries local path first (for Docker), then external path (for local development).
    
    Returns:
        Path: Path to the hotels data directory
    """
    config = _load_config_file()
    use_local = config.get("hotels", {}).get("local", True)
    if use_local and HOTELS_DATA_PATH_LOCAL.exists() and (HOTELS_DATA_PATH_LOCAL / "hotels.json").exists():
        logger.info(f"Using local hotel data path: {HOTELS_DATA_PATH_LOCAL}")
        return HOTELS_DATA_PATH_LOCAL
    elif HOTELS_DATA_PATH_EXTERNAL.exists() and (HOTELS_DATA_PATH_EXTERNAL / "hotels.json").exists():
        logger.info(f"Using external hotel data path: {HOTELS_DATA_PATH_EXTERNAL}")
        return HOTELS_DATA_PATH_EXTERNAL
    else:
        logger.warning(f"No valid hotel data path found; defaulting to local path: {HOTELS_DATA_PATH_LOCAL}")
        return HOTELS_DATA_PATH_LOCAL
    
# Create embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004", google_api_key=os.getenv("AI_AGENTIC_API_KEY"))

# Initialize Vector Store
chroma_host = os.getenv("CHROMA_HOST")
chroma_port = os.getenv("CHROMA_PORT")
collection_name = "hotel_info"

if chroma_host and chroma_port:
    logger.info(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}")
    import chromadb
    client = chromadb.HttpClient(host=chroma_host, port=int(chroma_port))
    vectorstore = Chroma(
        client=client,
        embedding_function=embeddings,
        collection_name=collection_name
    )
else:
    # Use local persistence
    persist_directory = str(PROJECT_ROOT / "chroma_db_data")
    logger.info(f"Using local ChromaDB persistence at {persist_directory}")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=collection_name
    )

# Check if we need to load data
if vectorstore._collection.count() == 0:
    logger.info("Vector store is empty. Loading data...")
    
    # Load hotel data
    hotels_data_path = _get_hotels_data_path()
    documents = []

    # Load hotels.json
    hotels_json_path = hotels_data_path / "hotels.json"
    if hotels_json_path.exists():
        try:
            with open(hotels_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Extract hotels list
                hotels_list = data.get("Hotels", [])
                for hotel in hotels_list:
                    # Convert hotel object to string representation
                    content = json.dumps(hotel, ensure_ascii=False, indent=2)
                    # Create document with metadata
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(hotels_json_path),
                            "type": "hotel_info",
                            "hotel_name": hotel.get("Name", "Unknown")
                        }
                    )
                    documents.append(doc)
            logger.info(f"Loaded {len(hotels_list)} hotels from {hotels_json_path}")
        except Exception as e:
            logger.error(f"Error loading hotels.json: {e}")

    # Load markdown files
    md_files = ["hotel_details.md", "hotel_rooms.md"]
    for md_file in md_files:
        file_path = hotels_data_path / md_file
        if file_path.exists():
            try:
                loader = TextLoader(str(file_path), encoding="utf-8")
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Loaded {md_file}")
            except Exception as e:
                logger.error(f"Error loading {md_file}: {e}")

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    # Add to vectorstore
    vectorstore.add_documents(splits)
    logger.info("Data loaded into vector store.")
else:
    logger.info(f"Vector store already populated with {vectorstore._collection.count()} documents.")

# Load configuration from centralized config system
config = get_agent_config()


# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=config.model,
    temperature=config.temperature,
    google_api_key=os.getenv("AI_AGENTIC_API_KEY")
)

# Define Prompt Template
template = """You are a helpful hotel assistant. Use the following pieces of context to answer the question at the end.

Context:
{context}

When answering questions:
- Be accurate and specific
- Reference hotel names, locations, and details from the data
- If information is not available, say so clearly
- Format responses in a clear, readable way using markdown
- Use bullet points and tables when appropriate
- Include specific prices, addresses, and details when available

Question: {question}

Helpful Answer:"""


print("Prompt Template:")
print(template)

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

# Create Retrieval Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

def answer_hotel_question_rag(question: str) -> str:
    """
    Answer a question about hotels using RAG.
    
    Args:
        question: The user's question
        
    Returns:
        str: The agent's response
    """
    try:
        logger.info(f"Processing RAG question: {question[:100]}...")
        result = qa_chain.invoke({"query": question})
        return result["result"]
    except Exception as e:
        logger.error(f"Error processing RAG question: {e}", exc_info=True)
        return f"Error: {str(e)}"

async def handle_hotel_query_rag(user_query: str) -> str:
    """
    Async wrapper for RAG agent.
    """
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, answer_hotel_question_rag, user_query)
    return response