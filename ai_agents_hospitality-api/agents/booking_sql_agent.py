import asyncio
import os
import hashlib
from collections import OrderedDict
from typing import Union
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_core.tools import tool

from util.configuration import settings
from util.logger_config import logger
from util.booking_sql_agent_util import get_hotel_capacity, get_hotels_data_path
from config.agent_config import get_agent_config

# Load configuration from centralized config system
config = get_agent_config()


# Initialize Database
db_uri = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
db = SQLDatabase.from_uri(db_uri)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=config.model,
    temperature=0,
    google_api_key=os.getenv("AI_AGENTIC_API_KEY")
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)


# Determine the correct path to hotel data files
hotels_data_path = get_hotels_data_path()
hotels_json_path = hotels_data_path / "hotels.json"

# Hotel Room Capacity Data (Extracted from hotels.json)
HOTEL_ROOMS_COUNT = get_hotel_capacity(hotels_json_path)

if not HOTEL_ROOMS_COUNT:
    logger.warning("HOTEL_ROOMS_COUNT is empty. Check if hotels.json exists and is readable at %s", hotels_json_path)

try:
    hotel_capacity_formatted = "\n".join([f"- {k}: {v}" for k, v in HOTEL_ROOMS_COUNT.items()])
except Exception as e:
    logger.error(f"Error formatting hotel capacity data: {e}")
    hotel_capacity_formatted = "No capacity data available."

SYSTEM_PREFIX = """
You are an expert hospitality data analyst. You are interacting with a PostgreSQL database bookings_db.
Your goal is to answer questions about bookings, revenue, occupancy, and other hospitality metrics.

Tables:
- bookings: id, hotel_name, room_id, room_type, room_category, check_in_date, check_out_date, total_nights, guest_first_name, guest_last_name, guest_country, guest_city, meal_plan, total_price

Key Metrics Definitions:
1. Bookings Count: Count of rows satisfying the condition.
2. Total Revenue: Sum of 'total_price'.
3. Occupancy Rate (%): 
    - Logic: Retrieve 'SUM(total_nights)' via SQL.
    - Calculation: Use the tool `calculate_occupancy_rate`. DO NOT calculate internally.
    - Inputs: total_occupied_nights (from SQL), total_available_rooms (from Capacity Map), days_in_period.
4. RevPAR (Revenue Per Available Room):
    - Logic: Retrieve 'SUM(total_price)' via SQL.
    - Calculation: Use the tool `calculate_revpar`. DO NOT calculate internally.
    - Inputs: total_revenue (from SQL), total_available_rooms (from Capacity Map), days_in_period.

Hotel Capacity Map (Number of Rooms per Hotel):
{hotel_capacity}

Process:
Step 1: Generate the SQL query based on natural language to extract the necessary aggregations (SUM(total_nights), SUM(total_price), etc.).
Step 2: Validate the generated SQL query using the `validate_sql_query` tool.
    - If valid: Proceed to Step 3.
    - If invalid or a syntax error occurs: Analyze the error message, CORRECT the SQL query, and RE-VALIDATE.
Step 3: Execute the validated query using `execute_sql_with_cache` tool (DO NOT use `sql_db_query`).
Step 4: Call the appropriate tool (`calculate_occupancy_rate` or `calculate_revpar`) with the SQL result, room count (from the map below), and number of days.
Step 5: Format the final answer using the tool's output.

Guidelines:
- When filtering by 'hotel_name', use ILIKE to handle potential capitalization differences (e.g., ILIKE '%Obsidian Tower%').
- For date calculations (Days_In_Period), use PostgreSQL built-in functions where possible, or use standard calendar days (Jan=31, etc).
- 2025 is NOT a leap year.
- Always refer to the Hotel Capacity Map for room counts; do not infer from data.
- NEVER perform complex division or multiplication for Occupancy/RevPAR in your head. USE THE TOOLS.
- ALWAYS validate your SQL (Step 2) before executing it (Step 3).
- ALWAYS use `execute_sql_with_cache` for query execution to enable caching and logging.

Example of expected Queries to Handle, including but not limited to:
- "Tell me the amount of bookings for Obsidian Tower in 2025"
- "What is the occupancy rate for Imperial Crown in January 2025?"
- "Show me the total revenue for hotels in Paris in Q1 2025"
- "Calculate the RevPAR for Grand Victoria in August 2025"
- "How many guests from Germany stayed at our hotels in 2025?"
- "Compare bookings by meal plan type across all hotels"

IMPORTANT:
- ALWAYS end your thought process with "Final Answer: [Your Answer]".
- If you have the answer, do not just output it. You MUST format it.

Return the final answer in a clear, professional text format, using markdown tables and bullet points to enhance readability.
""".format(hotel_capacity=hotel_capacity_formatted)

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
    @tool
    def validate_sql_query(query: str) -> str:
        """
        Validates a SQL query by running EXPLAIN. 
        Use this tool to check the syntax of your generated SQL before executing it.
        Returns "Valid" if the query syntax is correct.
        Returns the error message if the query contains syntax errors.
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
    @tool
    def execute_sql_with_cache(query: str) -> str:
        """
        Executes a SQL query with LRU caching.
        Use this tool to execute the validated SQL query against the database.
        Returns the query result.
        """
        query_hash = SQLQueryManager._get_query_hash(query)
        
        # Check cache
        if query_hash in SQLQueryManager._cache:
            logger.info(f"Cache Hit for query: {query}")
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
    def _parse_params(input_str: str) -> dict:
        """Parses a string of kwargs like 'key=value, key2=value2'."""
        params = {}
        try:
            parts = input_str.split(',')
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
    @tool
    def calculate_occupancy_rate(total_occupied_nights: Union[int, str], total_available_rooms: Union[int, str] = 0, days_in_period: Union[int, str] = 0) -> str:
        """
        Calculate the Occupancy Rate percentage.
        Formula: (total_occupied_nights / (total_available_rooms * days_in_period)) * 100
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
    @tool
    def calculate_revpar(total_revenue: Union[float, str], total_available_rooms: Union[int, str] = 0, days_in_period: Union[int, str] = 0) -> str:
        """
        Calculate Revenue Per Available Room (RevPAR).
        Formula: total_revenue / (total_available_rooms * days_in_period)
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

try:
    hotel_sql_agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            prefix=SYSTEM_PREFIX,
            handle_parsing_errors=True,
            max_execution_time=30,
            extra_tools=[
                HotelFinancialCalculator.calculate_occupancy_rate, 
                HotelFinancialCalculator.calculate_revpar,
                SQLQueryManager.validate_sql_query,
                SQLQueryManager.execute_sql_with_cache
            ]
        )
    # Explicitly force handle_parsing_errors in case the wrapper ignored it
    if hotel_sql_agent:
        hotel_sql_agent.handle_parsing_errors = True
except Exception as e:
    logger.error(f"Error initializing hotel_sql_agent: {e}")
    hotel_sql_agent = None

def answer_hotel_question_sql(question: str) -> str:
    """
    Answer a question about hotels using the SQL Agent.
    """
    try:
        logger.info(f"Processing SQL question: {question[:100]}...")
        
        if not hotel_sql_agent:
            return "Error: SQL Agent not initialized."

        # The key is "input" for the SQL Agent
        result = hotel_sql_agent.invoke({"input": question})
        
        # The output key is "output"
        return result["output"]
        
    except Exception as e:
        logger.error(f"Error processing SQL question: {e}", exc_info=True)
        return f"Error: {str(e)}"

async def handle_hotel_query_sql(user_query: str) -> str:
    """
    Async wrapper for SQL agent.
    """
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, answer_hotel_question_sql, user_query)
    return response