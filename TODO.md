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
| 1 | **ex_1_phase_1**: Install RAG dependencies (`langchain-community`, `chromadb`) | 2025-12-16 | ai_agents_hospitality-api/ |
| 2 | **ex_1_phase_1**: Generate full hotel dataset (50 hotels) using `gen_synthetic_hotels.py` | 2025-12-16 | bookings-db/ |
| 3 | **ex_1_phase_1**: Verify all hotel files are created (JSON, markdown files) | 2025-12-16 | bookings-db/output_files/hotels/ |
| 4 | **ex_1_phase_2**: Implement document loader for `hotels.json` (JSONLoader) | 2025-12-16 | agents/hotel_rag_agent.py |
| 5 | **ex_1_phase_2**: Implement document loader for `hotel_details.md` (TextLoader) | 2025-12-16 | agents/hotel_rag_agent.py |
| 6 | **ex_1_phase_2**: Implement document loader for `hotel_rooms.md` (TextLoader) | 2025-12-16 | agents/hotel_rag_agent.py |
| 7 | **ex_1_phase_2**: Configure RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200) | 2025-12-16 | agents/hotel_rag_agent.py |
| 8 | **ex_1_phase_2**: Create GoogleGenerativeAIEmbeddings instance | 2025-12-16 | agents/hotel_rag_agent.py |
| 9 | **ex_1_phase_2**: Build ChromaDB vector store from all documents | 2025-12-16 | agents/hotel_rag_agent.py |
| 10 | **ex_1_phase_2**: Persist vector store to disk for reuse | 2025-12-16 | agents/hotel_rag_agent.py |

### Medium Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| - | _No tasks_ | - | - |

### Low Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| - | _No tasks_ | - | - |

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

---

## 🐛 Technical Debt

| Description | Impact | Detected | Status |
|-------------|--------|----------|--------|
| _No technical debt registered_ | - | - | - |

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
- [ ] Install RAG dependencies (`langchain-community`, `chromadb`)
- [ ] Generate full hotel dataset (50 hotels) using `gen_synthetic_hotels.py`
- [ ] Verify all hotel files are created (JSON, markdown files)

#### Phase 2: Vector Store Creation
- [ ] Implement document loader for `hotels.json` (JSONLoader)
- [ ] Implement document loader for `hotel_details.md` (TextLoader)
- [ ] Implement document loader for `hotel_rooms.md` (TextLoader)
- [ ] Configure RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
- [ ] Create GoogleGenerativeAIEmbeddings instance
- [ ] Build ChromaDB vector store from all documents
- [ ] Persist vector store to disk for reuse

#### Phase 3: RAG Chain Implementation
- [ ] Create ChatGoogleGenerativeAI LLM instance (gemini-2.5-flash-lite, temperature=0)
- [ ] Implement RetrievalQA chain with vector store
- [ ] Design system prompt for hotel assistant context
- [ ] Configure retrieval parameters (k=5 documents)
- [ ] Test retrieval quality with sample queries

#### Phase 4: Agent Implementation
- [ ] Create hotel details agent function
- [ ] Implement query preprocessing (normalization, validation)
- [ ] Add response formatting (markdown structure)
- [ ] Handle edge cases (no results, ambiguous queries)

#### Phase 5: Integration & Testing
- [ ] Integrate RAG agent with WebSocket API
- [ ] Test with hotel location queries
- [ ] Test with meal plan and pricing queries
- [ ] Test with room comparison queries
- [ ] Verify performance (response time < 10s)
- [ ] Compare results with Exercise 0 (should be more accurate)

#### Phase 6: Optimization
- [ ] Tune chunk size and overlap if needed
- [ ] Optimize retrieval k parameter
- [ ] Add caching for frequent queries (optional)
- [ ] Document vector store persistence strategy

---

### Exercise 2: Booking Analytics with SQL Agent

#### Phase 1: Setup & Database Connection
- [ ] Start PostgreSQL database using `./start-app.sh --no_ai_agent`
- [ ] Install SQL dependencies (`langchain-community`, `psycopg2-binary`)
- [ ] Verify database connection (test connection string)
- [ ] Inspect database schema and understand table structure
- [ ] Load sample booking data to test queries

#### Phase 2: SQL Database Integration
- [ ] Create SQLDatabase instance from connection URI
- [ ] Test basic SQL queries manually (SELECT, COUNT, SUM)
- [ ] Verify database schema introspection works
- [ ] Test date filtering and aggregation queries

#### Phase 3: SQL Agent Implementation
- [ ] Create SQLDatabaseToolkit with database and LLM
- [ ] Implement create_sql_agent with proper system prompt
- [ ] Configure agent for hospitality context (hotel names, dates, metrics)
- [ ] Add custom system prompt explaining booking schema
- [ ] Test agent with simple queries (booking counts)

#### Phase 4: Analytics Calculations
- [ ] Implement bookings count query logic
- [ ] Implement occupancy rate calculation (two-step: query + formula)
- [ ] Implement total revenue aggregation
- [ ] Implement RevPAR calculation (revenue / available room-nights)
- [ ] Handle edge cases (no bookings, division by zero)

#### Phase 5: Two-Step Query Process
- [ ] Implement Step 1: Generate SQL from natural language
- [ ] Implement Step 2: Execute query and format results
- [ ] Add query validation before execution
- [ ] Implement result formatting (tables, markdown)
- [ ] Add error handling for SQL syntax errors

#### Phase 6: Advanced Queries & Testing
- [ ] Test with date range queries (months, quarters, years)
- [ ] Test with hotel-specific filters
- [ ] Test with guest country/city filters
- [ ] Test with meal plan comparisons
- [ ] Verify occupancy and RevPAR calculations are accurate
- [ ] Test with edge cases (empty results, invalid dates)

#### Phase 7: Integration & Error Handling
- [ ] Integrate SQL agent with WebSocket API
- [ ] Add comprehensive error handling (connection errors, query errors)
- [ ] Implement query timeout protection
- [ ] Add logging for debugging SQL generation
- [ ] Test end-to-end with WebSocket interface

#### Phase 8: Optimization & Documentation
- [ ] Optimize system prompt for better SQL generation
- [ ] Add query result caching for common queries (optional)
- [ ] Document SQL agent limitations and best practices
- [ ] Add code comments and docstrings

---

## 📊 Quick Summary

```
📌 Pending:  10
🔥 In progress: 0
✅ Completed: 20
🐛 Technical debt: 0
🎓 Workshop Exercises: 3 (Exercise 0, 1, 2)
```

> ⚠️ **Remember**: Update this file after each work session
