import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from util.logger_config import logger
from config.agent_config import get_agent_config

# Import specialized agents
from agents.booking_sql_agent import handle_hotel_query_sql
from agents.hotel_rag_agent import handle_hotel_query_rag

# Load configuration
config = get_agent_config()

# Initialize LLM for router
llm = ChatGoogleGenerativeAI(
    model=config.model,
    temperature=0,
    google_api_key=os.getenv("AI_AGENTIC_API_KEY")
)

# Define the routing prompt
ROUTER_TEMPLATE = """
You are a smart dispatcher for a hotel hospitality system. Your job is to classify the user's query into one of two categories: 'RAG' or 'SQL'.

Categories:
1. 'SQL': Select this if the user asks about quantitative booking data, hospitality metrics, financial stats, or existing reservation records.
   Examples (but not limited to):
   - "Tell me the amount of bookings..."
   - "What is the occupancy rate..."
   - "Show me the total revenue..."
   - "Calculate the RevPAR..."
   - "How many guests..."
   - "Compare bookings by meal plan..."

2. 'RAG': Select this if the user asks for qualitative hotel information, general descriptions, amenities, policies, location, specific hotel details or list of hotels.
   Examples (but not limited to):
   - "What is the full address of..."
   - "What are the meal charges..."
   - "List all hotels in France..."
   - "What is the discount for extra bed..."
   - "Compare room prices between..."
   - "Does this hotel have a pool?"

3. 'AMBIGUOUS': Select this if the query is unclear, too vague, or doesn't fit the specific domains above.

Query: {input}

Return ONLY the keyword: SQL, RAG, or AMBIGUOUS. Do not contain Markdown formatting.
"""

route_prompt = ChatPromptTemplate.from_template(ROUTER_TEMPLATE)
route_chain = route_prompt | llm | StrOutputParser()

def classify_query(query: str) -> str:
    """Synchronous wrapper for classification"""
    try:
        logger.info(f"Classifying query: {query}")
        response = route_chain.invoke({"input": query})
        
        # Log raw response for debugging
        logger.info(f"Raw Orchestrator response: '{response}'")
        
        # Clean the response (handle Markdown code blocks, whitespace)
        cleaned_response = response.strip().upper().replace("```", "").replace("MARKDOWN", "").strip()
        
        # Fallback if empty
        if not cleaned_response:
            logger.warning("Orchestrator returned empty response. Defaulting to AMBIGUOUS.")
            return "AMBIGUOUS"
            
        return cleaned_response
    except Exception as e:
        logger.error(f"Error classifying query: {e}")
        return "AMBIGUOUS"

async def handle_orchestrated_query(user_query: str) -> str:
    """
    Classifies the user query and routes it to the appropriate specialized agent.
    """
    try:
        # Use run_in_executor to avoid blocking the event loop with synchronous LLM call
        loop = asyncio.get_event_loop()
        intent = await loop.run_in_executor(None, classify_query, user_query)
        
        logger.info(f"Orchestrator decision: '{intent}'")

        if "SQL" in intent:
            logger.info("Routing to Booking SQL Agent")
            return await handle_hotel_query_sql(user_query)
        elif "RAG" in intent:
            logger.info("Routing to Hotel RAG Agent")
            return await handle_hotel_query_rag(user_query)
        else:
            logger.warning(f"Orchestrator could not route query. Intent: {intent}")
            return "I'm not sure which information you're looking for. Please be more specific. For example:\n- Ask about 'bookings', 'revenue', or 'occupancy' for analytics.\n- Ask about 'hotel details', 'amenities', or 'prices' for general info."

    except Exception as e:
        logger.error(f"Orchestrator error: {e}", exc_info=True)
        return f"Orchestrator Error: {str(e)}"
