"""
Flask Backend สำหรับ Stock Chatbot UI
รัน: python app.py
"""
import os
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="%H:%M:%S")

app = Flask(__name__)
CORS(app)

# Import agent (lazy load เพื่อให้ server start เร็ว)
agent = None

def get_agent():
    global agent
    if agent is None:
        from agent import StockAgent
        agent = StockAgent()
    return agent

# ─── HTML Template ───────────────────────────────────────────────
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Assistant — AI ผู้ช่วยด้านการลงทุน</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --gold: #C9A84C;
            --gold-light: #E8D48B;
            --gold-dark: #8B6914;
            --bg-primary: #0A0A0F;
            --bg-secondary: #12121A;
            --bg-card: #1A1A25;
            --text-primary: #F5F0E8;
            --text-secondary: #9A9A9A;
            --border: rgba(201,168,76,0.15);
            --glass: rgba(26,26,37,0.85);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Sarabun', 'Noto Sans Thai', sans-serif;
            background: radial-gradient(ellipse at top, #1a1520 0%, var(--bg-primary) 50%, #050508 100%);
            color: var(--text-primary);
            height: 100vh; display: flex; flex-direction: column;
            overflow: hidden;
        }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(201,168,76,0.2); border-radius: 10px; }

        /* Ambient glow */
        .ambient { position: fixed; top: -200px; left: 50%; transform: translateX(-50%);
            width: 600px; height: 600px; border-radius: 50%;
            background: radial-gradient(circle, rgba(201,168,76,0.03) 0%, transparent 70%);
            pointer-events: none; z-index: 0; }

        /* Header */
        header {
            padding: 16px 24px; background: var(--glass);
            backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
            display: flex; align-items: center; gap: 14; z-index: 10;
        }
        .header-logo {
            width: 42px; height: 42px; border-radius: 12px;
            background: linear-gradient(135deg, var(--gold-dark), var(--gold));
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; box-shadow: 0 0 20px rgba(201,168,76,0.2);
        }
        .header-title { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; }
        .header-title span { color: var(--gold); }
        .header-sub { font-size: 11.5px; color: var(--text-secondary); letter-spacing: 0.3px; }
        .status-badge {
            margin-left: auto; padding: 4px 12px; border-radius: 20px;
            background: rgba(201,168,76,0.08); border: 1px solid rgba(201,168,76,0.2);
            font-size: 11px; color: var(--gold); font-weight: 500;
        }

        /* Chat */
        .chat-area { flex: 1; overflow-y: auto; padding: 24px 20px; display: flex; flex-direction: column; gap: 16; }

        /* Welcome */
        .welcome { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 28; animation: fadeIn 0.8s ease; }
        .welcome-logo {
            width: 80px; height: 80px; border-radius: 24px;
            background: linear-gradient(135deg, var(--gold-dark), var(--gold), var(--gold-light));
            display: flex; align-items: center; justify-content: center;
            font-size: 40px; box-shadow: 0 0 40px rgba(201,168,76,0.15);
            animation: float 3s ease-in-out infinite;
        }
        .welcome h2 { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; }
        .welcome h2 span { color: var(--gold); }
        .welcome p { font-size: 14px; color: var(--text-secondary); line-height: 1.8; text-align: center; }
        .divider { width: 60px; height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }

        .examples { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; max-width: 520px; width: 100%; padding: 0 12px; }
        .example-btn {
            padding: 12px 16px; border-radius: 14px; background: var(--bg-card);
            border: 1px solid var(--border); color: var(--text-primary);
            font-size: 12.5px; line-height: 1.5; cursor: pointer; text-align: left;
            transition: all 0.3s ease; font-family: 'Sarabun', sans-serif;
            display: flex; align-items: flex-start; gap: 8;
        }
        .example-btn:hover {
            border-color: rgba(201,168,76,0.35); background: rgba(201,168,76,0.04);
            transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .example-btn .arrow { color: var(--gold); font-size: 14px; flex-shrink: 0; }

        /* Messages */
        .msg { display: flex; gap: 12; max-width: 85%; animation: slideUp 0.4s cubic-bezier(0.16,1,0.3,1); }
        .msg-user { align-self: flex-end; flex-direction: row-reverse; }
        .msg-bot { align-self: flex-start; }
        .msg-avatar {
            width: 30px; height: 30px; border-radius: 50%;
            background: linear-gradient(135deg, var(--gold-dark), var(--gold));
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; flex-shrink: 0; box-shadow: 0 0 12px rgba(201,168,76,0.3);
        }
        .msg-bubble {
            padding: 14px 20px; font-size: 14.5px; line-height: 1.7;
            white-space: pre-wrap; word-break: break-word;
        }
        .msg-user .msg-bubble {
            border-radius: 20px 20px 4px 20px;
            background: linear-gradient(135deg, rgba(139,105,20,0.53), rgba(201,168,76,0.27));
            border: 1px solid rgba(201,168,76,0.27); box-shadow: 0 4px 20px rgba(201,168,76,0.15);
        }
        .msg-bot .msg-bubble {
            border-radius: 20px 20px 20px 4px;
            background: var(--bg-card); border: 1px solid var(--border);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        /* Typing */
        .typing-dots { display: flex; gap: 6; padding: 8px 0; }
        .typing-dots span {
            width: 8px; height: 8px; border-radius: 50%; background: var(--gold);
            animation: pulse 1.4s ease-in-out infinite;
        }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        .typing-hint { font-size: 11px; color: var(--text-secondary); margin-top: 4px; }

        /* Input */
        .input-area {
            padding: 16px 20px 20px; background: var(--glass);
            backdrop-filter: blur(20px); border-top: 1px solid var(--border);
        }
        .input-wrap {
            display: flex; gap: 10; align-items: flex-end;
            background: var(--bg-secondary); border-radius: 18px;
            border: 1px solid var(--border); padding: 4px 4px 4px 18px;
            transition: border 0.3s ease;
        }
        .input-wrap:focus-within { border-color: rgba(201,168,76,0.4); }
        .input-wrap textarea {
            flex: 1; background: transparent; border: none; color: var(--text-primary);
            font-size: 14.5px; padding: 12px 0; resize: none;
            font-family: 'Sarabun', sans-serif; line-height: 1.5;
            max-height: 120px; overflow-y: auto; outline: none;
        }
        .input-wrap textarea::placeholder { color: var(--text-secondary); }
        .send-btn {
            width: 44px; height: 44px; border-radius: 14px; border: none;
            background: linear-gradient(135deg, var(--gold-dark), var(--gold));
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            font-size: 18px; transition: all 0.3s ease; flex-shrink: 0;
            box-shadow: 0 0 16px rgba(201,168,76,0.2);
        }
        .send-btn:disabled { background: rgba(201,168,76,0.13); cursor: not-allowed; box-shadow: none; }
        .send-btn:not(:disabled):hover { box-shadow: 0 0 24px rgba(201,168,76,0.4); }
        .disclaimer { text-align: center; font-size: 10.5px; color: rgba(154,154,154,0.5); margin-top: 10px; }

        @keyframes slideUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
        @keyframes pulse { 0%,80%,100% { opacity:0.2; transform:scale(0.8); } 40% { opacity:1; transform:scale(1.2); } }

        @media (max-width: 600px) {
            .examples { grid-template-columns: 1fr; }
            .msg { max-width: 95%; }
            .welcome h2 { font-size: 22px; }
        }
    </style>
</head>
<body>
    <div class="ambient"></div>

    <header>
        <div class="header-logo">📊</div>
        <div>
            <div class="header-title"><span>Stock</span> Assistant</div>
            <div class="header-sub">Powered by Typhoon AI • ReAct Agent</div>
        </div>
        <div class="status-badge">🟢 Online</div>
    </header>

    <div class="chat-area" id="chatArea">
        <div class="welcome" id="welcome">
            <div class="welcome-logo">📈</div>
            <div>
                <h2><span>Stock</span> Investment Assistant</h2>
                <p>ผู้ช่วยด้านการลงทุน ครอบคลุมหุ้นไทยและหุ้น US<br>วิเคราะห์ • เปรียบเทียบ • คำนวณ • ข่าวสาร</p>
            </div>
            <div class="divider"></div>
            <div class="examples">
                <button class="example-btn" onclick="sendExample(this)">
                    <span class="arrow">→</span>มีเงิน 5,000 บาท อยากลงทุนหุ้น ซื้อตัวไหนดี?
                </button>
                <button class="example-btn" onclick="sendExample(this)">
                    <span class="arrow">→</span>เปรียบเทียบ PTT กับ AAPL
                </button>
                <button class="example-btn" onclick="sendExample(this)">
                    <span class="arrow">→</span>P/E ratio คืออะไร?
                </button>
                <button class="example-btn" onclick="sendExample(this)">
                    <span class="arrow">→</span>ราคาหุ้น NVDA ตอนนี้เท่าไหร่?
                </button>
                <button class="example-btn" onclick="sendExample(this)">
                    <span class="arrow">→</span>ข่าวหุ้น GULF ล่าสุด
                </button>
                <button class="example-btn" onclick="sendExample(this)">
                    <span class="arrow">→</span>คำนวณ P/E ถ้าราคา 50 EPS 5
                </button>
            </div>
        </div>
    </div>

    <div class="input-area">
        <div class="input-wrap">
            <textarea id="userInput" rows="1" placeholder="ถามเกี่ยวกับหุ้นไทยหรือหุ้น US..." onkeydown="handleKey(event)"></textarea>
            <button class="send-btn" id="sendBtn" onclick="sendMessage()">➤</button>
        </div>
        <div class="disclaimer">ข้อมูลนี้ไม่ใช่คำแนะนำการลงทุน ควรศึกษาข้อมูลเพิ่มเติมก่อนตัดสินใจ</div>
    </div>

    <script>
        const chatArea = document.getElementById('chatArea');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const welcome = document.getElementById('welcome');
        let isLoading = false;

        function sendExample(btn) {
            const text = btn.textContent.replace('→', '').trim();
            userInput.value = text;
            sendMessage();
        }

        function handleKey(e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        }

        function addMessage(role, content) {
            const div = document.createElement('div');
            div.className = `msg msg-${role}`;
            div.innerHTML = `
                <div class="msg-avatar">${role === 'user' ? '👤' : '📈'}</div>
                <div class="msg-bubble">${content.replace(/\\n/g, '<br>')}</div>
            `;
            chatArea.appendChild(div);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function showTyping() {
            const div = document.createElement('div');
            div.className = 'msg msg-bot';
            div.id = 'typing';
            div.innerHTML = `
                <div class="msg-avatar">📈</div>
                <div class="msg-bubble">
                    <div class="typing-dots"><span></span><span></span><span></span></div>
                    <div class="typing-hint">กำลังวิเคราะห์...</div>
                </div>
            `;
            chatArea.appendChild(div);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function removeTyping() {
            const el = document.getElementById('typing');
            if (el) el.remove();
        }

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text || isLoading) return;

            welcome.style.display = 'none';
            isLoading = true;
            sendBtn.disabled = true;
            userInput.value = '';

            addMessage('user', text);
            showTyping();

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: text }),
                });
                const data = await res.json();
                removeTyping();
                addMessage('bot', data.answer || 'ขออภัย เกิดข้อผิดพลาด');
            } catch (err) {
                removeTyping();
                addMessage('bot', '⚠️ ไม่สามารถเชื่อมต่อ server ได้ กรุณาลองใหม่อีกครั้ง');
            }

            isLoading = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    </script>
</body>
</html>
"""


# ─── API Routes ──────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"answer": "กรุณาพิมพ์คำถาม"}), 400

    try:
        stock_agent = get_agent()
        answer = stock_agent.run(query)
        return jsonify({"answer": answer})
    except Exception as e:
        logging.exception("Error in chat endpoint")
        return jsonify({"answer": f"เกิดข้อผิดพลาด: {str(e)}"}), 500


# ─── Run Server ──────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"""
╔══════════════════════════════════════════════╗
║   📊 Stock Assistant — Chatbot UI            ║
║   🌐 http://localhost:{port}                   ║
║   ⏹  กด Ctrl+C เพื่อหยุด server              ║
╚══════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=True)