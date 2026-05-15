# Agentic RAG — Stock Investment Assistant

> Business Practice #5: Final Mini Project | NLP Course

AI Agent ที่ใช้ ReAct loop + RAG สำหรับตอบคำถามด้านการลงทุนและตลาดหุ้น (SET + US)

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Typhoon v2.5-30B-A3B-Instruct (30B, open-source) |
| Vector DB | ChromaDB (persistent local) |
| Embedding Model | `paraphrase-multilingual-MiniLM-L12-v2` (Thai/EN) |
| Agent Framework | OpenAI Function Calling (ReAct loop) |
| Real-time Data | yfinance |
| Web Search | DuckDuckGo (DDGS, no API key) |
| Terminal UI | Rich |

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│              StockAgent                 │
│          (ReAct Loop, max 8 iter)       │
│                                         │
│  1. Call Typhoon LLM with tools list    │
│  2. LLM decides: stop or call tool      │
│  3. Execute tool → append result        │
│  4. Repeat until finish_reason="stop"   │
└──────────────┬──────────────────────────┘
               │  tool_calls
     ┌─────────┼─────────────┐
     ▼         ▼             ▼           ▼
semantic_  web_search   calculator  stock_price
 search    (DuckDuckGo)  (eval)     (yfinance)
     │
     ▼
ChromaDB ← ingest.py ← data/knowledge/*.md
```

---

## Tools

| Tool | Description |
|---|---|
| `semantic_search` | Vector search จาก ChromaDB (Thai + US stocks, investment guide) |
| `web_search` | DuckDuckGo real-time news & web |
| `calculator` | คำนวณ P/E, ROE, Dividend Yield และสูตรการเงิน |
| `stock_price` | ราคาหุ้น real-time ผ่าน yfinance (รองรับ SET `.BK`) |

---

## Project Structure

```
agentic rag/
├── agent.py              # ReAct Agent (StockAgent class)
├── main.py               # Interactive CLI (Rich UI + logging)
├── test_agent.py         # Quick test script
├── check_models.py       # ตรวจสอบ model ที่ใช้ได้ใน Typhoon API
├── requirements.txt
├── .env                  # TYPHOON_API_KEY (ไม่ commit)
├── .env.example
│
├── rag/
│   ├── vectorstore.py    # ChromaDB wrapper (search)
│   └── ingest.py         # โหลด .md → chunk → upsert ChromaDB
│
├── tools/
│   ├── semantic_search.py
│   ├── web_search.py
│   ├── calculator.py
│   └── stock_price.py
│
└── data/
    ├── knowledge/
    │   ├── thai_stocks.md      # PTT, KBANK, SCB, AOT, CPALL, ADVANC, GULF, BBL, DELTA
    │   ├── us_stocks.md        # AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA, BRK.B, JPM
    │   └── investment_guide.md # P/E, P/BV, ROE, ROA, DCF, DCA, etc.
    └── chroma_db/              # ChromaDB persistent storage (auto-created)
```

---

## Setup

### 1. ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า API Key

```bash
cp .env.example .env
# แก้ไข TYPHOON_API_KEY ใน .env
```

### 3. Ingest Knowledge Base (ครั้งแรก)

```bash
python rag/ingest.py
```

### 4. รัน Interactive CLI

```bash
# Windows
$env:PYTHONIOENCODING="utf-8"
python main.py
```

---

## Observability & Logging

ทุก iteration จะ log:
- `[ITERATION N]` — รอบที่ N ของ ReAct loop
- `[TOOL CALL] tool_name` — ชื่อ tool ที่ถูกเรียก
- `Args: {...}` — arguments ที่ส่งไป
- `Result: ...` — ผลลัพธ์ (truncate 500 chars)
- `[FINAL ANSWER]` — คำตอบสุดท้าย

Log ถูกบันทึกไว้ที่ `logs/agent_YYYYMMDD_HHMMSS.log` (UTF-8)

ตัวอย่าง log output:
```
10:00:01 | [USER] PTT เป็นบริษัทอะไร มีธุรกิจอะไรบ้าง?
10:00:01 | [ITERATION 1]
10:00:02 | [TOOL CALL] semantic_search
          |   Args: {"query": "PTT บริษัท ธุรกิจ", "n_results": 3}
          |   Result: [1] score=0.7291 | source=thai_stocks.md
          |   PTT (ปตท.) เป็นบริษัทพลังงานแห่งชาติ...
10:00:03 | [ITERATION 2]
10:00:05 | [FINAL ANSWER]
          | PTT (บริษัท ปตท. จำกัด (มหาชน)) เป็นบริษัทพลังงาน...
```

---

## ตัวอย่างคำถาม

```
PTT เป็นบริษัทอะไร มีธุรกิจอะไรบ้าง?
ราคาหุ้น NVDA ตอนนี้เป็นเท่าไหร่?
P/E ratio คืออะไร ใช้วิเคราะห์หุ้นยังไง?
ถ้าหุ้น AAPL ราคา 180 USD และ EPS = 6.5 USD ค่า P/E เท่าไหร่?
เปรียบเทียบ KBANK กับ SCB ใครน่าลงทุนกว่า?
```

---

## Knowledge Base

| ไฟล์ | เนื้อหา | จำนวน chunks |
|---|---|---|
| `thai_stocks.md` | PTT, KBANK, SCB, AOT, CPALL, ADVANC, GULF, BBL, DELTA | ~9 chunks |
| `us_stocks.md` | AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA, BRK.B, JPM | ~9 chunks |
| `investment_guide.md` | P/E, P/BV, EV/EBITDA, ROE, ROA, Dividend Yield, DCF, DCA | ~5 chunks |

Chunk size: 500 chars, overlap: 50 chars | Total: 23 chunks
