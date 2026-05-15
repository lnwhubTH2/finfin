"""Tool 4: Stock Price — ดึงราคาและข้อมูลหุ้น real-time ผ่าน yfinance"""
import yfinance as yf

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "stock_price",
        "description": (
            "ดึงราคาหุ้นปัจจุบันและข้อมูลพื้นฐาน เช่น P/E, Market Cap, 52-week high/low "
            "รองรับทั้งหุ้นไทย (ใส่ .BK ต่อท้าย เช่น PTT.BK) "
            "และหุ้น US (เช่น AAPL, MSFT, NVDA)"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": (
                        "Ticker symbol เช่น 'PTT.BK', 'KBANK.BK', 'AAPL', 'NVDA' "
                        "หุ้นไทยต้องใส่ .BK ต่อท้าย"
                    ),
                },
            },
            "required": ["ticker"],
        },
    },
}


def run(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        if not info or info.get("regularMarketPrice") is None:
            hist = stock.history(period="1d")
            if hist.empty:
                return f"ไม่พบข้อมูลหุ้น '{ticker}' กรุณาตรวจสอบ ticker symbol"
            price = hist["Close"].iloc[-1]
            return f"ราคาหุ้น {ticker}: {price:.2f}"

        price = info.get("regularMarketPrice") or info.get("currentPrice", "N/A")
        currency = info.get("currency", "")
        name = info.get("longName") or info.get("shortName", ticker)
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        pb_ratio = info.get("priceToBook")
        div_yield = info.get("dividendYield")
        week_high = info.get("fiftyTwoWeekHigh")
        week_low = info.get("fiftyTwoWeekLow")
        eps = info.get("trailingEps")
        sector = info.get("sector", "N/A")

        lines = [
            f"📈 {name} ({ticker.upper()})",
            f"ราคาปัจจุบัน: {price:,.2f} {currency}",
            f"Sector: {sector}",
        ]
        if market_cap:
            cap_b = market_cap / 1e9
            lines.append(f"Market Cap: {cap_b:,.2f}B {currency}")
        if pe_ratio:
            lines.append(f"P/E Ratio: {pe_ratio:.2f}x")
        if pb_ratio:
            lines.append(f"P/BV Ratio: {pb_ratio:.2f}x")
        if eps:
            lines.append(f"EPS: {eps:.2f} {currency}")
        if div_yield:
            if div_yield > 1:
                div_pct = div_yield
            else:
                div_pct = div_yield * 100
            lines.append(f"Dividend Yield: {div_pct:.2f}%")
        if week_high and week_low:
            lines.append(f"52-week: {week_low:,.2f} - {week_high:,.2f} {currency}")

        return "\n".join(lines)

    except Exception as e:
        return f"ดึงข้อมูลหุ้น '{ticker}' ไม่สำเร็จ: {e}"
