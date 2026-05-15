"""Tool 3: Financial Calculator — คำนวณ metrics ทางการเงิน"""

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "คำนวณตัวชี้วัดทางการเงิน เช่น P/E ratio, P/BV ratio, "
            "Dividend Yield, ROE, Market Cap, EPS, หรือสมการทางคณิตศาสตร์ทั่วไป"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "สมการที่ต้องการคำนวณ เช่น '150 / 10' หรือ '(100 * 1.05) ** 3' "
                        "รองรับ +, -, *, /, **, (, )"
                    ),
                },
            },
            "required": ["expression"],
        },
    },
}

ALLOWED_NAMES = {"__builtins__": {}, "abs": abs, "round": round, "pow": pow}


def run(expression: str) -> str:
    try:
        safe_expr = expression.replace("^", "**")
        result = eval(safe_expr, ALLOWED_NAMES)  # noqa: S307
        return f"ผลลัพธ์: {expression} = {result:,.6g}"
    except ZeroDivisionError:
        return "ข้อผิดพลาด: หารด้วยศูนย์ไม่ได้"
    except Exception as e:
        return f"ข้อผิดพลาดในการคำนวณ: {e}"
