
try:
    from agents.hotel_sql_agent import hotel_sql_agent
    if hotel_sql_agent:
        print("Hotel SQL Agent initialized successfully.")
        print(f"Prefix: {hotel_sql_agent.agent.llm_chain.prompt.template[:100]}...")
    else:
        print("Hotel SQL Agent failed to initialize.")
except Exception as e:
    print(f"Error importing hotel_sql_agent: {e}")


