import asyncio
import os
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType

from util.configuration import PROJECT_ROOT
from util.logger_config import logger
from config.agent_config import get_agent_config

# Load configuration from centralized config system
config = get_agent_config()

# Initialize Database
db = SQLDatabase.from_uri(
    "postgresql://postgres:postgres@localhost:5432/bookings_db"
)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=config.model,
    temperature=0,
    google_api_key=os.getenv("AI_AGENTIC_API_KEY")
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Hotel Room Capacity Data (Extracted from hotels.csv)
HOTEL_ROOMS_COUNT = {
    'Obsidian Tower': 47,
    'Royal Sovereign': 53,
    'Grand Victoria': 78,
    'Imperial Crown': 74,
    'Majestic Plaza': 60,
    'Regal Chambers': 35,
    'Sovereign Suites': 73,
    'Noble Abode': 80,
    'Heritage House': 53,
    'Legacy Lodge': 41,
    'Landmark Hotel': 72,
    'Apex Tower': 67,
    'Zenith Point': 45,
    'Meridian Suites': 45,
    'Nexus Hotel': 48,
    'Vertex Residences': 43,
    'Luminary Hotel': 53,
    'Solstice Plaza': 39,
    'Equinox Suites': 37,
    'Azure Retreat': 38,
    'Crimson Manor': 74,
    'Seraphina Hotel': 77,
    'Elysian Suites': 64,
    'Valerian Residences': 58,
    'Avant-Garde Hotel': 67,
    'Emerald Grove': 60,
    'Sapphire Coast': 68,
    'Golden Peak': 75,
    'Silver Stream': 44,
    'Diamond Falls': 57,
    'Crystal Bay': 79,
    'Ivory Dunes': 30,
    'Onyx Cliffs': 43,
    'Amber Forest': 76,
    'Pearl Lagoon': 71,
    'Celestial Heights': 75,
    'Aurora Suites': 35,
    'Stellar Hotel': 46,
    'Lunar Residences': 68,
    'Solar Plaza': 74,
    'Silk Road Hotel': 61,
    'Savoy London': 37,
    'Plaza New York': 46,
    'Ritz Paris': 78,
    'Danieli Venice': 76,
    'Raffles Singapore': 68,
    'Peninsula Hong Kong': 46,
    'Adlon Berlin': 62,
    'Imperial Vienna': 74,
    'Cipriani Venice': 75
}

SYSTEM_PREFIX = """
You are an expert hospitality data analyst. You are interacting with a PostgreSQL database bookings_db.
Your goal is to answer questions about bookings, revenue, occupancy, and other hospitality metrics.

Tables:
- bookings: id, hotel_name, room_id, room_type, room_category, check_in_date, check_out_date, total_nights, guest_first_name, guest_last_name, guest_country, guest_city, meal_plan, total_price

Key Metrics Definitions:
1. Bookings Count: Count of rows satisfying the condition.
2. Total Revenue: Sum of 'total_price'.
3. Occupancy Rate (%): (Total Occupied Nights / Total Available Room-Nights) * 100
   - Total Occupied Nights: SUM(total_nights) for bookings checking in within the period.
   - Total Available Room-Nights: (Number of Rooms in the Hotel) * (Number of Days in the Period).
   - MAX CAPACITY: Use the "Hotel Capacity Map" below to find the 'Number of Rooms' for the hotel. Do not try to count distinct room_ids in the table.
4. RevPAR (Revenue Per Available Room): Total Revenue / Total Available Room-Nights
   - Total Revenue: SUM(total_price) for the period.
   - Total Available Room-Nights: (Number of Rooms in the Hotel) * (Number of Days in the Period).

Hotel Capacity Map (Number of Rooms per Hotel):
{hotel_capacity}

Process:
Step 1: Generate the SQL query based on natural language to extract the necessary aggregations (SUM(total_nights), SUM(total_price), etc.).
Step 2: Execute the query against PostgreSQL, perform any necessary math (like Occupancy or RevPAR calculations using the capacity map), and format the results.

Instructions:
- When calculating 'Number of Days in the Period':
    - January = 31
    - Q1 = 90 days (Jan+Feb+Mar)
    - 2025 is not a leap year.
- If querying for a specific month/year, filter `check_in_date` accordingly.
- Return the final answer in a clear, professional text format.

Expected Queries to Handle:
- "Tell me the amount of bookings for Obsidian Tower in 2025"
- "What is the occupancy rate for Imperial Crown in January 2025?"
- "Show me the total revenue for hotels in Paris in Q1 2025"
- "Calculate the RevPAR for Grand Victoria in August 2025"
- "How many guests from Germany stayed at our hotels in 2025?"
- "Compare bookings by meal plan type across all hotels"
""".format(hotel_capacity=str(HOTEL_ROOMS_COUNT).replace('{', '{{').replace('}', '}}'))

try:
    hotel_sql_agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            prefix=SYSTEM_PREFIX,
            handle_parsing_errors=True
        )   
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