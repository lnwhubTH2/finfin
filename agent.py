"""Agentic RAG — ReAct Agent ที่ใช้ Typhoon API + Tools"""
import json
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv
from tools import semantic_search, web_search, calculator, stock_price

load_dotenv()

TYPHOON_BASE_URL = "https://api.opentyphoon.ai/v1"
MODEL = "typhoon-v2.5-30b-a3b-instruct"
MAX_ITERATIONS = 15

TOOLS = [
    semantic_search.TOOL_DEFINITION,
    web_search.TOOL_DEFINITION,
    calculator.TOOL_DEFINITION,
    stock_price.TOOL_DEFINITION,
]

TOOL_RUNNERS = {
    "semantic_search": lambda args: semantic_search.run(**args),
    "web_search": lambda args: web_search.run(**args),
    "calculator": lambda args: calculator.run(**args),
    "stock_price": lambda args: stock_price.run(**args),
}

SYSTEM_PROMPT = """คุณคือ AI Assistant ผู้เชี่ยวชาญด้านการลงทุนและตลาดหุ้น
คุณมีเครื่องมือ 4 อย่าง:
1. semantic_search — ค้นหาข้อมูลพื้นฐานหุ้น/การลงทุนจากฐานความรู้
2. web_search — ค้นหาข่าวและข้อมูล real-time
3. calculator — คำนวณ P/E, ROE, Dividend Yield และสมการการเงิน
4. stock_price — ดึงราคาหุ้นและข้อมูล real-time

กฎสำคัญ:
- ตอบเป็นภาษาไทย
- ใช้ tool ให้เหมาะสม อย่าเรียกเกิน 4-5 ครั้งต่อคำถาม
- เมื่อได้ข้อมูลเพียงพอแล้วให้สรุปคำตอบทันที ไม่ต้องหาเพิ่ม
- ถ้าเป็นคำถามทั่วไป ใช้ข้อมูลจาก semantic_search อย่างเดียวก็พอ
- ไม่จำเป็นต้องดึงราคาหุ้นทุกตัว ดึงแค่ 1-2 ตัวที่เกี่ยวข้องที่สุด
- ถ้าถูกถามเปรียบเทียบหุ้นมากกว่า 3 ตัว ให้ดึง stock_price แค่ 3 ตัวที่สำคัญที่สุด ที่เหลือใช้ข้อมูลจาก semantic_search หรือ web_search แทน
- เมื่อแนะนำหุ้น ให้เสนอทั้งหุ้นไทย (.BK) และหุ้น US เสมอ เพื่อให้ผู้ใช้มีตัวเลือกเปรียบเทียบ"""

logger = logging.getLogger("agent")


class StockAgent:
    def __init__(self):
        api_key = os.getenv("TYPHOON_API_KEY")
        if not api_key or api_key == "your-typhoon-api-key-here":
            raise ValueError("กรุณาตั้งค่า TYPHOON_API_KEY ใน .env ก่อน")
        self.client = OpenAI(api_key=api_key, base_url=TYPHOON_BASE_URL)

    def run(self, user_query: str) -> str:
        logger.info("=" * 60)
        logger.info(f"[USER] {user_query}")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]

        for iteration in range(1, MAX_ITERATIONS + 1):
            logger.info(f"\n[ITERATION {iteration}]")

            # บังคับสรุปในรอบสุดท้าย
            if iteration == MAX_ITERATIONS:
                messages.append({
                    "role": "user",
                    "content": "กรุณาสรุปคำตอบจากข้อมูลที่มีทั้งหมดตอนนี้เลย ไม่ต้องค้นหาเพิ่ม"
                })

            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto" if iteration < MAX_ITERATIONS else "none",
                max_tokens=4096,
            )

            msg = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # Agent ตัดสินใจหยุด — ส่งคำตอบสุดท้าย
            if finish_reason == "stop" or not msg.tool_calls:
                answer = msg.content or "ไม่สามารถตอบได้"
                logger.info(f"\n[FINAL ANSWER]\n{answer}")
                logger.info("=" * 60)
                return answer

            # Agent เรียก tool
            messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]})

            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                logger.info(f"\n[TOOL CALL] {tool_name}")
                logger.info(f"  Args: {json.dumps(tool_args, ensure_ascii=False)}")

                runner = TOOL_RUNNERS.get(tool_name)
                if runner:
                    tool_result = runner(tool_args)
                else:
                    tool_result = f"ไม่พบ tool ชื่อ '{tool_name}'"

                logger.info(f"  Result:\n{tool_result[:500]}{'...' if len(tool_result) > 500 else ''}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

        logger.warning("[AGENT] ถึงขีดจำกัด iteration แล้ว")
        return "ขออภัย ไม่สามารถประมวลผลได้ภายในขีดจำกัดที่กำหนด"
