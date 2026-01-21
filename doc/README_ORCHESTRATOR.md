# Orchestrator Agent Implementation Report

## Overview
This document details the implementation of the **Orchestrator Agent**, a semantic router designed to act as the central brain of the Hospitality AI API. Its primary function is to interpret user intent and intelligently delegate queries to the most appropriate specialized sub-agent: the **RAG Agent** (Exercise 1) for descriptive hotel queries or the **SQL Agent** (Exercise 2) for analytics and booking metrics.

## System Architecture

### 1. Integration with FastAPI (`main.py`)
The Orchestrator sits at the entry point of the WebSocket chat interface.
- **Import**: It is conditionally imported in `main.py` if the specialized agents are available.
- **Workflow**: When a message arrives at the `/ws/{uuid}` endpoint, instead of calling a specific agent directly, `main.py` invokes `handle_orchestrated_query(user_query)`.
- **Decoupling**: This abstraction allows the frontend to have a single entry point for all types of questions without needing to know which underlying system (Vector DB or SQL DB) handles the request.

### 2. The Routing Logic (`orchestrator.py`)
The core logic resides in `agents/orchestrator.py`. It uses a focused LLM call to classify intent before routing.

#### The Classification Prompt
The system uses a specialized prompt (`ROUTER_TEMPLATE`) that defines clear boundaries between the domains:

*   **SQL Domain**: Defined as "quantitative booking data, hospitality metrics, financial stats".
    *   *Keywords*: count, occupancy, revenue, RevPAR, comparisons by meal plan.
*   **RAG Domain**: Defined as "qualitative hotel information, general descriptions, amenities".
    *   *Keywords*: address, pool, hotel list, descriptions, static prices.
*   **AMBIGUOUS**: A catch-all category for vague inputs.

#### Execution Flow
1.  **Receive Query**: The async function `handle_orchestrated_query` receives the text.
2.  **Classify (Sync)**: A thread-safe call is made to `classify_query`. This invokes the LLM with `temperature=0` to strictly output one of three tokens: "SQL", "RAG", or "AMBIGUOUS".
3.  **Route (Async)**: Based on the returned token:
    -   **If "SQL"**: Awaits `handle_hotel_query_sql(query)`.
    -   **If "RAG"**: Awaits `handle_hotel_query_rag(query)`.
    -   **If "AMBIGUOUS"** or Error: Returns a helpful fallback message guiding the user on how to ask better questions.

## Implementation Details

### Configuration
The orchestrator shares the global `agent_config` used by other agents, utilizing the same `ChatGoogleGenerativeAI` model (`gemini-2.5-flash` or similar) but with a strict temperature setting to ensure deterministic routing decisions.

### Error Handling
- **Classification Failures**: If the LLM returns an unexpected string or fails, the system defaults to "AMBIGUOUS" rather than crashing.
- **Agent Failures**: Exceptions raised by the sub-agents are caught and logged, returning a user-friendly error message.

## Benefits
- **Unified Experience**: Users don't need to toggle between "Search Mode" and "Analytics Mode".
- **Efficiency**: Prevents sending simple static queries to the SQL engine (which would fail) and complex math queries to the RAG system (which would hallucinate).
- **Scalability**: New agents (e.g., a "CRM Agent" for modifying bookings) can be added simply by updating the Orchestrator's routing logic.

## Limitations
- **Latency**: Adding an orchestration step introduces a small overhead (typically <1s) as it requires an initial LLM call just for classification before the actual work begins.
- **Ambiguity**: Queries that mix domains (e.g., "Show me the revenue for the hotel with the biggest pool") may require multi-step reasoning which a simple router cannot handle effectively (currently routes based on the dominant intent).
