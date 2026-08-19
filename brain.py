"""
=============================================================
  SELF-LEARNING CHATBOT — BRAIN / LEARNING ENGINE
=============================================================
  Project Title : NeuraBot - Self-Learning AI Chatbot
  Created By    : arik
  Description   : Core intelligence engine. Uses pattern
                  matching, similarity scoring, and a
                  self-growing knowledge base stored in
                  SQLite. No external API or library needed.
=============================================================
"""

import sqlite3
import json
import re
import random
import difflib
import string
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot_memory.db")

# ─────────────────────────────────────────────────────────
#  DATABASE — persistent memory
# ─────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern  TEXT NOT NULL,
            response TEXT NOT NULL,
            hits     INTEGER DEFAULT 0,
            added_on TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            role      TEXT,
            message   TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
    _seed_defaults()

def _seed_defaults():
    """Pre-load starter knowledge so the bot works right away."""
    defaults = [
        ("hello|hi|hey|good morning|good evening|greetings",
         "Hey there! I'm NeuraBot 🤖 — I learn from every chat. What's on your mind?|Hello! Nice to meet you. Teach me something new today!|Hi! I'm always learning. Ask me anything!"),
        ("how are you|how r u|how are u|how do you do",
         "I'm running great, thanks for asking! Every conversation makes me smarter. 😊|I'm doing wonderful! I've been learning a lot lately. How about you?"),
        ("what is your name|who are you|what are you",
         "I'm NeuraBot — a self-learning chatbot created by arik. I grow smarter with every conversation!|My name is NeuraBot. I was built by arik as a project that learns on its own without any API."),
        ("who made you|who created you|who built you|who is your creator",
         "I was created by arik as a personal project. Pretty cool, right?|arik brought me to life! A developer who wanted to see how far pattern-matching could go without any APIs."),
        ("what can you do|your features|help|what do you know",
         "I can chat, learn new things you teach me, remember past conversations, and get smarter over time! Try asking me something or teach me by saying: 'learn: question | answer'"),
        ("bye|goodbye|see you|take care|exit",
         "Goodbye! It was great chatting with you. I'll remember everything we talked about! 👋|See you next time! I'll keep learning while you're away. Bye! 😊"),
        ("thank you|thanks|thank u|thx",
         "You're very welcome! 😊 Happy to help anytime.|Glad I could help! That's what I'm here for."),
        ("what is python|tell me about python",
         "Python is a powerful, beginner-friendly programming language. It's used for web development, AI, data science, and much more! I myself am built entirely in Python 🐍"),
        ("what is ai|what is artificial intelligence",
         "Artificial Intelligence (AI) is the simulation of human intelligence in machines. I'm a small example of AI — I learn and respond like a human would!"),
        ("what time is it|current time|what's the time",
         "TIME_NOW"),
        ("what is today|today's date|current date|what day is it",
         "DATE_NOW"),
        ("tell me a joke|say a joke|joke",
         "Why do programmers prefer dark mode? Because light attracts bugs! 🐛😄|Why did the computer go to the doctor? Because it had a virus! 💻|I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads. 😂"),
        ("what is machine learning|tell me about machine learning",
         "Machine Learning is a branch of AI where computers learn from data without being explicitly programmed. I use a simple form of ML — pattern matching and memory — to learn from you!"),
        ("how do you learn|how are you learning",
         "Great question! I learn by storing patterns from our conversations in my memory database. Every time you correct me or teach me something new, I update my knowledge. No internet needed!"),
        ("motivate me|give me motivation|inspire me",
         "You are capable of amazing things! Every expert was once a beginner. Keep going! 💪|The only way to do great work is to love what you do. — Steve Jobs 🌟|Believe in yourself. You've survived 100% of your bad days so far. That's a perfect record! 🔥"),
        ("what is your purpose|why do you exist|why were you made",
         "I exist to prove that AI doesn't need the internet or paid APIs to be smart. I learn purely from conversations — built entirely by arik using Python!"),
    ]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM knowledge")
    count = c.fetchone()[0]
    if count == 0:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for pattern, response in defaults:
            c.execute("INSERT INTO knowledge (pattern, response, hits, added_on) VALUES (?,?,0,?)",
                      (pattern, response, now))
        conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────
#  TEXT UTILITIES
# ─────────────────────────────────────────────────────────

def clean(text: str) -> str:
    text = text.lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def tokenize(text: str):
    return re.findall(r'\b\w+\b', clean(text))

def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, clean(a), clean(b)).ratio()

def keyword_score(user_tokens: list, pattern: str) -> float:
    """Score how well user input matches a pattern string."""
    parts = [p.strip() for p in pattern.split("|")]
    best = 0.0
    user_set = set(user_tokens)
    for part in parts:
        part_tokens = set(tokenize(part))
        if not part_tokens:
            continue
        overlap = len(user_set & part_tokens) / len(part_tokens)
        seq = similarity(" ".join(user_tokens), part)
        score = (overlap * 0.6) + (seq * 0.4)
        if score > best:
            best = score
    return best

# ─────────────────────────────────────────────────────────
#  KNOWLEDGE BASE OPERATIONS
# ─────────────────────────────────────────────────────────

def teach(pattern: str, response: str) -> str:
    """Add new knowledge to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO knowledge (pattern, response, hits, added_on) VALUES (?,?,0,?)",
              (clean(pattern), response, now))
    conn.commit()
    conn.close()
    return f"✅ Got it! I've learned: '{pattern}' → '{response}'"

def get_all_knowledge():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, pattern, response, hits, added_on FROM knowledge ORDER BY hits DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_knowledge(kid: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM knowledge WHERE id=?", (kid,))
    conn.commit()
    conn.close()

def increment_hits(kid: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE knowledge SET hits = hits + 1 WHERE id=?", (kid,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────
#  CHAT LOG
# ─────────────────────────────────────────────────────────

def save_log(role: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO chat_log (role, message, timestamp) VALUES (?,?,?)", (role, message, now))
    conn.commit()
    conn.close()

def get_chat_log(limit=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, message, timestamp FROM chat_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

# ─────────────────────────────────────────────────────────
#  MAIN RESPONSE ENGINE
# ─────────────────────────────────────────────────────────

TEACH_PATTERN = re.compile(r'^(learn|teach|remember|add)[:\-]\s*(.+?)\s*[|]\s*(.+)$', re.IGNORECASE)
UNKNOWN_RESPONSES = [
    "Hmm, I haven't learned about that yet. You can teach me! Type: learn: your question | your answer",
    "I don't know about that yet 🤔 But I'm always ready to learn! Use: learn: topic | explanation",
    "That's new to me! Teach me by typing: learn: [question] | [answer]",
    "I'm still learning about this. Could you teach me? Format: learn: question | answer",
    "Interesting! I don't have that in my memory yet. Add it with: learn: question | answer 📚",
]

def get_response(user_input: str) -> str:
    """Core response function — matches input to best known pattern."""

    # Check for teach command
    m = TEACH_PATTERN.match(user_input.strip())
    if m:
        pattern = m.group(2).strip()
        response = m.group(3).strip()
        return teach(pattern, response)

    # Special dynamic responses
    if re.search(r'\btime\b', user_input.lower()):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"🕒 The current time is {now}"
    if re.search(r'\bdate\b|\btoday\b', user_input.lower()):
        now = datetime.datetime.now().strftime("%A, %d %B %Y")
        return f"📅 Today is {now}"

    tokens = tokenize(user_input)
    if not tokens:
        return random.choice(UNKNOWN_RESPONSES)

    # Score all knowledge entries
    rows = get_all_knowledge()
    best_score = 0.0
    best_row = None
    for row in rows:
        kid, pattern, response, hits, added_on = row
        score = keyword_score(tokens, pattern)
        if score > best_score:
            best_score = score
            best_row = row

    THRESHOLD = 0.35
    if best_row and best_score >= THRESHOLD:
        kid, pattern, response, hits, added_on = best_row
        increment_hits(kid)
        # Handle special tokens
        if response == "TIME_NOW":
            return f"🕒 The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
        if response == "DATE_NOW":
            return f"📅 Today is {datetime.datetime.now().strftime('%A, %d %B %Y')}"
        options = [r.strip() for r in response.split("|")]
        return random.choice(options)

    return random.choice(UNKNOWN_RESPONSES)
