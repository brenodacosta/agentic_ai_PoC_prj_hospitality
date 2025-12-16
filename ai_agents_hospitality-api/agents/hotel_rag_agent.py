from langchain_community.document_loaders import JSONLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import json
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

# Create embeddings and vector store
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("AI_AGENTIC_API_KEY"))
splits = text_splitter.split_documents(documents)
vectorstore = Chroma.from_documents(splits, embeddings)