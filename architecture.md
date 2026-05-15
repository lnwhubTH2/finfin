# Architecture Diagram — Agentic RAG Stock Assistant

## System Architecture (Mermaid)

```mermaid
flowchart TD
    User([User Query]) --> Agent

    subgraph Agent["StockAgent — ReAct Loop (max 8 iterations)"]
        direction TB
        LLM["Typhoon v2.5-30B\n(typhoon-v2.5-30b-a3b-instruct)"]
        Loop{{"finish_reason\n= stop?"}}
        LLM --> Loop
        Loop -- "No → tool_calls" --> Tools
        Tools --> LLM
    end

    Loop -- "Yes" --> Answer([Final Answer])

    subgraph Tools["Tools"]
        T1["semantic_search\n(ChromaDB vector search)"]
        T2["web_search\n(DuckDuckGo)"]
        T3["calculator\n(financial formulas)"]
        T4["stock_price\n(yfinance real-time)"]
    end

    subgraph VectorDB["Knowledge Base"]
        Ingest["ingest.py\n(chunk + embed)"]
        ChromaDB[("ChromaDB\n23 chunks")]
        MD["data/knowledge/*.md\n(thai_stocks, us_stocks,\ninvestment_guide)"]
        MD --> Ingest --> ChromaDB
    end

    T1 --> ChromaDB
    T2 --> Web[(DuckDuckGo\nReal-time Web)]
    T4 --> YF[(yfinance\nSET + NYSE/NASDAQ)]

    subgraph Observability["Observability & Logging"]
        Rich["Rich Terminal\n(colorized output)"]
        LogFile["logs/agent_*.log\n(UTF-8 file log)"]
    end

    Agent --> Rich
    Agent --> LogFile
```

---

## Data Flow

```
1. User types query
       │
2. Agent sends to Typhoon LLM with 4 tool definitions
       │
3. LLM returns tool_calls (ReAct: think → act)
       │
4. Agent executes tool(s):
   ├─ semantic_search  → embed query → cosine search ChromaDB → top-k docs + scores
   ├─ web_search       → DuckDuckGo DDGS → title + body + URL
   ├─ calculator       → restricted eval() → numeric result
   └─ stock_price      → yfinance Ticker → price, P/E, sector, mktcap
       │
5. Tool results appended to messages as role="tool"
       │
6. LLM synthesizes results → next iteration or final answer
       │
7. Return Thai-language answer + full log
```

---

## Tech Stack Summary (for slides)

| Layer | Technology | Detail |
|---|---|---|
| LLM | Typhoon API | v2.5-30B-A3B, open-source, ≤50B |
| Agent Pattern | ReAct | Reasoning + Acting loop |
| Vector DB | ChromaDB | Persistent local storage |
| Embedding | Sentence Transformers | `paraphrase-multilingual-MiniLM-L12-v2` |
| Real-time | yfinance | SET (`.BK`) + US stocks |
| Web Search | DuckDuckGo DDGS | No API key required |
| UI | Rich | Terminal panels + colorized logs |
| Language | Python 3.12 | Windows 11 |
