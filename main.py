"""
Agentic RAG — Stock Investment Assistant
รัน: python main.py
"""
import io
import logging
import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler
from rich.prompt import Prompt
from rich.rule import Rule
from agent import StockAgent

# รองรับ UTF-8 บน Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        RichHandler(rich_tracebacks=True, show_path=False),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)

console = Console(highlight=False)


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]Agentic RAG - Stock Investment Assistant[/bold cyan]\n"
        "[dim]Powered by Typhoon API + ChromaDB + DuckDuckGo + yfinance[/dim]",
        border_style="cyan",
    ))
    console.print(f"[dim]Log file: {LOG_FILE}[/dim]\n")


def print_answer(answer: str):
    console.print(Rule("[bold green]คำตอบ[/bold green]"))
    console.print(Panel(answer, border_style="green", padding=(1, 2)))
    console.print()


EXAMPLE_QUERIES = [
    "PTT เป็นบริษัทอะไร มีธุรกิจอะไรบ้าง?",
    "ราคาหุ้น NVDA ตอนนี้เป็นเท่าไหร่?",
    "P/E ratio คืออะไร ใช้วิเคราะห์หุ้นยังไง?",
    "ถ้าหุ้น AAPL ราคา 180 USD และ EPS = 6.5 USD ค่า P/E เท่าไหร่?",
    "เปรียบเทียบ KBANK กับ SCB ใครน่าลงทุนกว่า?",
]


def main():
    print_banner()

    console.print("[bold]ตัวอย่างคำถาม:[/bold]")
    for i, q in enumerate(EXAMPLE_QUERIES, 1):
        console.print(f"  {i}. {q}")
    console.print()

    try:
        agent = StockAgent()
    except ValueError as e:
        console.print(f"[bold red]ข้อผิดพลาด:[/bold red] {e}")
        sys.exit(1)

    console.print("[dim]พิมพ์ 'exit' หรือ 'quit' เพื่อออกจากโปรแกรม[/dim]\n")

    while True:
        try:
            query = Prompt.ask("[bold yellow]คำถาม[/bold yellow]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]ออกจากโปรแกรม[/dim]")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "ออก"):
            console.print("[dim]ออกจากโปรแกรม[/dim]")
            break

        console.print(f"\n[dim]กำลังประมวลผล...[/dim]")
        try:
            answer = agent.run(query)
            print_answer(answer)
        except Exception as e:
            console.print(f"[bold red]เกิดข้อผิดพลาด:[/bold red] {e}")
            logging.exception("Unhandled error")


if __name__ == "__main__":
    main()
