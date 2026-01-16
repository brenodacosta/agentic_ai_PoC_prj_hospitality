# 📋 TODO - Agentic AI Hospitality PoC

> Last updated: 2025-12-16

---

## 🔥 In Progress (Current)

| Task | Priority | Started | Notes |
|------|----------|---------|-------|
| _No tasks in progress_ | - | - | - |

---

## 📌 Pending (Backlog)

### High Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| 1 | **ex_1_phase_4**: Handle edge cases (no results, ambiguous queries) | 2026-01-08 | agents/hotel_rag_agent.py |

### Medium Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| 1 | **ex_1_phase_4**: Implement query preprocessing (normalization, validation) | 2026-01-08 | agents/hotel_rag_agent.py |
| 2 | **ex_1_phase_5**: Verify performance (response time < 10s) | 2026-01-08 | - |

### Low Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| 2 | **ex_1_phase_5**: Compare results with Exercise 0 (should be more accurate) | 2026-01-08 | - |
| 3 | **ex_1_phase_6**: Tune chunk size and overlap if needed | 2026-01-08 | agents/hotel_rag_agent.py |
| 4 | **ex_1_phase_6**: Optimize retrieval k parameter | 2026-01-08 | agents/hotel_rag_agent.py |
| 5 | **ex_1_phase_6**: Add caching for frequent queries (optional) | 2026-01-08 | - |

---

## ✅ Completed (Done)

| Task | Completed | Commit | Notes |
|------|-----------|--------|-------|
| **bugfix**: Fix docker compose command | 2025-12-11 | [a5b6bd8](https://github.com/delard-linux/agentic_ai_PoC_prj_hospitality/commit/a5b6bd89c76b683d38e3214efc720514bca546a1) | PR accepted in source repo. |
| **bugfix**: Fix pull policy to do never pull images from docker hub | 2025-12-11 | [fa68adf](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/fa68adf98c28787f7632ae97b1a9157ca26ca455) | PR accepted in source repo. |
| **ex_0_phase_1**: Configure Google Gemini API key as environment variable (AI_AGENTIC_API_KEY) | 2025-12-11 | N/A | Deployed and tested the key. Added the key to bashrc file. |
| **ex_0_phase_1**: Verify hotel files are created in bookings-db/output_files/hotels/ | 2025-12-16 | [ef0a0d6](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/ef0a0d601f090a1f16d9982ca66d6c22fe3352b8) | Data was created in the xlsx files |
| **ex_0_phase_1**: Generate synthetic hotel data (3 hotels) using gen_synthetic_hotels.py | 2025-12-16 | [ef0a0d6](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/ef0a0d601f090a1f16d9982ca66d6c22fe3352b8) | Data was created in the xlsx files |
| **ex_0_phase_1**: Install LangChain dependencies (langchain, langchain-google-genai) | 2025-12-16 | N/A | Libraries were created in the venv |
| **ex_0_phase_2**: Build LangChain chain (prompt template + LLM) | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | Most of the code was already given in the guide |
| **ex_0_phase_2**: Create ChatPromptTemplate with system prompt for hotel assistant | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | Most of the code was already given in the guide |
| **ex_0_phase_2**: Implement answer_hotel_question() function with file context | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | Most of the code was already given in the guide |
| **ex_0_phase_2**: Create function to load hotel details markdown (hotel_details.md) | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | Small change was done to retrieve data from hotels_details.md |
| **ex_0_phase_2**: Create function to load hotel JSON file (hotels.json) | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | Small change was done to retrieve data from hotels.json |
| **ex_0_phase_3**: Test with room information queries | 2025-12-16 | [d525544](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d525544fff549768fd82728ac8a43bf8ae615a61) | Most of the code was already given in the guide |
| **ex_0_phase_3**: Test with meal plan queries | 2025-12-16 | [d525544](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d525544fff549768fd82728ac8a43bf8ae615a61) | Most of the code was already given in the guide |
| **ex_0_phase_3**: Test with basic queries (hotel names, addresses, locations) | 2025-12-16 | [d525544](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d525544fff549768fd82728ac8a43bf8ae615a61) | Most of the code was already given in the guide |
| **ex_0_phase_3**: Create `handle_hotel_query_simple()` async function for WebSocket API | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | Most of the code was already given in the guide |
| **ex_0_phase_3**: Verify agent implementation with `test_exercise_0.py` | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | All 4 tests passed 🎉 |
| **ex_0_phase_3**: Verify error handling works correctly | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | - |
| **ex_0_phase_4**: Add code comments and docstrings | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | - |
| **ex_0_phase_4**: Verify responses are properly formatted | 2025-12-16 | [e411356](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/e411356fff549768fd82728ac8a43bf8ae615a61) | - |
| **ex_0_phase_4**: Test integration with WebSocket API endpoint | 2025-12-16 | [41acfff](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/41acffffa02424d534bd1ebc8142a295aabe650a) | Integration validated with `test_websocket_integration.py` |
| **ex_1_phase_1**: Install RAG dependencies (`langchain-community`, `chromadb`) | 2025-12-17 | N/A | Installed dependencies in venv |
| **ex_1_phase_1**: Generate full hotel dataset (50 hotels) using `gen_synthetic_hotels.py` | 2025-12-17 | [19b415b](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/19b415bc5f8ae50bd3217c8d74d571f98e0dee4a) | Generated 50 hotels dataset |
| **ex_1_phase_1**: Verify all hotel files are created (JSON, markdown files) | 2025-12-17 | [19b415b](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/19b415bc5f8ae50bd3217c8d74d571f98e0dee4a) | Verified output files exist |
| **ex_1_phase_2**: Implement document loader for `hotels.json` (JSONLoader) | 2025-12-17 | [05a0d4b](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/05a0d4b025426cd73fce61b6704987769f5f77c0) | Implemented JSONLoader |
| **ex_1_phase_2**: Implement document loader for `hotel_details.md` (TextLoader) | 2025-12-17 | [05a0d4b](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/05a0d4b025426cd73fce61b6704987769f5f77c0) | Implemented TextLoader for details |
| **ex_1_phase_2**: Implement document loader for `hotel_rooms.md` (TextLoader) | 2025-12-17 | [05a0d4b](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/05a0d4b025426cd73fce61b6704987769f5f77c0) | Implemented TextLoader for rooms |
| **ex_1_phase_2**: Configure RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200) | 2025-12-17 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | Configured text splitter |
| **ex_1_phase_2**: Create GoogleGenerativeAIEmbeddings instance | 2025-12-17 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | Initialized embeddings model |
| **ex_1_phase_2**: Build ChromaDB vector store from all documents | 2025-12-17 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | Vector store created |
| **ex_1_phase_2**: Persist vector store to disk for reuse | 2025-12-17 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | Vector store persisted |
| **ex_1_phase_3**: Create ChatGoogleGenerativeAI LLM instance (gemini-2.5-flash-lite, temperature=0) | 2025-12-18 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | - |
| **ex_1_phase_3**: Implement RetrievalQA chain with vector store | 2025-12-18 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | RAG implemented with tools to search in the database for queries such as "list all..." |
| **ex_1_phase_3**: Design system prompt for hotel assistant context | 2026-01-07 | [d2cb36f](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d2cb36f8def899fcbd614b86984af5e84595c5cc) | Prompt created to prioritize RAG, but to use other tools when RAG is not effective |
| **ex_1_phase_3**: Configure retrieval parameters (k=5 documents) | 2025-12-18 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | - |
| **ex_1_phase_3**: Test retrieval quality with sample queries | 2026-01-07 | [d2cb36f](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d2cb36f8def899fcbd614b86984af5e84595c5cc) | It's a trade-off between response time and retrieval accuracy |
| **ex_1_phase_4**: Create hotel details agent function | 2025-12-18 | [7d340e2](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/7d340e240d0929ee69bf4b484c11ab9ac67362db) | RAG implemented with tools to search in the database for queries such as "list all..." |
| **ex_1_phase_5**: Test with hotel location queries | 2026-01-07 | N/A | Tests passed 🎉 |
| **ex_1_phase_5**: Test with meal plan and pricing queries | 2026-01-07 | N/A | Tests passed 🎉 |
| **ex_1_phase_5**: Test with room comparison queries | 2026-01-07 | N/A | Tests passed 🎉 |
| **ex_1_phase_5**: Integrate RAG agent with WebSocket API | 2026-01-08 | [41acfff](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/41acffffa02424d534bd1ebc8142a295aabe650a) | Integration validated with `test_websocket_integration.py` |
| **ex_1_phase_6**: Document vector store persistence strategy | 2026-01-16 | [5c44c68](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/5c44c688c4f04897cbf76f985ee9d50f1dd469f9) | Documented in README_EXERCISE_1.md |
| **ex_2_phase_1**: Start PostgreSQL database using `./start-app.sh --no_ai_agent` | 2026-01-08 | N/A | - |
| **ex_2_phase_1**: Install SQL dependencies (`langchain-community`, `psycopg2-binary`) | 2026-01-08 | N/A | - |
| **ex_2_phase_1**: Verify database connection (test connection string) | 2026-01-08 | [0607217](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/0607217bf11fc55223c9497aee907f23d01a2943) | Test script for SQL connectivity |
| **ex_2_phase_1**: Inspect database schema and understand table structure | 2026-01-08 | N/A | - |
| **ex_2_phase_1**: Load sample booking data to test queries | 2026-01-08 | [0607217](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/0607217bf11fc55223c9497aee907f23d01a2943) | Test script for SQL connectivity |
| **ex_2_phase_2**: Create SQLDatabase instance from connection URI | 2026-01-08 | [0607217](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/0607217bf11fc55223c9497aee907f23d01a2943) | Test script for SQL connectivity |
| **ex_2_phase_2**: Test basic SQL queries manually (SELECT, COUNT, SUM) | 2026-01-08 | [0607217](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/0607217bf11fc55223c9497aee907f23d01a2943) | Test script for SQL connectivity |
| **ex_2_phase_2**: Verify database schema introspection works | 2026-01-08 | [0607217](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/0607217bf11fc55223c9497aee907f23d01a2943) | Test script for SQL connectivity |
| **ex_2_phase_2**: Test date filtering and aggregation queries | 2026-01-08 | [0607217](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/0607217bf11fc55223c9497aee907f23d01a2943) | Test script for SQL connectivity |
| **ex_2_phase_3**: Create SQLDatabaseToolkit with database and LLM | 2026-01-09 | [d157030](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d157030c91c982846b4e18c693bf1364cc0bc97f) | First functional SQL Agent for simple queries |
| **ex_2_phase_3**: Implement create_sql_agent with proper system prompt | 2026-01-09 | [d157030](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d157030c91c982846b4e18c693bf1364cc0bc97f) | First functional SQL Agent for simple queries |
| **ex_2_phase_3**: Configure agent for hospitality context | 2026-01-09 | [d157030](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d157030c91c982846b4e18c693bf1364cc0bc97f) | First functional SQL Agent for simple queries |
| **ex_2_phase_3**: Add custom system prompt explaining booking schema | 2026-01-09 | [d157030](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d157030c91c982846b4e18c693bf1364cc0bc97f) | First functional SQL Agent for simple queries |
| **ex_2_phase_3**: Test agent with simple queries (booking counts) | 2026-01-09 | [d157030](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d157030c91c982846b4e18c693bf1364cc0bc97f) | Test passed returning booking counts for specific hotel |
| **ex_2_phase_4**: Implement occupancy rate calculation (two-step: query + formula) | 2026-01-12 | [bb15c8b](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/bb15c8b3bcfde32e8f33f7063b5d2d4ea8c54c47) | Implemented with converting natural language to SQL query and returning formatted result |
| **ex_2_phase_4**: Implement total revenue aggregation | 2026-01-12 | [2530dee](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2530dee4989314f93fdf7ed1f67ba113e23c151c) | Tools created to help agent to perform calculations with retrieved data |
| **ex_2_phase_4**: Implement RevPAR calculation (revenue / available room-nights) | 2026-01-12 | [2530dee](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2530dee4989314f93fdf7ed1f67ba113e23c151c) | Tools created to help agent to perform calculations with retrieved data |
| **ex_2_phase_4**: Handle edge cases (no bookings, division by zero) | 2026-01-12 | [2530dee](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2530dee4989314f93fdf7ed1f67ba113e23c151c) | Functions prevent math edge cases and no data errors |
| **ex_2_phase_5**: Implement Step 1: Generate SQL from natural language | 2026-01-12 | [d157030](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d157030c91c982846b4e18c693bf1364cc0bc97f) | First agent handling simple queries |
| **ex_2_phase_5**: Implement Step 2: Execute query and format results | 2026-01-12 | [d157030](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d157030c91c982846b4e18c693bf1364cc0bc97f) | first agent handling simple queries |
| **ex_2_phase_5**: Implement result formatting (tables, markdown) | 2026-01-12 | [2530dee](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2530dee4989314f93fdf7ed1f67ba113e23c151c) | Results are formatted by default by the agent |
| **ex_1_phase_4**: Add response formatting (markdown structure) | 2026-01-07 | [d2cb36f](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/d2cb36f8def899fcbd614b86984af5e84595c5cc) | The system_prefix specifies that the result should be formatted in MD structure | 
| **ex_2_phase_7**: Integrate SQL agent with WebSocket API | 2026-01-12 | [2530dee](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2530dee4989314f93fdf7ed1f67ba113e23c151) | Booking SQL Agent integrated with WebSocket, pending orchestrator |
| **ex_2_phase_5**: Add query validation before execution | 2026-01-13 | [2abf679](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2abf679fac3cd65ad52fa310f91d2443c001eed3) | New function created as a tool to validate the SQL query before it is executed |
| **ex_2_phase_5**: Add error handling for SQL syntax errors | 2026-01-13 | [2abf679](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2abf679fac3cd65ad52fa310f91d2443c001eed3) | SQL errors are handled Interally via the model before the final answer |
| **ex_2_phase_6**: Test with date range queries (months, quarters, years) | 2026-01-13 | N/A | Test passed 🎉 see readme.md of the module for details |
| **ex_2_phase_6**: Test with hotel-specific filters | 2026-01-13 | N/A | Test passed 🎉 see readme.md of the module for details |
| **ex_2_phase_6**: Test with guest country/city filters | 2026-01-13 | N/A | Test passed 🎉 see readme.md of the module for details |
| **ex_2_phase_6**: Test with meal plan comparisons | 2026-01-13 | N/A | Test passed 🎉 see readme.md of the module for details |
| **ex_2_phase_6**: Verify occupancy and RevPAR calculations are accurate | 2026-01-13 | N/A | Test passed 🎉 see readme.md of the module for details |
| **ex_2_phase_6**: Test with edge cases (empty results, invalid dates) | 2026-01-13 | N/A | Test passed 🎉 see readme.md of the module for details |
| **ex_2_phase_7**: Test end-to-end with WebSocket interface | 2026-01-13 | N/A | Test passed 🎉 see readme.md of the module for details |
| **ex_2_phase_7**: Add comprehensive error handling (connection errors, query errors) | 2026-01-13 | [2abf679](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/2abf679fac3cd65ad52fa310f91d2443c001eed3) | Errors are handled gracefully |
| **ex_2_phase_7**: Implement query timeout protection | 2026-01-15 | [9facc48](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/9facc480a10bb3abf3481928f24689d92656d666) | Added `max_execution_time=30` to agent creation |
| **ex_2_phase_7**: Add logging for debugging SQL generation | 2026-01-15 | [9facc48](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/9facc480a10bb3abf3481928f24689d92656d666) | Implemented `_log_query` in `SQLQueryManager` |
| **ex_2_phase_8**: Optimize system prompt for better SQL generation | 2026-01-15 | [9facc48](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/9facc480a10bb3abf3481928f24689d92656d666) | Enhanced `SYSTEM_PREFIX` with clearer steps and `execute_sql_with_cache` instruction |
| **ex_2_phase_8**: Add query result caching for common queries (optional) | 2026-01-15 | [9facc48](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/9facc480a10bb3abf3481928f24689d92656d666) | Implemented `SQLQueryManager` with LRU cache and `execute_sql_with_cache` tool |
| **ex_2_phase_8**: Document SQL agent limitations and best practices | 2026-01-16 | [9716970](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/97169708584c336bd53ab24c0c3afcdbbc2ec090) | Documented in README_EXERCISE_2.md |
| **ex_2_phase_8**: Add code comments and docstrings | 2026-01-16 | [9716970](https://github.com/brenodacosta/agentic_ai_PoC_prj_hospitality/commit/97169708584c336bd53ab24c0c3afcdbbc2ec090) | Added verification logic comments |
---

## 🐛 Technical Debt

| Description | Impact | Detected | Status |
|-------------|--------|----------|--------|
| Agent relies on free tier Gemini API which limits full architecture testing | High | 2026-01-08 | Open |
| Agent does not fallback to other tools (DB, reports) if RAG fails | High | 2026-01-08 | Open |
| RAG agent tools (HotelDatabaseHelper) are coupled in same file, violating separation of concerns | Low | 2026-01-09 | Closed |
| Unused/Commented-out tools in RAG agent (tool_list_hotels, tool_get_prices...) adding clutter | Low | 2026-01-09 | Closed |

---

## 📝 Usage Notes

### How to manage this file

1. **New task** → Add to **Backlog** with date and priority
2. **Start task** → Move to **In Progress** with start date
3. **Complete task** → Move to **Completed** with date and commit hash
4. **Technical debt** → Register in specific section to not forget it

### Commit format
When you complete a task, reference the commit like this:
- Short hash: `abc1234`
- With link (if using GitHub): `[abc1234](url-to-commit)`

### Priorities
- 🔴 **High**: Blocks other tasks or is critical
- 🟡 **Medium**: Important but not urgent
- 🟢 **Low**: Nice-to-have, minor improvements

---

## 🎓 Workshop Exercise Plans

### Exercise 0: Simple Agentic Assistant with File Context

#### Phase 1: Setup & Data Preparation
- [✅] Install LangChain dependencies (`langchain`, `langchain-google-genai`)
- [✅] Configure Google Gemini API key as environment variable (`AI_AGENTIC_API_KEY`)
- [✅] Generate synthetic hotel data (3 hotels) using `gen_synthetic_hotels.py`
- [✅] Verify hotel files are created in `bookings-db/output_files/hotels/`

#### Phase 2: Core Implementation
- [✅] Create function to load hotel JSON file (`hotels.json`)
- [✅] Create function to load hotel details markdown (`hotel_details.md`)
- [✅] Implement `answer_hotel_question()` function with file context
- [✅] Create ChatPromptTemplate with system prompt for hotel assistant
- [✅] Build LangChain chain (prompt template + LLM)

#### Phase 3: Integration & Testing
- [✅] Create `handle_hotel_query_simple()` async function for WebSocket API
- [✅] Test with basic queries (hotel names, addresses, locations)
- [✅] Test with meal plan queries
- [✅] Test with room information queries
- [✅] Verify error handling works correctly

#### Phase 4: Documentation & Cleanup
- [✅] Add code comments and docstrings
- [✅] Test integration with WebSocket API endpoint
- [✅] Verify responses are properly formatted

---

### Exercise 1: Hotel Details with RAG

#### Phase 1: Setup & Data Preparation
- [✅] Install RAG dependencies (`langchain-community`, `chromadb`)
- [✅] Generate full hotel dataset (50 hotels) using `gen_synthetic_hotels.py`
- [✅] Verify all hotel files are created (JSON, markdown files)

#### Phase 2: Vector Store Creation
- [✅] Implement document loader for `hotels.json` (JSONLoader)
- [✅] Implement document loader for `hotel_details.md` (TextLoader)
- [✅] Implement document loader for `hotel_rooms.md` (TextLoader)
- [✅] Configure RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
- [✅] Create GoogleGenerativeAIEmbeddings instance
- [✅] Build ChromaDB vector store from all documents
- [✅] Persist vector store to disk for reuse

#### Phase 3: RAG Chain Implementation
- [✅] Create ChatGoogleGenerativeAI LLM instance (gemini-2.5-flash-lite, temperature=0)
- [✅] Implement RetrievalQA chain with vector store
- [✅] Design system prompt for hotel assistant context
- [✅] Configure retrieval parameters (k=5 documents)
- [✅] Test retrieval quality with sample queries

#### Phase 4: Agent Implementation
- [✅] Create hotel details agent function
- [ ] Implement query preprocessing (normalization, validation)
- [✅] Add response formatting (markdown structure)
- [ ] Handle edge cases (no results, ambiguous queries)

#### Phase 5: Integration & Testing
- [✅] Integrate RAG agent with WebSocket API
- [✅] Test with hotel location queries
- [✅] Test with meal plan and pricing queries
- [✅] Test with room comparison queries
- [ ] Verify performance (response time < 10s)
- [ ] Compare results with Exercise 0 (should be more accurate)

#### Phase 6: Optimization
- [ ] Tune chunk size and overlap if needed
- [ ] Optimize retrieval k parameter
- [ ] Add caching for frequent queries (optional)
- [✅] Document vector store persistence strategy

---

### Exercise 2: Booking Analytics with SQL Agent

#### Phase 1: Setup & Database Connection
- [✅] Start PostgreSQL database using `./start-app.sh --no_ai_agent`
- [✅] Install SQL dependencies (`langchain-community`, `psycopg2-binary`)
- [✅] Verify database connection (test connection string)
- [✅] Inspect database schema and understand table structure
- [✅] Load sample booking data to test queries

#### Phase 2: SQL Database Integration
- [✅] Create SQLDatabase instance from connection URI
- [✅] Test basic SQL queries manually (SELECT, COUNT, SUM)
- [✅] Verify database schema introspection works
- [✅] Test date filtering and aggregation queries

#### Phase 3: SQL Agent Implementation
- [✅] Create SQLDatabaseToolkit with database and LLM
- [✅] Implement create_sql_agent with proper system prompt
- [✅] Configure agent for hospitality context (hotel names, dates, metrics)
- [✅] Add custom system prompt explaining booking schema
- [✅] Test agent with simple queries (booking counts)

#### Phase 4: Analytics Calculations
- [✅] Implement bookings count query logic
- [✅] Implement occupancy rate calculation (two-step: query + formula)
- [✅] Implement total revenue aggregation
- [✅] Implement RevPAR calculation (revenue / available room-nights)
- [✅] Handle edge cases (no bookings, division by zero)

#### Phase 5: Two-Step Query Process
- [✅] Implement Step 1: Generate SQL from natural language
- [✅] Implement Step 2: Execute query and format results
- [✅] Add query validation before execution
- [✅] Implement result formatting (tables, markdown)
- [✅] Add error handling for SQL syntax errors

#### Phase 6: Advanced Queries & Testing
- [✅] Test with date range queries (months, quarters, years)
- [✅] Test with hotel-specific filters
- [✅] Test with guest country/city filters
- [✅] Test with meal plan comparisons
- [✅] Verify occupancy and RevPAR calculations are accurate
- [✅] Test with edge cases (empty results, invalid dates)

#### Phase 7: Integration & Error Handling
- [✅] Integrate SQL agent with WebSocket API
- [✅] Add comprehensive error handling (connection errors, query errors)
- [✅] Implement query timeout protection
- [✅] Add logging for debugging SQL generation
- [✅] Test end-to-end with WebSocket interface

#### Phase 8: Optimization & Documentation
- [✅] Optimize system prompt for better SQL generation
- [✅] Add query result caching for common queries (optional)
- [✅] Document SQL agent limitations and best practices
- [✅] Add code comments and docstrings

---

## 📊 Quick Summary

```
📌 Pending:  7
🔥 In progress: 0
✅ Completed: 80
🐛 Technical debt: 4
🎓 Workshop Exercises: 3 (Exercise 0, 1, 2)
```

> ⚠️ **Remember**: Update this file after each work session
