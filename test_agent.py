import os, logging
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
from agent import StockAgent
agent = StockAgent()
answer = agent.run("PTT เป็นบริษัทอะไร มีธุรกิจอะไรบ้าง?")
print("\n=== คำตอบ ===")
print(answer)
