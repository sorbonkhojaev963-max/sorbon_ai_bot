# ============================================================
# SORBON AI CLEAN - 20-MODULE TELEGRAM BOT + MULTI-API + SQLITE
# Created by SORBON KHOJAEV
# Powered by Groq + Gemini + OpenRouter + Tavily
# Code & Comments: 100% ENGLISH | Replies: AUTO-LANGUAGE
# ============================================================

import ast
import datetime
import hashlib
import json
import os
import random
import re
import secrets
import sqlite3
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from groq import Groq
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

# ============ ENVIRONMENT CONFIGURATION ============
# Set these values in your hosting/runtime environment variables before running.
TOKEN = os.environ.get("BOT_TOKEN", "").strip()
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "").strip()
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free").strip()
DB_PATH = os.environ.get("SORBON_DB_PATH", "sorbon_ai.db").strip()

OWNER = "SORBON KHOJAEV"
BOT_NAME = "SORBON AI"

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# ============ 20 CORE MODULES ============
MODULES_20: List[Dict[str, str]] = [
    {"id": "1", "code": "ai_brain", "name": "AI Brain", "desc": "Chat, Q&A, conversation memory"},
    {"id": "2", "code": "languages", "name": "Languages", "desc": "Translation, auto language detection, 100+ languages"},
    {"id": "3", "code": "trading_markets", "name": "Trading & Markets", "desc": "Crypto, Forex, Gold, Stocks market analysis"},
    {"id": "4", "code": "technical_analysis", "name": "Technical Analysis", "desc": "RSI, MACD, EMA, Fibonacci, Support/Resistance"},
    {"id": "5", "code": "market_charts", "name": "Market Charts", "desc": "Chart structure, candlesticks & bullish/bearish scenarios"},
    {"id": "6", "code": "image_generator", "name": "Image Generator", "desc": "Prompts & concepts for images, logos, avatars, posters"},
    {"id": "7", "code": "image_editor", "name": "Image Editor", "desc": "Editing steps, background cleanup & visual styling"},
    {"id": "8", "code": "video_creator", "name": "Video Creator", "desc": "Scripts, subtitles, hooks & video ideas"},
    {"id": "9", "code": "voice_ai", "name": "Voice AI", "desc": "Voice scripts, speech text & voice assistant flows"},
    {"id": "10", "code": "programming", "name": "Programming", "desc": "Python, JavaScript, C++, Java & more"},
    {"id": "11", "code": "bot_builder", "name": "Bot Builder", "desc": "Building new Telegram bots & handlers"},
    {"id": "12", "code": "website_builder", "name": "Website Builder", "desc": "Building websites & web applications"},
    {"id": "13", "code": "web_search", "name": "Web Search", "desc": "Researching topics, market news & fact checks"},
    {"id": "14", "code": "study_assistant", "name": "Study Assistant", "desc": "Math, physics, chemistry, history & exam prep"},
    {"id": "15", "code": "writing_studio", "name": "Writing Studio", "desc": "Essays, articles, stories, ads & copywriting"},
    {"id": "16", "code": "pdf_documents", "name": "PDF & Documents", "desc": "Reading, summarizing & drafting PDF/Word content"},
    {"id": "17", "code": "smart_tools", "name": "Smart Tools", "desc": "Calculator, converters, password & hash generators"},
    {"id": "18", "code": "games_fun", "name": "Games & Fun", "desc": "Trivia, riddles, word & interactive games"},
    {"id": "19", "code": "cybersecurity", "name": "Cybersecurity", "desc": "Computer safety, threat defense & data protection"},
    {"id": "20", "code": "ai_management", "name": "AI Management", "desc": "Profile, settings, memory & bot control"},
]

SYSTEM_PROMPT = """You are SORBON AI, an intelligent, versatile, and helpful AI assistant created by SORBON KHOJAEV.
Core Rules:
1. Automatically detect the language of the user's message (Tajik, Russian, English, Turkish, Arabic, Persian, Uzbek, Spanish, German, French, Chinese, Japanese, Korean, Hindi, etc.).
2. ALWAYS reply in the EXACT SAME language that the user wrote in, unless explicitly asked to translate or respond in another language.
3. Support all 20 modules clearly and practically: AI Brain, Languages, Trading & Markets, Technical Analysis, Market Charts, Image Generator, Image Editor, Video Creator, Voice AI, Programming, Bot Builder, Website Builder, Web Search, Study Assistant, Writing Studio, PDF & Documents, Smart Tools, Games & Fun, Cybersecurity, and AI Management.
4. For Trading, Technical Analysis, Market Charts, Risk/Reward, and Paper Trading:
   - Analyze market context, explain charts/candlesticks, evaluate RSI, MACD, EMA, Fibonacci, and Support/Resistance, and present bullish and bearish scenarios.
   - Always note that market analysis does not guarantee profit and the bot never executes real trades without permission.
"""

JOKES_POOL = [
    "Why did the computer go to the doctor? Because it had a virus! 😂",
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛😂",
    "Why did the math book look sad? Because it had too many problems! 📚😂",
    "Why did the trader watch the candle for 2 hours? Waiting for confirmation! 📈😂",
]

RIDDLES_POOL = [
    {"q": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", "a": "An echo"},
    {"q": "The more you take away from me, the bigger I get. What am I?", "a": "A hole"},
    {"q": "What has keys that open no locks, space but no room, and you can enter but not go outside?", "a": "A keyboard"},
]

# ============ SQLITE DATABASE ============
def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            messages INTEGER NOT NULL DEFAULT 0,
            active_module TEXT NOT NULL DEFAULT 'ai_brain',
            joined TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            user_id INTEGER PRIMARY KEY,
            balance_usd REAL NOT NULL DEFAULT 10000.0,
            realized_pnl REAL NOT NULL DEFAULT 0.0,
            positions_json TEXT NOT NULL DEFAULT '[]'
        )
    """)
    conn.commit()
    conn.close()

def ensure_user(user_id: int, first_name: Optional[str] = None) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, messages, active_module, joined FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    today = str(datetime.date.today())
    if not row:
        uname = first_name or "User"
        cur.execute(
            "INSERT INTO users (user_id, name, messages, active_module, joined) VALUES (?, ?, 0, 'ai_brain', ?)",
            (user_id, uname, today),
        )
        conn.commit()
        row = (user_id, uname, 0, "ai_brain", today)
    elif first_name and first_name != row[1]:
        cur.execute("UPDATE users SET name = ? WHERE user_id = ?", (first_name, user_id))
        conn.commit()
        row = (row[0], first_name, row[2], row[3], row[4])
    conn.close()
    return {
        "user_id": row[0],
        "name": row[1],
        "messages": row[2],
        "active_module": row[3],
        "joined": row[4],
    }

def increment_messages(user_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET messages = messages + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def set_user_module(user_id: int, module_code: str) -> None:
    ensure_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET active_module = ? WHERE user_id = ?", (module_code, user_id))
    conn.commit()
    conn.close()

def append_chat_message(user_id: int, role: str, content: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.execute("""
        DELETE FROM chat_history
        WHERE user_id = ? AND id NOT IN (
            SELECT id FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT 20
        )
    """, (user_id, user_id))
    conn.commit()
    conn.close()

def load_chat_history(user_id: int, limit: int = 10) -> List[Dict[str, str]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    rows.reverse()
    return [{"role": r[0], "content": r[1]} for r in rows]

def clear_chat_history(user_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.execute("UPDATE users SET active_module = 'ai_brain' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_wallet(user_id: int) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT balance_usd, realized_pnl, positions_json FROM wallets WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        cur.execute(
            "INSERT INTO wallets (user_id, balance_usd, realized_pnl, positions_json) VALUES (?, 10000.0, 0.0, '[]')",
            (user_id,),
        )
        conn.commit()
        row = (10000.0, 0.0, "[]")
    conn.close()
    return {
        "balance_usd": float(row[0]),
        "realized_pnl": float(row[1]),
        "positions": json.loads(row[2] or "[]"),
    }

def save_user_wallet(user_id: int, wallet: Dict[str, Any]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE wallets SET balance_usd = ?, realized_pnl = ?, positions_json = ? WHERE user_id = ?",
        (
            float(wallet["balance_usd"]),
            float(wallet["realized_pnl"]),
            json.dumps(wallet["positions"]),
            user_id,
        ),
    )
    conn.commit()
    conn.close()

# ============ TRADING & UTILITY HELPERS ============
def calc_ema(prices: List[float], period: int) -> Optional[float]:
    if len(prices) < period or period <= 0:
        return None
    k = 2.0 / (period + 1.0)
    ema = sum(prices[:period]) / period
    for p in prices[period:]:
        ema = (p * k) + (ema * (1.0 - k))
    return ema

def calc_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    if len(prices) < period + 1:
        return None
    gains: List[float] = []
    losses: List[float] = []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def calc_macd_approx(prices: List[float]) -> Optional[Dict[str, float]]:
    if len(prices) < 26:
        return None
    ema12 = calc_ema(prices, 12)
    ema26 = calc_ema(prices, 26)
    if ema12 is None or ema26 is None:
        return None
    macd_val = ema12 - ema26
    signal_val = macd_val * 0.85
    return {"macd": macd_val, "signal": signal_val, "hist": macd_val - signal_val}

def calc_fibonacci(low_p: float, high_p: float) -> Dict[str, float]:
    span = high_p - low_p
    return {
        "0.0% (High)": high_p,
        "23.6%": high_p - (span * 0.236),
        "38.2%": high_p - (span * 0.382),
        "50.0%": high_p - (span * 0.500),
        "61.8%": high_p - (span * 0.618),
        "78.6%": high_p - (span * 0.786),
        "100.0% (Low)": low_p,
    }

def calc_rr(entry: float, sl: float, tp: float) -> Dict[str, float]:
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    if risk == 0:
        raise ValueError("Stop loss cannot equal entry price.")
    return {"risk": risk, "reward": reward, "ratio": reward / risk}

def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp):
        val = _eval_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +val
        if isinstance(node.op, ast.USub):
            return -val
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("Division by zero.")
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            if right == 0:
                raise ZeroDivisionError("Floor division by zero.")
            return left // right
        if isinstance(node.op, ast.Mod):
            if right == 0:
                raise ZeroDivisionError("Modulo by zero.")
            return left % right
        if isinstance(node.op, ast.Pow):
            if abs(right) > 1000:
                raise ValueError("Exponent too large.")
            return left ** right
    raise ValueError("Unsupported operation.")

def safe_calculator(expression: str) -> float:
    allowed = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        ast.UAdd, ast.USub,
    )
    tree = ast.parse(expression, mode="eval")
    for n in ast.walk(tree):
        if not isinstance(n, allowed):
            raise ValueError("Only basic math operators are allowed.")
    return _eval_node(tree.body)

def generate_password(length: int = 16) -> str:
    safe_len = max(8, min(64, length))
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(safe_len))

def convert_temp(val: float, unit: str) -> str:
    u = unit.strip().upper()
    if u == "C":
        return f"{val:.2f}°C | {(val * 9 / 5) + 32:.2f}°F | {val + 273.15:.2f}K"
    if u == "F":
        c = (val - 32) * 5 / 9
        return f"{val:.2f}°F | {c:.2f}°C | {c + 273.15:.2f}K"
    if u == "K":
        c = val - 273.15
        return f"{val:.2f}K | {c:.2f}°C | {(c * 9 / 5) + 32:.2f}°F"
    raise ValueError("Unit must be C, F, or K.")

def compute_hashes(text: str) -> Dict[str, str]:
    data = text.encode("utf-8")
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }

def detect_script_hint(text: str) -> str:
    if re.search(r"[\u0600-\u06FF]", text):
        return "arabic_persian"
    if re.search(r"[\u0400-\u04FF]", text):
        return "cyrillic"
    if re.search(r"[\u4e00-\u9fff]", text):
        return "cjk"
    if re.search(r"[a-zA-Z]", text):
        return "latin"
    return "general"

# ============ EXTERNAL AI & SEARCH PROVIDERS ============
def _call_gemini(prompt: str, system_instruction: str) -> Optional[str]:
    if not GEMINI_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": prompt}]}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates") or []
            if candidates:
                parts = candidates[0].get("content", {}).get("parts") or []
                if parts:
                    return parts[0].get("text", "")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[GEMINI ERROR] {exc}")
    return None

def _call_openrouter(messages: List[Dict[str, str]]) -> Optional[str]:
    if not OPENROUTER_KEY:
        return None
    payload = json.dumps({
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.75,
        "max_tokens": 1800,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me/sorbon_ai_bot",
            "X-Title": BOT_NAME,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            choices = body.get("choices") or []
            if choices:
                return choices[0].get("message", {}).get("content", "")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[OPENROUTER ERROR] {exc}")
    return None

def search_web_tavily(query: str, max_results: int = 4) -> Optional[str]:
    if not TAVILY_KEY:
        return None
    payload = {
        "api_key": TAVILY_KEY,
        "query": query,
        "max_results": max_results,
        "include_answer": True,
    }
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            lines: List[str] = []
            if data.get("answer"):
                lines.append(f"Summary: {data['answer']}\n")
            for idx, item in enumerate(data.get("results") or [], start=1):
                title = item.get("title", "Result")
                link = item.get("url", "")
                snippet = (item.get("content") or "")[:240].strip()
                lines.append(f"{idx}. {title}\n{snippet}\n{link}")
            return "\n\n".join(lines) if lines else "No web results found."
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[TAVILY ERROR] {exc}")
        return None

async def ask_sorbon(user_id: int, prompt: str, module_code: str) -> str:
    mod_meta = next((m for m in MODULES_20 if m["code"] == module_code), MODULES_20[0])
    hint = detect_script_hint(prompt)
    sys_msg = (
        f"{SYSTEM_PROMPT}\n"
        f"Active Module: #{mod_meta['id']} {mod_meta['name']} ({mod_meta['desc']}).\n"
        f"Detected script hint: {hint}. Always reply in the exact language of the user's message."
    )
    messages: List[Dict[str, str]] = [{"role": "system", "content": sys_msg}]
    messages.extend(load_chat_history(user_id, limit=10))
    messages.append({"role": "user", "content": prompt})

    reply: Optional[str] = None

    if groq_client:
        try:
            res = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.75,
                max_tokens=1800,
                top_p=0.9,
            )
            reply = res.choices[0].message.content
        except Exception as exc:
            print(f"[GROQ ERROR] {exc}")

    if not reply and GEMINI_KEY:
        reply = _call_gemini(prompt, sys_msg)

    if not reply and OPENROUTER_KEY:
        reply = _call_openrouter(messages)

    if not reply:
        return "Temporary AI connection issue. Please try again in a few seconds."

    append_chat_message(user_id, "user", prompt)
    append_chat_message(user_id, "assistant", reply)
    return reply

async def send_split(update: Update, text: str, parse_mode: Optional[str] = None) -> None:
    if not update.message:
        return
    if len(text) <= 4000:
        await update.message.reply_text(text, parse_mode=parse_mode)
        return
    for i in range(0, len(text), 4000):
        await update.message.reply_text(text[i : i + 4000])

# ============ KEYBOARDS ============
def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("🧠 AI Brain", callback_data="mod_ai_brain"),
            InlineKeyboardButton("🌐 Languages", callback_data="mod_languages"),
        ],
        [
            InlineKeyboardButton("📊 Trading & TA", callback_data="mod_technical_analysis"),
            InlineKeyboardButton("💻 Code & Bots", callback_data="mod_programming"),
        ],
        [
            InlineKeyboardButton("🎨 Image & Video", callback_data="mod_image_generator"),
            InlineKeyboardButton("📚 Study & Docs", callback_data="mod_study_assistant"),
        ],
        [
            InlineKeyboardButton("🧩 All 20 Modules", callback_data="show_20_modules"),
            InlineKeyboardButton("🧰 Smart Tools", callback_data="show_tools"),
        ],
        [
            InlineKeyboardButton("💼 Paper Wallet", callback_data="show_wallet"),
            InlineKeyboardButton("👤 Profile", callback_data="show_profile"),
        ],
    ]
    return InlineKeyboardMarkup(rows)

def tools_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("🔐 Password", callback_data="act_pass"),
            InlineKeyboardButton("🪙 Coin Flip", callback_data="act_coin"),
        ],
        [
            InlineKeyboardButton("🎲 Dice Roll", callback_data="act_dice"),
            InlineKeyboardButton("🧩 Riddle", callback_data="act_riddle"),
        ],
        [
            InlineKeyboardButton("😂 Joke", callback_data="act_joke"),
            InlineKeyboardButton("⬅️ Main Menu", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)

# ============ COMMAND HANDLERS ============
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    u = update.effective_user
    prof = ensure_user(u.id, u.first_name)
    set_user_module(u.id, "ai_brain")
    msg = (
        f"Hello *{prof['name']}*!\n\n"
        f"Welcome to *{BOT_NAME}* — created by *{OWNER}*.\n"
        "Core Modules: *20* | Persistence: *SQLite Enabled*\n\n"
        "• *Auto-Language:* Detects your language and replies in that exact language.\n"
        "• *Trading & Analytics:* RSI, MACD, EMA, Fibonacci, Risk/Reward & Paper Trading.\n"
        "• *All 20 Modules:* Chat, languages, markets, TA, charts, image/video, voice, code, bots, web, search, study, writing, docs, tools, games, cybersecurity & management.\n\n"
        "Send any message or pick a button below:"
    )
    await update.message.reply_text(msg, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def cmd_modules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = [f"🧩 *{BOT_NAME} — 20 Modules*\n"]
    for m in MODULES_20:
        lines.append(f"*{m['id']}.* *{m['name']}* (`{m['code']}`) — {m['desc']}")
    lines.append("\nSwitch module: `/module <1-20 or code>` (example: `/module 4`)")
    await send_split(update, "\n".join(lines), parse_mode=ParseMode.MARKDOWN)

async def cmd_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: `/module <1-20 or code>`", parse_mode=ParseMode.MARKDOWN)
        return
    key = context.args[0].strip().lower()
    found = next((m for m in MODULES_20 if m["id"] == key or m["code"] == key), None)
    if not found:
        await update.message.reply_text("Unknown module. Use `/modules` to list all 20.")
        return
    set_user_module(update.effective_user.id, found["code"])
    await update.message.reply_text(
        f"✅ Active module: *#{found['id']} {found['name']}*\n{found['desc']}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip() if context.args else ""
    if not query:
        await update.message.reply_text("🔎 Usage: `/search latest market news`", parse_mode=ParseMode.MARKDOWN)
        return
    result = search_web_tavily(query)
    if not result:
        await update.message.reply_text("TAVILY_API_KEY is not configured or search failed.")
        return
    await send_split(update, result)

async def cmd_ta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args)
    try:
        prices = [float(x.strip()) for x in raw.split(",") if x.strip()]
        if len(prices) < 5:
            await update.message.reply_text("📈 Usage: `/ta 100, 101.2, 102.5, 101.8, 103.4, 104.1, 105.0`", parse_mode=ParseMode.MARKDOWN)
            return
        rsi_p = min(14, len(prices) - 1)
        ema_p = min(14, len(prices))
        rsi_val = calc_rsi(prices, rsi_p)
        ema_val = calc_ema(prices, ema_p)
        macd_info = calc_macd_approx(prices)
        last_p = prices[-1]
        sup = min(prices[-5:])
        res_lvl = max(prices[-5:])
        rsi_tag = "Overbought (>70)" if (rsi_val and rsi_val > 70) else ("Oversold (<30)" if (rsi_val and rsi_val < 30) else "Neutral")
        bias = "Bullish scenario above EMA" if (ema_val and last_p >= ema_val) else "Bearish scenario below EMA"
        macd_txt = f"`{macd_info['macd']:.4f}`" if macd_info else "_Need 26+ prices_"

        msg = (
            f"📊 *Technical Analysis Snapshot*\n"
            f"• Last Price: `{last_p}`\n"
            f"• RSI ({rsi_p}): `{rsi_val:.2f}` ({rsi_tag})\n"
            f"• EMA ({ema_p}): `{ema_val:.2f}`\n"
            f"• MACD Line: {macd_txt}\n"
            f"• Support / Resistance: `{sup}` / `{res_lvl}`\n"
            f"• Scenario Bias: *{bias}*\n\n"
            "_Analysis does not guarantee profit; bot never executes real trades without permission._"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        await update.message.reply_text(f"TA error: {exc}")

async def cmd_rr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        await update.message.reply_text("⚖️ Usage: `/rr <entry> <stop_loss> <take_profit>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        entry = float(context.args[0])
        sl = float(context.args[1])
        tp = float(context.args[2])
        rr = calc_rr(entry, sl, tp)
        await update.message.reply_text(
            f"⚖️ *Risk / Reward*\n• Entry: `{entry}` | SL: `{sl}` | TP: `{tp}`\n• Risk: `{rr['risk']:.4f}` | Reward: `{rr['reward']:.4f}`\n• Ratio: *1 : {rr['ratio']:.2f}*",
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as exc:
        await update.message.reply_text(f"R:R error: {exc}")

async def cmd_levels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("📐 Usage: `/levels <swing_low> <swing_high>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        low_p = float(context.args[0])
        high_p = float(context.args[1])
        if high_p <= low_p:
            raise ValueError("High price must be greater than low price.")
        fibs = calc_fibonacci(low_p, high_p)
        lines = ["📐 *Fibonacci Retracement Levels*\n"] + [f"• {k}: `{v:.4f}`" for k, v in fibs.items()]
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        await update.message.reply_text(f"Fibonacci error: {exc}")

async def cmd_paperbuy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        await update.message.reply_text("🧪 Usage: `/paperbuy BTC 1000 90000`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        sym = context.args[0].upper()
        usd = float(context.args[1])
        price = float(context.args[2])
        if usd <= 0 or price <= 0:
            raise ValueError("USD and price must be positive.")
        wallet = get_user_wallet(update.effective_user.id)
        if usd > wallet["balance_usd"]:
            await update.message.reply_text(f"Insufficient paper balance: ${wallet['balance_usd']:.2f}")
            return
        qty = usd / price
        wallet["balance_usd"] -= usd
        wallet["positions"].append({"symbol": sym, "qty": qty, "entry": price, "usd": usd})
        save_user_wallet(update.effective_user.id, wallet)
        await update.message.reply_text(
            f"✅ *Paper Buy Opened*\n• Symbol: *{sym}* | Qty: `{qty:.6f}` @ `${price:.2f}`\n• Cash Left: `${wallet['balance_usd']:.2f}`",
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as exc:
        await update.message.reply_text(f"Paper buy error: {exc}")

async def cmd_papersell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("📉 Usage: `/papersell BTC 92500`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        sym = context.args[0].upper()
        exit_price = float(context.args[1])
        if exit_price <= 0:
            raise ValueError("Exit price must be positive.")
        wallet = get_user_wallet(update.effective_user.id)
        idx = next((i for i, p in enumerate(wallet["positions"]) if p["symbol"] == sym), None)
        if idx is None:
            await update.message.reply_text(f"No open paper position for *{sym}*.", parse_mode=ParseMode.MARKDOWN)
            return
        pos = wallet["positions"].pop(idx)
        proceeds = pos["qty"] * exit_price
        pnl = proceeds - pos["usd"]
        wallet["balance_usd"] += proceeds
        wallet["realized_pnl"] += pnl
        save_user_wallet(update.effective_user.id, wallet)
        await update.message.reply_text(
            f"🧾 *Paper Position Closed ({sym})*\n"
            f"• Entry: `${pos['entry']:.2f}` -> Exit: `${exit_price:.2f}`\n"
            f"• Trade P&L: `${pnl:+.2f}`\n"
            f"• Cash: `${wallet['balance_usd']:.2f}` | Total Realized P&L: `${wallet['realized_pnl']:+.2f}`",
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as exc:
        await update.message.reply_text(f"Paper sell error: {exc}")

async def cmd_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    w = get_user_wallet(update.effective_user.id)
    pos_lines = "\n".join(
        f"• {p['symbol']}: `{p['qty']:.6f}` @ `${p['entry']:.2f}` (${p['usd']:.2f})"
        for p in w["positions"]
    ) or "• No open positions."
    await update.message.reply_text(
        f"💼 *Paper Trading Wallet*\n• Cash: *${w['balance_usd']:.2f}*\n• Realized P&L: *${w['realized_pnl']:+.2f}*\n• Positions:\n{pos_lines}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    expr = " ".join(context.args).strip()
    if not expr:
        await update.message.reply_text("🧮 Usage: `/calc (50 + 25) * 2`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        await update.message.reply_text(f"🧮 `{expr}` = *{safe_calculator(expr)}*", parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        await update.message.reply_text(f"Calc error: {exc}")

async def cmd_temp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("🌡️ Usage: `/temp 25 C`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        await update.message.reply_text(f"🌡️ {convert_temp(float(context.args[0]), context.args[1])}")
    except Exception as exc:
        await update.message.reply_text(f"Temp error: {exc}")

async def cmd_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    length = int(context.args[0]) if (context.args and context.args[0].isdigit()) else 16
    await update.message.reply_text(f"🔐 `{generate_password(length)}`", parse_mode=ParseMode.MARKDOWN)

async def cmd_hash(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args).strip()
    if not raw:
        await update.message.reply_text("🔑 Usage: `/hash <text>`", parse_mode=ParseMode.MARKDOWN)
        return
    h = compute_hashes(raw)
    await update.message.reply_text(f"🔑 MD5: `{h['md5']}`\nSHA-256: `{h['sha256']}`", parse_mode=ParseMode.MARKDOWN)

async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    u = update.effective_user
    p = ensure_user(u.id, u.first_name)
    await update.message.reply_text(
        f"👤 *Profile*\n• ID: `{u.id}`\n• Name: {p['name']}\n• Messages: {p['messages']}\n• Module: `{p['active_module']}`\n• Joined: {p['joined']}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    clear_chat_history(update.effective_user.id)
    await update.message.reply_text("🗑️ Chat memory cleared and module reset to AI Brain.")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = (
        f"📋 *{BOT_NAME} Commands*\n\n"
        "/start - Main menu\n"
        "/modules - List all 20 modules\n"
        "/module <1-20|code> - Switch module\n"
        "/search <query> - Web search via Tavily\n"
        "/ta <p1,p2,...> - RSI, EMA, MACD & S/R\n"
        "/rr <entry> <sl> <tp> - Risk/Reward ratio\n"
        "/levels <low> <high> - Fibonacci levels\n"
        "/paperbuy <SYM> <USD> <PRICE> - Paper buy\n"
        "/papersell <SYM> <PRICE> - Paper sell & P&L\n"
        "/wallet - Paper portfolio\n"
        "/calc <expr> - Safe calculator\n"
        "/temp <val> <C|F|K> - Temperature converter\n"
        "/password [len] - Password generator\n"
        "/hash <text> - MD5 & SHA-256\n"
        "/profile - User profile\n"
        "/clear - Reset chat memory"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# ============ CALLBACK ROUTER ============
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    ensure_user(uid, q.from_user.first_name)
    data = q.data or ""

    if data == "back_main":
        await q.edit_message_text(f"*{BOT_NAME}* Main Menu:", reply_markup=main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data.startswith("mod_"):
        code = data.replace("mod_", "")
        set_user_module(uid, code)
        m = next((item for item in MODULES_20 if item["code"] == code), MODULES_20[0])
        await q.edit_message_text(
            f"✅ Active Module: *#{m['id']} {m['name']}*\n{m['desc']}",
            reply_markup=main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif data == "show_20_modules":
        txt = "\n".join(f"{m['id']}. *{m['name']}* (`{m['code']}`)" for m in MODULES_20)
        await q.edit_message_text(f"🧩 *20 Modules:*\n\n{txt}", reply_markup=main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "show_tools":
        await q.edit_message_text("🧰 *Smart Tools & Fun:*", reply_markup=tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "show_wallet":
        w = get_user_wallet(uid)
        await q.edit_message_text(
            f"💼 *Paper Wallet*\n• Balance: *${w['balance_usd']:.2f}*\n• Realized P&L: *${w['realized_pnl']:+.2f}*\n• Positions: *{len(w['positions'])}*",
            reply_markup=main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif data == "show_profile":
        p = ensure_user(uid)
        await q.edit_message_text(
            f"👤 *Profile*\n• Name: {p['name']}\n• Messages: {p['messages']}\n• Module: `{p['active_module']}`",
            reply_markup=main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif data == "act_pass":
        await q.edit_message_text(f"🔐 `{generate_password(16)}`", reply_markup=tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "act_coin":
        await q.edit_message_text(f"🪙 *{random.choice(['Heads', 'Tails'])}*", reply_markup=tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "act_dice":
        await q.edit_message_text(f"🎲 *{random.randint(1, 6)}*", reply_markup=tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "act_joke":
        await q.edit_message_text(random.choice(JOKES_POOL), reply_markup=tools_keyboard())
    elif data == "act_riddle":
        r = random.choice(RIDDLES_POOL)
        await q.edit_message_text(f"🧩 {r['q']}\n\nAnswer: {r['a']}", reply_markup=tools_keyboard())

# ============ MESSAGE & DOCUMENT HANDLERS ============
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    u = update.effective_user
    prof = ensure_user(u.id, u.first_name)
    increment_messages(u.id)
    ans = await ask_sorbon(u.id, update.message.text.strip(), prof["active_module"])
    await send_split(update, ans)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.document:
        return
    u = update.effective_user
    ensure_user(u.id, u.first_name)
    increment_messages(u.id)
    doc = update.message.document
    instruction = update.message.caption or "Summarize and analyze this document."

    if doc.file_size and doc.file_size > 200_000:
        await update.message.reply_text("File exceeds 200 KB limit for direct text preview.")
        return

    try:
        tg_file = await doc.get_file()
        raw_bytes = await tg_file.download_as_bytearray()
        content = raw_bytes.decode("utf-8", errors="ignore").strip()
        if not content:
            await update.message.reply_text("No plain text extracted. Try `.txt`, `.md`, `.csv`, `.json`, or `.py`.")
            return
        prompt = f"File: {doc.file_name}\nTask: {instruction}\n\nText:\n{content[:8000]}"
        ans = await ask_sorbon(u.id, prompt, "pdf_documents")
        await send_split(update, ans)
    except Exception as exc:
        print(f"[DOC ERROR] {exc}")
        await update.message.reply_text("Failed to process document.")

# ============ RUNNER ============
def create_app() -> Application:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing.")
    if not GROQ_KEY and not GEMINI_KEY and not OPENROUTER_KEY:
        raise RuntimeError("At least one AI API key (GROQ_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY) is required.")

    init_db()

    # Use generous timeouts to prevent startup TimedOut errors on cloud hosting
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )
    get_updates_request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .get_updates_request(get_updates_request)
        .build()
    )

    handlers = [
        ("start", cmd_start),
        ("help", cmd_help),
        ("modules", cmd_modules),
        ("module", cmd_module),
        ("search", cmd_search),
        ("ta", cmd_ta),
        ("rr", cmd_rr),
        ("levels", cmd_levels),
        ("paperbuy", cmd_paperbuy),
        ("papersell", cmd_papersell),
        ("wallet", cmd_wallet),
        ("calc", cmd_calc),
        ("temp", cmd_temp),
        ("password", cmd_password),
        ("hash", cmd_hash),
        ("profile", cmd_profile),
        ("clear", cmd_clear),
    ]
    for name, fn in handlers:
        app.add_handler(CommandHandler(name, fn))

    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app

if __name__ == "__main__":
    bot_app = create_app()
    print(f"{BOT_NAME} CLEAN (20 Modules + Multi-API + SQLite) is running...")
    bot_app.run_polling(drop_pending_updates=True)
