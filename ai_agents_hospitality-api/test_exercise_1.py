"""
Test script for Exercise 1: RAG Agentic Assistant

This script tests the Exercise 1 agent implementation without needing
to start the full WebSocket server.

Usage:
    python test_exercise_1.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from agents.hotel_rag_agent import handle_hotel_query_rag


async def test_exercise_1():
    """Test the Exercise 1 agent with complex RAG queries."""
    
    # Check configuration
    try:
        from config.agent_config import get_agent_config
        config = get_agent_config()
        print(f"✅ Configuration loaded: provider={config.provider}, model={config.model}")
    except ValueError as e:
        print(f"❌ ERROR: Configuration error: {e}")
        print("Please set AI_AGENTIC_API_KEY environment variable or configure in config/agent_config.yaml")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to load configuration: {e}")
        return False
    
    print("🧪 Testing Exercise 1: RAG Agentic Assistant\n")
    print("=" * 60)
    
    # Test queries including complex ones to validate RAG
    test_queries = [
        "What is the full address of Obsidian Tower?",
        "What are the meal charges for Half Board in hotels in Paris?",
        "List all hotels in France with their cities",
        "What is the discount for extra bed in Grand Victoria?",
        "Compare room prices between peak and off season for hotels in Nice",
        "Which hotels in Paris have a Single room?",
        "What is the cost of a 'Double' room in Majestic Plaza during peak season including Full Board?",
        "Compare the 'OccupancyPeakSeasonWeight' between Grand Victoria and Obsidian Tower.",
        "List all distinct room types available across all hotels in Nice."
    ]
    
    success_count = 0
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/{len(test_queries)}: {query}")
        print("-" * 60)
        
        try:
            response = await handle_hotel_query_rag(query)
            print(f"✅ Response received ({len(response)} characters)")
            print(f"\n{response}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"\n📊 Results: {success_count}/{len(test_queries)} tests passed")
    
    if success_count == len(test_queries):
        print("✅ All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_exercise_1())
    sys.exit(0 if success else 1)
