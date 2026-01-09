from langchain_community.utilities import SQLDatabase
from sqlalchemy.exc import OperationalError, ProgrammingError

# Configuration
DB_URI = "postgresql://postgres:postgres@localhost:5432/bookings_db"
QUERY = "SELECT COUNT(*) FROM bookings WHERE hotel_name = 'Imperial Crown' AND check_in_date >= '2023-01-01';"
QUERY_2 = "SELECT hotel_name, SUM(total_price) as revenue FROM bookings WHERE check_in_date >= '2024-01-01' GROUP BY hotel_name LIMIT 3;"

def test_connection():
    print("--- Attempting to connect to Database ---")
    
    try:
        # 1. Initialize the Database
        # This sets up the engine but acts lazily; the real connection happens when we run a command.
        db = SQLDatabase.from_uri(DB_URI)
        
        # 2. Check for Tables
        # This is a good "pulse check" to see if we can actually read the schema
        tables = db.get_usable_table_names()
        print(f"✅ Connection successful! Found tables: {tables}")
        
        # 3. Run the specific query
        print(f"\n--- Running Query 1: {QUERY} ---")
        result = db.run(QUERY)
        
        # LangChain usually returns the result as a string representation of the list/tuple
        print(f"✅ Query 1 Result: {result}")

        # 4. Run the second query (Aggregation & Date Filtering)
        print(f"\n--- Running Query 2: {QUERY_2} ---")
        result_2 = db.run(QUERY_2)
        print(f"✅ Query 2 Result: {result_2}")

    except OperationalError as e:
        print("❌ Connection Failed. Is the database running?")
        print(f"Error details: {e}")
    except ProgrammingError as e:
        print("❌ Query Failed. Check your table name or SQL syntax.")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_connection()