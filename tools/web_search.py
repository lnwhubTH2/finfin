"""Tool 2: Web Search — ค้นหาข่าวหุ้น real-time ผ่าน DuckDuckGo"""
from ddgs import DDGS

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "ค้นหาข่าวและข้อมูลหุ้น real-time จากอินเทอร์เน็ต "
            "ใช้เมื่อต้องการข้อมูลล่าสุด เช่น ข่าวบริษัท, ผลประกอบการล่าสุด, "
            "ความเคลื่อนไหวราคาหุ้น, ข่าวเศรษฐกิจ"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "คำค้นหาข่าวหุ้นหรือเศรษฐกิจ",
                },
                "max_results": {
                    "type": "integer",
                    "description": "จำนวนผลลัพธ์สูงสุด (default: 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


def run(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"ค้นหาไม่สำเร็จ: {e}"

    if not results:
        return "ไม่พบข้อมูลจากการค้นหา"

    output_parts = []
    for i, r in enumerate(results, 1):
        output_parts.append(
            f"[{i}] {r.get('title', '')}\n{r.get('body', '')}\nURL: {r.get('href', '')}"
        )
    return "\n\n---\n\n".join(output_parts)
