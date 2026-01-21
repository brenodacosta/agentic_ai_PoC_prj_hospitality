import json
import hashlib
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Union, Any
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from util.logger_config import logger
from util.configuration import PROJECT_ROOT, settings

from config.agent_config import get_agent_config, _load_config_file

# Load configuration from centralized config system
config = get_agent_config()

# Initialize Database
db_uri = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
db = SQLDatabase.from_uri(db_uri)

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

class SQLQueryManager:
    """
    Manages SQL query validation, execution, and caching.
    """
    _cache = OrderedDict()
    MAX_CACHE_SIZE = 5

    @staticmethod
    def _get_query_hash(query: str) -> str:
        """Generates a simple hash for the query."""
        return hashlib.md5(query.strip().encode()).hexdigest()

    @staticmethod
    def _log_query(query: str):
        """Logs the generated SQL query."""
        logger.info(f"Generated SQL Query: {query}")

    @staticmethod
    def validate_sql_query(query: str) -> str:
        """
        Validates a SQL query by running EXPLAIN. 
        """
        SQLQueryManager._log_query(query)
        try:
            # Check for typically dangerous operations just in case (e.g. DROP, DELETE)
            # The agent should be read-only, but being safe is better.
            forbidden = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "GRANT", "REVOKE"]
            if any(cmd in query.upper() for cmd in forbidden):
                return "Error: Data modification commands are strictly forbidden."

            # Use the existing db connection to run EXPLAIN
            # This checks syntax and table existence without running the full query
            db.run(f"EXPLAIN {query}")
            return "Valid"
        except Exception as e:
            # Capture and return the specific SQL error so the agent can fix it
            return f"Invalid SQL Syntax: {str(e)}"

    @staticmethod
    def execute_sql_with_cache(query: str) -> str:
        """
        Executes a SQL query with LRU caching.
        """
        query_hash = SQLQueryManager._get_query_hash(query)
        
        # Check cache
        if query_hash in SQLQueryManager._cache:
            logger.info(f"Cache Hit for query: {query}. Returning cached result.")
            SQLQueryManager._cache.move_to_end(query_hash)
            return SQLQueryManager._cache[query_hash]["result"]
            
        # Execute
        try:
             # Use the global db instance
             result = db.run(query)
             
             # Store in cache
             SQLQueryManager._cache[query_hash] = {"query": query, "result": result}
             
             # Enforce LRU size
             if len(SQLQueryManager._cache) > SQLQueryManager.MAX_CACHE_SIZE:
                 SQLQueryManager._cache.popitem(last=False) # pop first (Least Recently Used)
                 
             return result
        except Exception as e:
            return f"Error executing SQL: {e}"

class HotelFinancialCalculator:
    
    @staticmethod
    def _parse_params(input_val: Union[str, int, float]) -> dict:
        """Parses a string of kwargs like 'key=value, key2=value2'."""
        params = {}
        if not isinstance(input_val, str):
            return params
            
        try:
            parts = input_val.split(',')
            for part in parts:
                if '=' in part:
                    k, v = part.split('=', 1)
                    k = k.strip()
                    v = v.strip()
                    # Try to convert to int or float
                    if v.isdigit():
                         v = int(v)
                    else:
                        try:
                            v = float(v)
                        except ValueError:
                            pass
                    params[k] = v
        except Exception:
            pass
        return params

    @staticmethod
    def calculate_occupancy_rate(total_occupied_nights: Union[int, str], total_available_rooms: Union[int, str] = 0, days_in_period: Union[int, str] = 0) -> str:
        """
        Calculate the Occupancy Rate percentage.
        """
        # Handle case where agent passes all args as a single string
        if isinstance(total_occupied_nights, str) and '=' in total_occupied_nights:
             params = HotelFinancialCalculator._parse_params(total_occupied_nights)
             total_occupied_nights = params.get('total_occupied_nights', 0)
             total_available_rooms = params.get('total_available_rooms', total_available_rooms)
             days_in_period = params.get('days_in_period', days_in_period)

        try:
            # Ensure types
            occupied = float(total_occupied_nights)
            rooms = float(total_available_rooms) 
            days = float(days_in_period)

            if rooms <= 0 or days <= 0:
                return "Error: Invalid capacity or period."
            
            numerator = occupied
            denominator = rooms * days
            
            if denominator == 0:
                return "0%"
                
            occupancy = (numerator / denominator) * 100
            return f"{occupancy:.2f}%"
        except Exception as e:
            return f"Error calculating occupancy: {e}"

    @staticmethod
    def calculate_revpar(total_revenue: Union[float, str], total_available_rooms: Union[int, str] = 0, days_in_period: Union[int, str] = 0) -> str:
        """
        Calculate Revenue Per Available Room (RevPAR).
        """
         # Handle case where agent passes all args as a single string
        if isinstance(total_revenue, str) and '=' in total_revenue:
             params = HotelFinancialCalculator._parse_params(total_revenue)
             total_revenue = params.get('total_revenue', 0.0)
             total_available_rooms = params.get('total_available_rooms', total_available_rooms)
             days_in_period = params.get('days_in_period', days_in_period)

        try:
            revenue = float(total_revenue)
            rooms = float(total_available_rooms)
            days = float(days_in_period)

            if rooms <= 0 or days <= 0:
                return "Error: Invalid capacity or period."
                
            numerator = revenue
            denominator = rooms * days
            
            if denominator == 0:
                return "$0.00"
                
            revpar = numerator / denominator
            return f"${revpar:.2f}"
        except Exception as e:
            return f"Error calculating RevPAR: {e}"

# --- Tool Wrappers ---

@tool
def tool_validate_sql_query(query: str) -> str:
    """
    Validates a SQL query by running EXPLAIN. 
    Use this tool to check the syntax of your generated SQL before executing it.
    Returns "Valid" if the query syntax is correct.
    Returns the error message if the query contains syntax errors.
    """
    return SQLQueryManager.validate_sql_query(query)

@tool
def tool_execute_sql_with_cache(query: str) -> str:
    """
    Executes a SQL query with LRU caching.
    Use this tool to execute the validated SQL query against the database.
    Returns the query result.
    """
    return SQLQueryManager.execute_sql_with_cache(query)

@tool
def tool_calculate_occupancy_rate(total_occupied_nights: Union[int, str], total_available_rooms: Union[int, str] = 0, days_in_period: Union[int, str] = 0) -> str:
    """
    Calculate the Occupancy Rate percentage.
    Formula: (total_occupied_nights / (total_available_rooms * days_in_period)) * 100
    """
    return HotelFinancialCalculator.calculate_occupancy_rate(total_occupied_nights, total_available_rooms, days_in_period)

@tool
def tool_calculate_revpar(total_revenue: Union[float, str], total_available_rooms: Union[int, str] = 0, days_in_period: Union[int, str] = 0) -> str:
    """
    Calculate Revenue Per Available Room (RevPAR).
    Formula: total_revenue / (total_available_rooms * days_in_period)
    """
    return HotelFinancialCalculator.calculate_revpar(total_revenue, total_available_rooms, days_in_period)
