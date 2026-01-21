import json
import re
from langchain.tools import tool
from util.logger_config import logger

def preprocess_query(query: str) -> str:
    """
    Normalizes and validates the user query before sending it to the agent.
    
    1. Normalization: Removes whitespace, standardizes spaces.
    2. Validation: Checks length constraints and empty content.
    """
    if not query:
        raise ValueError("Query cannot be empty.")

    # Normalization: internal whitespace compression (tab/newlines -> single space)
    cleaned_query = re.sub(r'\s+', ' ', query).strip()

    # Validation: Minimum length (avoids noise like '?', 'hi', 'a')
    if len(cleaned_query) < 4:
        raise ValueError("Query is too short. Please provide a specific question about the hotels.")

    # Validation: Maximum length (security & token limit protection)
    MAX_QUERY_LENGTH = 200
    if len(cleaned_query) > MAX_QUERY_LENGTH:
        logger.warning(f"Query too long ({len(cleaned_query)} chars). Truncating to {MAX_QUERY_LENGTH}.")
        cleaned_query = cleaned_query[:MAX_QUERY_LENGTH]

    return cleaned_query

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
                f"- Full Address: {full_address}\n"
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

# Global helper variable
_db_helper = None

def get_db_helper(json_path=None):
    global _db_helper
    if _db_helper is None and json_path:
        _db_helper = HotelDatabaseHelper(json_path)
    return _db_helper

@tool
def tool_calculate_prices(hotel_name: str) -> str:
    """
    Use this ONLY when the user asks for specific PRICE NUMBERS, MATH, 
    extra bed CHARGES, or meal plan COSTS. 
    Do NOT use this for addresses, location, or amenities.
    """
    helper = get_db_helper()
    if not helper: return "Error: Hotel Database not initialized"
    return helper.get_hotel_financials(hotel_name)

@tool
def tool_market_analysis(location: str) -> str:
    """
    Use this ONLY for COMPARING multiple hotels or LISTING hotels in a location.
    """
    helper = get_db_helper()
    if not helper: return "Error: Hotel Database not initialized"
    return helper.get_location_financial_report(location)
