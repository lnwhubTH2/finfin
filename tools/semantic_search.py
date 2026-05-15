"""Tool 1: Semantic Search — ค้นหาข้อมูลจาก Knowledge Base"""
from rag.vectorstore import search

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "semantic_search",
        "description": (
            "ค้นหาข้อมูลพื้นฐานเกี่ยวกับหุ้นไทย (SET) หุ้น US และความรู้การลงทุน "
            "เช่น ข้อมูลบริษัท, P/E ratio, กลยุทธ์การลงทุน, การวิเคราะห์งบการเงิน"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "คำค้นหาเกี่ยวกับหุ้นหรือการลงทุน",
                },
                "n_results": {
                    "type": "integer",
                    "description": "จำนวนผลลัพธ์ที่ต้องการ (default: 3)",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
}


def run(query: str, n_results: int = 3) -> str:
    results = search(query, n_results=n_results)
    if not results:
        return "ไม่พบข้อมูลที่เกี่ยวข้องใน Knowledge Base"

    output_parts = []
    for i, r in enumerate(results, 1):
        output_parts.append(
            f"[ผลที่ {i}] (score: {r['score']:.4f}) [แหล่ง: {r['source']}]\n{r['content']}"
        )
    return "\n\n---\n\n".join(output_parts)
