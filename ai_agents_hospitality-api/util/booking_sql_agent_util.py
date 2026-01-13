import json
from pathlib import Path
from typing import Dict
from util.logger_config import logger
from util.configuration import PROJECT_ROOT, settings

from config.agent_config import get_agent_config, _load_config_file

# Load configuration from centralized config system
config = get_agent_config()

HOTELS_DATA_PATH_LOCAL = PROJECT_ROOT / "data" / "hotels"
HOTELS_DATA_PATH_EXTERNAL = PROJECT_ROOT.parent / "bookings-db" / "output_files" / "hotels"


def get_hotel_capacity(json_path: Path) -> Dict[str, int]:
    """
    Reads the hotels.json file and returns a dictionary of hotel names and their room capacities.
    """
    hotel_capacity = {}
    if not json_path.exists():
        logger.error(f"hotels.json not found at {json_path}")
        return {}

    try:
        with open(json_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            hotels = data.get("Hotels", [])
            for hotel in hotels:
                name = hotel.get("Name")
                rooms = hotel.get("Rooms", [])
                
                if name:
                     hotel_capacity[name] = len(rooms)
                else:
                    logger.warning(f"Missing Name in hotel entry: {hotel.keys()}")
                    
    except Exception as e:
        logger.error(f"Error reading hotels.json: {e}")
    
    return hotel_capacity

def get_hotels_data_path():
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
