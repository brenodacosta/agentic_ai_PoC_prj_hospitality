from langchain_community.document_loaders import JSONLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
import json
import asyncio
from langchain_core.documents import Document

from util.configuration import PROJECT_ROOT
from util.logger_config import logger
from config.agent_config import get_agent_config, _load_config_file
from util.rag_agent_util import get_db_helper, tool_calculate_prices, tool_market_analysis

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate
import json

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
    print("Existing Paths:")
    print(HOTELS_DATA_PATH_EXTERNAL.exists() and (HOTELS_DATA_PATH_EXTERNAL / "hotels.json").exists())
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

# Load hotel data path
# Determine the correct path to hotel data files
hotels_data_path = _get_hotels_data_path()

# Check if vector store is empty; if so, load and process data
if vectorstore._collection.count() == 0:
    logger.info("Vector store is empty. Loading data with Context Injection...")
    documents = []

    # ==========================================
    # 1. PROCESS JSON (Source of Truth for Rules)
    # ==========================================
   
    hotels_json_path = hotels_data_path / "hotels.json"
    if hotels_json_path.exists():
        try:
            with open(hotels_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                hotels_list = data.get("Hotels", [])
                
                for hotel in hotels_list:
                    # Flatten the nested Address
                    addr = hotel.get("Address", {})
                    full_address = f"{addr.get('Address')}, {addr.get('City')}, {addr.get('ZipCode')}, {addr.get('Country')}"
                    
                    # Flatten SyntheticParams (The "Hidden" Business Rules)
                    params = hotel.get("SyntheticParams", {})
                    meal_prices = params.get("MealPlanPrices", {})
                    
                    # Create a "Business Rules" Narrative
                    # We explicitly phrase this so the LLM matches "discount" or "charge" queries
                    rules_text = (
                        f"Hotel Name: {hotel.get('Name')}\n"
                        f"Full Address: {full_address}\n"
                        f"City: {addr.get('City')}\n"
                        f"Business Rules & Charges:\n"
                        f"- Peak Season Occupancy Weight: {params.get('OccupancyPeakSeasonWeight')}%\n"
                        f"- Extra Bed Charge: {params.get('ExtraBedChargePercentage')}%\n"
                        f"- Base Discount: {params.get('OccupancyBaseDiscountPercentage')}%\n"
                        f"- Meal Plan Prices: Room Only x{meal_prices.get('Room Only')}, "
                        f"Half Board x{meal_prices.get('Half Board')}, "
                        f"Full Board x{meal_prices.get('Full Board')}\n"
                    )
                    
                    doc = Document(
                        page_content=rules_text,
                        metadata={"source": "hotels.json", "hotel_name": hotel.get("Name"), "type": "business_rules"}
                    )
                    documents.append(doc)
            logger.info(f"Processed {len(hotels_list)} hotels from JSON")
        except Exception as e:
            logger.error(f"Error loading hotels.json: {e}")

    # ==========================================
    # 2. PROCESS MARKDOWN (Rich Details)
    # ==========================================
    # We split by headers to keep room details together
    headers_to_split_on = [
        ("#", "hotel_name"),
        ("##", "section"),
        ("###", "room_id"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    # Load hotel_details.md (The detailed text)
    details_path = hotels_data_path / "hotel_details.md"
    if details_path.exists():
        with open(details_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        md_docs = markdown_splitter.split_text(md_content)
        
        # CRITICAL STEP: Context Injection
        # We rewrite the page_content to include the metadata
        for doc in md_docs:
            hotel_name = doc.metadata.get("hotel_name", "Unknown Hotel")
            section = doc.metadata.get("section", "General")
            room_id = doc.metadata.get("room_id", "")
            
            # Construct a clear context header
            context_header = f"Hotel: {hotel_name} | Section: {section}"
            if room_id:
                context_header += f" | Room: {room_id}"
            
            # Prepend context to the actual content
            doc.page_content = f"{context_header}\n---\n{doc.page_content}"
            doc.metadata["source"] = "hotel_details.md"
            
        documents.extend(md_docs)
        logger.info(f"Loaded {len(md_docs)} chunks from hotel_details.md")

    # ==========================================
    # 3. FINAL SPLIT & EMBED
    # ==========================================
    # Now valid to split further because every chunk has "Hotel: Name" written in it
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(documents)
    
    vectorstore.add_documents(splits)
    logger.info(f"Final Vector Store count: {vectorstore._collection.count()}")
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

# ==============================================================================
# 1. DEFINE TOOLS & HELPER (The "Left Brain")
# ==============================================================================
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate
import json

# Initialize the helper
get_db_helper(hotels_data_path / "hotels.json")

# Wrap your existing vectorstore into a tool
tool_vector_search = create_retriever_tool(
    vectorstore.as_retriever(search_kwargs={"k": 10}),
    "tool_search_descriptions",
    "Useful for questions about amenities, hotel vibes, descriptions, styles, and policies. NOT for listing hotels or calculating prices."
)

tools = [
    tool_calculate_prices,
    tool_market_analysis,
    tool_vector_search
]

# Update Prompt
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful Hybrid Hotel Agent.
    
    YOUR KNOWLEDGE SOURCES:
    1. **The Library (tool_search_descriptions):** This is your PRIMARY source. Use it for:
       - Hotel addresses, location, and contact info.
       - Amenities, room descriptions, and styles.
       - Policies, rules, and general details.
       
    2. **The Calculator (tool_calculate_prices):** Use this ONLY for:
       - Exact price checks (Peak vs Off-Peak).
       - Calculating discounts or meal plan costs.
       
    3. **The Analyst (tool_market_analysis):** Use this ONLY for:
       - "List all hotels in..."
       - "Compare prices between..."
       - "How many hotels..."
       - "Market analysis of..."
       - Aggregated data across multiple hotels.
       - "Summarize hotel options in..."
       - "What are the meal plan charges in..."

    STRATEGY:
    - Question: "Where is Obsidian Tower?" -> Use **Library** (RAG).
    - Question: "Does Grand Victoria have a pool?" -> Use **Library** (RAG).
    - Question: "Price of Grand Victoria?" -> Use **Calculator**.
    - Question: "Compare Paris hotels" -> Use **Analyst**.
     
    WHEN ANSWERING QUESTIONS:
    - Be accurate and specific
    - Reference hotel names, locations, and details from the data
    - If information is not available, say so clearly
    - Format responses in a clear, readable way using markdown
    - Use bullet points and tables when appropriate
    - Include specific prices, addresses, and details when available
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Initialize the Agent
agent = create_tool_calling_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ==============================================================================
# 3. UPDATED EXECUTION FUNCTION
# ==============================================================================

def answer_hotel_question_rag(question: str) -> str:
    """
    Answer a question about hotels using the Agentic RAG (Tools + Vectors).
    """
    try:
        logger.info(f"Processing RAG question: {question[:100]}...")
        
        # CHANGED: We now invoke the agent_executor, not qa_chain
        # The key is "input", not "query"
        result = agent_executor.invoke({"input": question})
        
        # The output key is "output", not "result"
        return result["output"]
        
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