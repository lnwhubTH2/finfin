---
title: Stock Investment Assistant
emoji: 📈
colorFrom: yellow
colorTo: orange
sdk: docker
app_port: 7860
pinned: false
---

# Agentic RAG — Stock Investment Assistant

AI Agent ที่ใช้ ReAct loop + RAG สำหรับตอบคำถามด้านการลงทุนและตลาดหุ้น (SET + US)

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Typhoon v2.5-30B-A3B-Instruct |
| Vector DB | ChromaDB (persistent local) |
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 |
| Real-time Data | yfinance |
| Web Search | DuckDuckGo |
| UI | Flask + Custom HTML |

## Tools

| Tool | Description |
|---|---|
| `semantic_search` | Vector search จาก ChromaDB |
| `web_search` | DuckDuckGo real-time news |
| `calculator` | คำนวณ P/E, ROE, Dividend Yield |
| `stock_price` | ราคาหุ้น real-time ผ่าน yfinance |