# Exercise 1: Hotel Details with RAG Implementation Report

## Overview

This document details the implementation of "Exercise 1", a specialised Retrieval-Augmented Generation (RAG) agent designed to answer complex queries about hotel details, amenities, room specifications, and policies.

Unlike the simple agent in Exercise 0, this implementation utilizes a **Vector Database (ChromaDB)** to store and retrieve unstructured text data (markdown documents), allowing the agent to handle a much larger knowledge base (50+ hotels) efficiently without overloading the LLM's context window. It combines this semantic search capability with deterministic tools to handle specific data lookups and calculations.

## System Architecture

### 1. Vector Database Integration (ChromaDB)
The agent relies on **ChromaDB** as its long-term memory store.
- **Embeddings**: Text data is converted into vector embeddings using `GoogleGenerativeAIEmbeddings` (model: `text-embedding-004`).
- **Storage**:
    - **Development/Docker**: Connects to a dedicated ChromaDB service container.
    - **Local Fallback**: Uses local file persistence (`chroma_db_data/`) if the service is unavailable.
- **Context Injection**: On startup, the system checks if the vector store is empty. If so, it automatically loads `hotel_details.md` and `hotel_rooms.md`, splits them into chunks (using `MarkdownHeaderTextSplitter`), generates embeddings, and indexes them.

### 2. FastAPI & WebSocket Handling
The agent is integrated into the `ai_agents_hospitality-api` service, maintaining a decoupled and non-blocking architecture:
- **Async Wrapper**: The core RAG logic (`answer_hotel_question_rag`) is synchronous. To prevent blocking the FastAPI event loop, it is wrapped in an `async` function (`handle_hotel_query_rag`) which offloads the execution to a thread pool.
- **Communication**: It communicates via the same WebSocket interface defined in `main.py`, allowing the frontend to send petitions and receive streaming or final responses without maintaining a persistent stateful connection to the logic core.

## Agent Design (`hotel_rag_agent.py`)

The core logic is implemented in `agents/hotel_rag_agent.py`.

### The "Hybrid Hotel Agent" Strategy
Pure RAG systems often struggle with specific types of queries, such as "List all hotels" (retrieval limits) or "Calculate the price" (LLM math hallucinations). To solve this, we implemented a **Hybrid Agent** using LangChain's Tool Calling capabilities.

The agent is equipped with three distinct "brains" (tools):

1.  **The Library (`tool_vector_search`)**: 
    -   **Function**: Performs semantic similarity search in ChromaDB.
    -   **Use Case**: Unstructured questions like "Does the Obsidian Tower have a pool?", "Describe the vibe of the Grand Victoria", or "What are the cancellation policies?".
    -   **Enhancement**: We use a `k=10` retrieval setting to ensure sufficient context is gathered.

2.  **The Calculator (`tool_calculate_prices`)**:
    -   **Function**: A deterministic Python function (from `rag_agent_util.py`).
    -   **Use Case**: Exact price lookups and math. E.g., "How much for 3 nights in a double room?".
    -   **Why**: LLMs are probabilistic; calculators are deterministic. This ensures pricing is 100% accurate.

3.  **The Analyst (`tool_market_analysis`)**:
    -   **Function**: Aggregates data across the entire dataset.
    -   **Use Case**: "List all hotels in Paris", "Compare prices between Cannes and Nice", "How many hotels do we have?".
    -   **Why**: RAG cannot "see" the entire dataset at once to count or list everything. This tool fills that gap.

### Prompt Engineering
The system prompt is tailored to act as a router and a formatter. It instructs the model on *which* tool to use based on the user's intent:

```text
STRATEGY:
- Question: "Where is Obsidian Tower?" -> Use **Library** (RAG).
- Question: "Price of Grand Victoria?" -> Use **Calculator**.
- Question: "Compare Paris hotels" -> Use **Analyst**.
```

This explicit "Chain of Thought" guidance prevents the model from trying to guess prices or hallucinate lists of hotels that weren't retrieved in the top-k documents.

## Utilities & Enhancements (`rag_agent_util.py`)

A specialized utility module, `rag_agent_util.py`, was created to empower the agent with capabilities that go beyond simple text generation. It centres around the `HotelDatabaseHelper` class.

### `HotelDatabaseHelper` Class
This class loads the structured `hotels.json` data directly, serving as a "ground truth" backup to the vector store.

#### Key Functions:

*   **`get_hotels_by_location(location)`**: 
    *   **Problem Solved**: Vector search retrieves chunks, not lists of all entities. Asking "List all hotels in France" to a RAG system usually results in an incomplete list based only on the retrieved chunks.
    *   **Solution**: This function iterates through the structured JSON and returns a complete, exact list of every hotel matching the location string.

*   **`get_hotel_financials(hotel_name)`**:
    *   **Problem Solved**: Pricing logic can be complex (peak vs off-season, meal plan multipliers).
    *   **Solution**: This function retrieves the raw data and presents a pre-calculated, structured summary of costs, ensuring the agent doesn't need to do complex arithmetic.

*   **`get_location_financial_report(location)`**:
    *   **Problem Solved**: Conducting a market analysis requires aggregated data from multiple entities simultaneously, which often exceeds the RAG context or retrieval window.
    *   **Solution**: This generates a dense financial summary for *all* hotels in a location, feeding the LLM a consolidated report that it can simply summarize for the user.

## Limitations & Technical Debt

While utilizing advanced patterns, the project currently faces specific constraints:

*   **Gemini API Limits**: The agent relies on the **Free Tier** of the Gemini API. This imposes strict Rate Limits (RPM) and Daily Limits.
    *   **Impact**: We cannot perform extensive load testing or high-frequency automated integration tests.
    *   **Consequence**: Occasional `429 Too Many Requests` errors may occur during rapid testing sequences.
*   **Vector Store Synchronization**: Currently, the vector store is populated on startup. If the underlying data changes, the index must be rebuilt (no incremental updates).

## Optimization & Robustness Features

### 1. Query Preprocessing & Validation
To ensure the agent operates efficiently and securely, a preprocessing pipeline was introduced in `rag_agent_util.py`.

*   **Sanitization**: The `preprocess_query(query)` function first normalizes the input by collapsing multiple whitespace characters (tabs, newlines, double spaces) into a single space.
*   **Validation**:
    *   **Minimum Length**: Queries shorter than 4 characters (e.g., "Hi", "?") are rejected immediately with a `ValueError`, saving unnecessary LLM calls and processing time.
    *   **Maximum Length**: To prevent context window overflows and potential abuse, queries are truncated to a sensible maximum of **200 characters**.
    *   **Empty Checks**: Blank or whitespace-only queries are caught early.

### 2. Performance Caching (LRU)
A Least Recently Used (LRU) caching mechanism, `RAGQueryCache`, has been integrated directly into the `answer_hotel_question_rag` flow.

*   **Mechanism**: Since the RAG agent does not generate intermediate SQL, the cache uses the **MD5 hash of the preprocessed user query** as the key.
*   **Storage**: Results (the final text answer) are stored in an in-memory `OrderedDict`.
*   **Eviction Policy**: The cache has a strict limit (default: 5 entries). When new queries arrive, the least recently accessed result is evicted to maintain memory efficiency.
*   **Benefit**: This ensures that users repeating questions (e.g., asking for the same address twice) get instant responses (~0ms) rather than waiting for the full Retrieval-Generation cycle (~3-8s).

## Verification & Tests

### The Test Suite (`test_exercise_1.py`)
A comprehensive testing script was built to validate the agent's capabilities across different query types. It bypasses the API server to test the logic core directly.

*   **Scope**: The script runs a suite of 11 distinct test cases covering:
    *   **Simple Facts**: "What is the full address of..."
    *   **Complex Aggregation**: "List all hotels in France..."
    *   **Math/Pricing**: "What is the cost of a Double room..."
    *   **Comparisons**: "Compare room prices between..."
    *   **Edge Cases**: Handling non-existent cities ("Bordeaux") or ambiguous queries ("Price of a room?").
*   **Performance Metrics**: It measures the execution time of each query, flagging any response that takes longer than 10 seconds.
*   **Automated Checks**: It counts successes vs. failures and provides a final pass/fail summary for the entire suite.

*(Screenshots of the tests performed will be added here)*
