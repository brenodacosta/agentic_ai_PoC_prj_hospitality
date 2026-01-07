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

# Helper class to read the JSON directly for math/list questions
class HotelDatabaseHelper:
    def __init__(self, json_path):
        self.data = []
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                self.data = json.load(f).get("Hotels", [])
    
    def get_hotels_by_location(self, location: str) -> str:
        matches = []
        for h in self.data:
            loc_data = h.get('Address', {})
            # Search in City and Country
            full_loc = f"{loc_data.get('City', '')} {loc_data.get('Country', '')}"
            if location.lower() in full_loc.lower():
                matches.append(f"- {h['Name']} ({loc_data.get('City')})")
        return "\n".join(matches) if matches else "No hotels found."

    def get_hotel_financials(self, hotel_name: str) -> str:
            # Fuzzy match the name
            target = next((h for h in self.data if hotel_name.lower() in h["Name"].lower()), None)
            if not target: return "Hotel not found in database."
            
            # 1. Extract Address (The missing piece)
            addr = target.get("Address", {})
            full_address = f"{addr.get('Address')}, {addr.get('City')}, {addr.get('ZipCode')}, {addr.get('Country')}"
            
            # 2. Calculate Financials
            rooms = target.get("Rooms", [])
            if not rooms: return f"Address: {full_address}\n(No room data available)"
            
            peak = [r.get("PricePeakSeason", 0) for r in rooms]
            off = [r.get("PriceOffSeason", 0) for r in rooms]
            params = target.get("SyntheticParams", {})
            
            # 3. Return Combined Data
            return (
                f"DETAILS FOR {target['Name']}:\n"
                f"- Full Address: {full_address}\n"  # <--- ADDED THIS
                f"- Off-Season Price Range: ${min(off)} - ${max(off)}\n"
                f"- Peak-Season Price Range: ${min(peak)} - ${max(peak)}\n"
                f"- Meal Plan Pricing Multipliers: {json.dumps(params.get('MealPlanPrices'))}\n"
                f"- Extra Bed Charge: {params.get('ExtraBedChargePercentage')}%\n"
            )
    

    def get_location_financial_report(self, location: str) -> str:
            """Generates a financial summary for ALL hotels in a specific location."""
            # 1. Find all matching hotels
            matches = []
            for h in self.data:
                loc_data = h.get('Address', {})
                full_loc = f"{loc_data.get('City', '')} {loc_data.get('Country', '')}"
                
                # We match strictly on the location provided (e.g. "France" or "Paris")
                if location.lower() in full_loc.lower():
                    matches.append(h)
            
            if not matches:
                return f"No hotels found in {location}."

            # 2. Build the Report
            report = [f"--- MARKET ANALYSIS FOR: {location} ({len(matches)} hotels) ---"]
            
            for h in matches:
                rooms = h.get("Rooms", [])
                if not rooms: continue
                
                # Extract Location Data explicitly
                addr = h.get('Address', {})
                city = addr.get('City', 'Unknown City')
                country = addr.get('Country', 'Unknown Country')
                
                # Math
                off = [r.get("PriceOffSeason", 0) for r in rooms]
                peak = [r.get("PricePeakSeason", 0) for r in rooms]
                params = h.get("SyntheticParams", {})
                meal_prices = params.get("MealPlanPrices", {})
                
                report.append(
                    f"HOTEL: {h['Name']}\n"
                    f"  - Location: {city}, {country}\n" 
                    f"  - Peak Range: ${min(peak)} - ${max(peak)}\n"
                    f"  - Off-Peak Range: ${min(off)} - ${max(off)}\n"
                    f"  - Half Board Multiplier: x{meal_prices.get('Half Board', 'N/A')}\n"
                    f"  - Extra Bed: {params.get('ExtraBedChargePercentage')}%\n"
                )
                
            return "\n".join(report)

# Initialize the helper (Assuming 'hotels_data_path' is defined in your config area)
# If not, use: Path("path/to/your/data")


db_helper = HotelDatabaseHelper(hotels_data_path / "hotels.json")

# # Define the Tools the Agent can use
# @tool
# def tool_list_hotels(location: str) -> str:
#     """Useful for listing, counting, or finding hotels in a specific city or country."""
#     return db_helper.get_hotels_by_location(location)

# @tool
# def tool_get_prices_and_policies(hotel_name: str) -> str:
#     """
#     Useful for getting specific details about a SINGLE hotel, including:
#     - Full Address and Location
#     - Price ranges and Booking costs
#     - Meal plan charges and policies
#     Input should be the hotel name.
#     """
#     return db_helper.get_hotel_financials(hotel_name)

# @tool
# def tool_get_market_analysis(location: str) -> str:
#     """
#     Useful for COMPARISONS or AGGREGATIONS. 
#     Use this when the user asks to "compare prices", "list meal charges", 
#     or "analyze" hotels across an entire city or country (e.g. "Paris", "Nice").
#     Returns a financial summary for all hotels in that location.
#     """
#     return db_helper.get_location_financial_report(location)

@tool
def tool_calculate_prices(hotel_name: str) -> str:
    """
    Use this ONLY when the user asks for specific PRICE NUMBERS, MATH, 
    extra bed CHARGES, or meal plan COSTS. 
    Do NOT use this for addresses, location, or amenities.
    """
    return db_helper.get_hotel_financials(hotel_name)

# Keep the Market Analysis (RAG cannot do this)
@tool
def tool_market_analysis(location: str) -> str:
    """
    Use this ONLY for COMPARING multiple hotels or LISTING hotels in a location.
    """
    return db_helper.get_location_financial_report(location)


# Wrap your existing vectorstore into a tool
tool_vector_search = create_retriever_tool(
    vectorstore.as_retriever(search_kwargs={"k": 5}),
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
    1. **The Library (tool_vector_search):** This is your PRIMARY source. Use it for:
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