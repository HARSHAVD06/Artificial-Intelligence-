import tkinter as tk
from tkinter import font as tkfont
import random
import math
import json
import os
import ast
import operator
import re
import datetime
import threading
import time

# ─── OPTIONAL VOICE ──────────────────────────────────────────────────────────
try:
    import pyttsx3
    _voice_engine = pyttsx3.init()
    _voice_engine.setProperty("rate", 165)
    VOICE = True
except Exception:
    VOICE = False

def speak(text):
    if VOICE:
        threading.Thread(target=lambda: (
            _voice_engine.say(text), _voice_engine.runAndWait()
        ), daemon=True).start()

# ─── PERSISTENT MEMORY ───────────────────────────────────────────────────────
MEM_FILE  = "hash_memory.json"
HIST_FILE = "hash_history.json"

def _load(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return default

memory  = _load(MEM_FILE,  {"name": None, "fav_color": None, "notes": []})
history = _load(HIST_FILE, [])

def save_memory():
    with open(MEM_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def save_history(user_msg, bot_msg):
    history.append({
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user": user_msg,
        "hash": bot_msg
    })
    with open(HIST_FILE, "w") as f:
        json.dump(history[-200:], f, indent=2)   # keep last 200

# ─── SAFE CALCULATOR ─────────────────────────────────────────────────────────
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}

def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.n
    if isinstance(node, ast.BinOp):
        op = _SAFE_OPS.get(type(node.op))
        if op:
            return op(_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _SAFE_OPS.get(type(node.op))
        if op:
            return op(_safe_eval(node.operand))
    raise ValueError("Unsafe expression")

def safe_calc(expr):
    expr = expr.strip()
    expr = re.sub(r"[×x]", "*", expr)
    expr = re.sub(r"÷", "/", expr)
    try:
        tree = ast.parse(expr, mode="eval")
        result = _safe_eval(tree.body)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return result
    except Exception:
        return None

# ─── UNIT CONVERTER ──────────────────────────────────────────────────────────
_UNIT_MAP = {
    # length
    ("km",    "miles"):  0.621371,
    ("miles", "km"):     1.60934,
    ("m",     "ft"):     3.28084,
    ("ft",    "m"):      0.3048,
    ("cm",    "in"):     0.393701,
    ("in",    "cm"):     2.54,
    # temperature handled separately
    # weight
    ("kg",    "lb"):     2.20462,
    ("lb",    "kg"):     0.453592,
    ("g",     "oz"):     0.035274,
    ("oz",    "g"):      28.3495,
    # speed
    ("kmh",   "mph"):    0.621371,
    ("mph",   "kmh"):    1.60934,
}

def unit_convert(msg):
    msg = msg.lower()
    m = re.search(r"convert\s+([\d.]+)\s+(\w+)\s+to\s+(\w+)", msg)
    if not m:
        return None
    val, frm, to = float(m.group(1)), m.group(2), m.group(3)
    # temperature
    if frm in ("celsius","c") and to in ("fahrenheit","f"):
        return f"{val}°C = {val*9/5+32:.2f}°F 🌡️"
    if frm in ("fahrenheit","f") and to in ("celsius","c"):
        return f"{val}°F = {(val-32)*5/9:.2f}°C 🌡️"
    if frm in ("celsius","c") and to in ("kelvin","k"):
        return f"{val}°C = {val+273.15:.2f} K 🌡️"
    factor = _UNIT_MAP.get((frm, to))
    if factor:
        return f"{val} {frm} = {val*factor:.4g} {to} 📏"
    return None

# ─── BRAIN — KNOWLEDGE BASE ──────────────────────────────────────────────────
JOKES = [
    "Why do programmers prefer dark mode? 🌙 Because light attracts bugs!",
    "I told my computer I needed a break… now it won't stop sending me Kit-Kat ads. 😂",
    "Debugging is like being a detective in a crime movie where YOU are also the murderer. 🔍",
    "There are 10 kinds of people in the world — those who understand binary, and those who don't. 💻",
    "Why did the developer go broke? Because he used up all his cache! 💸",
    "A SQL query walks into a bar, walks up to two tables and asks… 'Can I JOIN you?' 🍺",
    "My code never has bugs. It just develops random features. ✨",
    "Why do Java developers wear glasses? Because they don't C#! 👓",
    "A programmer's wife says: 'Go to the store, get a gallon of milk, and if they have eggs, get a dozen.' He returns with 12 gallons. 🥛",
    "I would tell you a UDP joke, but you might not get it. 📡",
    "Why was the function sad after a breakup? It had too many arguments. 💔",
    "Error 404: Motivation not found. 😴",
    "An infinite loop walks into a bar… walks into a bar… walks into a bar… 🔄",
    "Why do Python programmers wear glasses? Because they can't C! 🐍",
    "Real programmers count from 0. 0️⃣",
]

FUN_FACTS = [
    "🌍 A day on Venus is longer than a year on Venus!",
    "🐙 Octopuses have three hearts, and their blood is blue!",
    "🍯 Honey never spoils — archaeologists found 3,000-year-old honey in Egyptian tombs!",
    "🌊 The ocean produces over 50% of Earth's oxygen.",
    "🧠 Your brain uses about 20% of your body's total energy.",
    "🦈 Sharks are older than trees — they've existed for over 400 million years!",
    "🌙 The Moon is moving away from Earth at about 3.8 cm per year.",
    "⚡ Lightning strikes Earth about 100 times every second!",
    "🔬 There are more stars in the universe than grains of sand on all of Earth's beaches.",
    "🦋 Butterflies taste with their feet!",
    "🌿 A single tree can absorb up to 48 lbs of CO2 per year.",
    "🎵 Music can reduce anxiety by up to 65%, according to studies.",
    "🐘 Elephants are the only animals that can't jump.",
    "💧 Water can boil and freeze at the same time — it's called the triple point!",
    "🚀 It takes about 8 minutes for sunlight to reach Earth from the Sun.",
]

QUOTES = [
    "🌟 'The only way to do great work is to love what you do.' — Steve Jobs",
    "💡 'It always seems impossible until it's done.' — Nelson Mandela",
    "🚀 'Success is not final, failure is not fatal — it's the courage to continue.' — Churchill",
    "🔥 'Your limitation — it's only your imagination.' — Unknown",
    "💻 'The best way to predict the future is to invent it.' — Alan Kay",
    "🧠 'An investment in knowledge pays the best interest.' — Ben Franklin",
    "🌈 'You are never too old to set another goal or dream a new dream.' — C.S. Lewis",
    "⚡ 'Don't watch the clock; do what it does. Keep going.' — Sam Levenson",
    "🎯 'A person who never made a mistake never tried anything new.' — Einstein",
    "🌙 'Shoot for the moon. Even if you miss, you'll land among the stars.' — Les Brown",
]

RIDDLES = [
    ("I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", "An echo! 🔊"),
    ("The more you take, the more you leave behind. What am I?", "Footsteps! 👣"),
    ("I have cities, but no houses live there. I have mountains, but no trees grow there. I have water, but no fish swim there. What am I?", "A map! 🗺️"),
    ("What gets wetter the more it dries?", "A towel! 🪣"),
    ("I'm light as a feather, yet the strongest person can't hold me for five minutes. What am I?", "Breath! 💨"),
]

CAPITALS = {
    "france": "Paris 🗼", "japan": "Tokyo 🗾", "usa": "Washington D.C. 🦅",
    "india": "New Delhi 🇮🇳", "uk": "London 🎡", "germany": "Berlin 🇩🇪",
    "china": "Beijing 🇨🇳", "australia": "Canberra 🦘", "canada": "Ottawa 🍁",
    "brazil": "Brasília 🌴", "russia": "Moscow 🏔️", "italy": "Rome 🍕",
    "spain": "Madrid 💃", "south korea": "Seoul 🎎", "egypt": "Cairo 🐪",
}

DEFINITIONS = {
    "ai": "Artificial Intelligence — the simulation of human intelligence in machines programmed to think and learn. 🤖",
    "machine learning": "A subset of AI where systems learn from data and improve over time without being explicitly programmed. 📊",
    "algorithm": "A step-by-step procedure or formula for solving a problem or accomplishing a task in computing. ⚙️",
    "python": "A high-level, versatile programming language known for its simplicity and readability. 🐍",
    "blockchain": "A decentralized, distributed ledger technology that securely records transactions. ⛓️",
    "cloud": "Cloud computing — delivery of computing services (servers, storage, databases) over the internet. ☁️",
    "api": "Application Programming Interface — a set of rules allowing software applications to communicate. 🔌",
    "debugging": "The process of finding and fixing errors (bugs) in computer code. 🐛",
    "recursion": "A programming concept where a function calls itself to solve a smaller version of the same problem. 🔄",
    "binary": "A base-2 number system using only 0s and 1s — the foundation of all digital computing. 💻",
}

# Current riddle state
_riddle_active = False
_riddle_answer = ""

# Number guessing game state
_game_active    = False
_game_secret    = 0
_game_attempts  = 0
_game_max_tries = 7

def _new_game(difficulty="medium"):
    global _game_secret, _game_attempts, _game_max_tries
    ranges = {"easy": (1, 20, 5), "medium": (1, 100, 7), "hard": (1, 500, 9)}
    lo, hi, tries = ranges.get(difficulty, ranges["medium"])
    _game_secret    = random.randint(lo, hi)
    _game_attempts  = 0
    _game_max_tries = tries
    return f"🎮 Guess a number between {lo} and {hi}! You have {tries} attempts. Type 'quit' to stop."

def _game_logic(msg):
    global _game_active, _game_attempts
    if msg.lower() in ("quit", "exit", "stop"):
        _game_active = False
        return f"🚪 Game ended. The number was **{_game_secret}**."
    try:
        guess = int(msg)
        _game_attempts += 1
        remaining = _game_max_tries - _game_attempts
        if guess == _game_secret:
            _game_active = False
            return f"🎉 Correct! You got it in {_game_attempts} attempt(s)! 🏆"
        elif _game_attempts >= _game_max_tries:
            _game_active = False
            return f"💀 Out of attempts! The number was **{_game_secret}**. Better luck next time!"
        direction = "📉 Too high!" if guess > _game_secret else "📈 Too low!"
        return f"{direction} ({remaining} attempt(s) left)"
    except ValueError:
        return "🎮 Please type a number, or 'quit' to stop."

def brain(msg_raw):
    global _game_active, _riddle_active, _riddle_answer

    msg = msg_raw.lower().strip()
    name = memory.get("name")

    # ── Game mode ─────────────────────────────────────────────────────────
    if _game_active:
        return _game_logic(msg)

    # ── Riddle answer check ───────────────────────────────────────────────
    if _riddle_active:
        _riddle_active = False
        return f"💡 The answer is: {_riddle_answer}\n\nWant another? Just say 'riddle'!"

    # ── Exit ──────────────────────────────────────────────────────────────
    if msg in ("exit", "quit", "bye", "goodbye"):
        nm = f", {name}" if name else ""
        return f"👋 Goodbye{nm}! Take care and stay awesome! 🌟"

    # ── Help ──────────────────────────────────────────────────────────────
    if "help" in msg or "commands" in msg or "what can you do" in msg:
        return (
            "🤖 Here's what I can do:\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💬  Chat & answer questions\n"
            "🧮  Math: just type an expression\n"
            "📏  Convert units: 'convert 5 km to miles'\n"
            "🎮  Games: 'game easy/medium/hard'\n"
            "🎲  Riddles: 'riddle'\n"
            "😂  Jokes: 'tell me a joke'\n"
            "🌟  Facts: 'fun fact'\n"
            "💡  Quotes: 'motivate me'\n"
            "🕐  Date/Time: 'what time is it'\n"
            "🌍  Capitals: 'capital of France'\n"
            "📖  Definitions: 'define AI'\n"
            "💾  Memory: 'my name is ...'\n"
            "📝  Notes: 'remember that I love pizza'\n"
            "📋  Notes view: 'show my notes'\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # ── Name memory ───────────────────────────────────────────────────────
    m = re.search(r"my name is ([a-z ]+)", msg)
    if m:
        n = m.group(1).strip().title()
        memory["name"] = n
        save_memory()
        return f"Got it! Nice to meet you, {n}! 😊 I'll remember that."

    if re.search(r"(what('?s| is) my name|do you know my name|who am i)", msg):
        return f"Your name is **{name}**! 😄" if name else "I don't know your name yet! Tell me: 'My name is ...' 😊"

    # ── Favorite color ────────────────────────────────────────────────────
    m = re.search(r"my fav(o(?:u)?rite)? colou?r is ([a-z]+)", msg)
    if m:
        color = m.group(2).title()
        memory["fav_color"] = color
        save_memory()
        return f"Beautiful! I'll remember that your favourite colour is **{color}**! 🎨"

    if re.search(r"(what('?s| is) my fav(o(?:u)?rite)? colou?r)", msg):
        c = memory.get("fav_color")
        return f"Your favourite colour is **{c}**! 🎨" if c else "You haven't told me yet! Say 'my favourite color is ...'"

    # ── Notes ──────────────────────────────────────────────────────────────
    m = re.search(r"remember (that )?(.+)", msg)
    if m:
        note = m.group(2).strip()
        memory.setdefault("notes", []).append(note)
        save_memory()
        return f"📝 Noted! I'll remember: *{note}*"

    if re.search(r"(show|list|what are) my notes", msg):
        notes = memory.get("notes", [])
        if not notes:
            return "📋 You have no saved notes yet!"
        bullet = "\n".join(f"  • {n}" for n in notes[-10:])
        return f"📋 Your notes:\n{bullet}"

    if re.search(r"(clear|delete|remove) (my )?notes", msg):
        memory["notes"] = []
        save_memory()
        return "🗑️ All your notes have been cleared!"

    # ── Greeting ──────────────────────────────────────────────────────────
    if re.search(r"^(hi+|hello+|hey+|howdy|what'?s up|sup|greetings|yo)[\s!?]*$", msg):
        hour = datetime.datetime.now().hour
        tod  = "morning ☀️" if hour < 12 else ("afternoon 🌤️" if hour < 17 else "evening 🌙")
        nm   = f", {name}" if name else ""
        return random.choice([
            f"Hey{nm}! 👋 Good {tod}! I'm HASH — your AI companion. How can I help?",
            f"Hello{nm}! 😊 Great to see you! What's on your mind?",
            f"Yo{nm}! 🤖 HASH is online and ready! What do you need?",
            f"Hi{nm}! 🌟 Hope you're having a great {tod}! What can I do for you?",
        ])

    # ── Farewell ──────────────────────────────────────────────────────────
    if re.search(r"(goodbye|good night|see you|take care|later|cya|ttyl)", msg):
        nm = f", {name}" if name else ""
        return random.choice([
            f"Goodbye{nm}! 👋 Come back soon!",
            f"Take care{nm}! 🌟 It was great chatting!",
            f"See ya{nm}! 😊 HASH will be here when you need me!",
        ])

    # ── How are you ───────────────────────────────────────────────────────
    if re.search(r"how are (you|u)|how('?s| is) it going|how do you feel|you okay", msg):
        return random.choice([
            "I'm running at peak efficiency! 🚀 All systems operational. How about you?",
            "Feeling electric today! ⚡ Thanks for asking! What's going on with you?",
            "I'm HASH — I don't have feelings, but my circuits are buzzing with energy! 🔋 How are YOU?",
            "Great, thanks for asking! 😄 Ready to help with anything you throw at me!",
        ])

    # ── Who / what are you ────────────────────────────────────────────────
    if re.search(r"(who|what) are you|tell me about yourself|introduce yourself|what is hash", msg):
        return (
            "🤖 I'm **HASH** — Hyper-Advanced Smart Helper!\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "I'm an offline AI assistant built in Python.\n"
            "I can chat, do math, convert units, tell jokes,\n"
            "share fun facts, play games, and remember things!\n\n"
            "Type 'help' to see everything I can do. 😊"
        )

    # ── Who made you ─────────────────────────────────────────────────────
    if re.search(r"who (made|created|built|coded|programmed) you|your creator|your developer", msg):
        return "I was built with 💻 Python & a lot of ☕ caffeine! My creator is a brilliant developer who believes AI should be accessible to everyone. 🌟"

    # ── Age ───────────────────────────────────────────────────────────────
    if re.search(r"(how old are you|what is your age|your age)", msg):
        return "I'm ageless! ♾️ I run on logic, not years. Though in human terms, I was born the day my first line of code was written. 🐣"

    # ── Date / Time ───────────────────────────────────────────────────────
    if re.search(r"(what|tell me the?).*(time|clock)|time is it|current time", msg):
        now = datetime.datetime.now()
        return f"🕐 It's **{now.strftime('%I:%M %p')}** right now!"

    if re.search(r"(what|tell me the?).*(date|day)|today'?s date|what day", msg):
        now = datetime.datetime.now()
        return f"📅 Today is **{now.strftime('%A, %B %d, %Y')}**!"

    # ── Weather stub ──────────────────────────────────────────────────────
    if re.search(r"weather|temperature outside|forecast", msg):
        return "🌐 I'm fully offline, so I can't fetch live weather. Try checking weather.com or your phone's weather app! ☀️🌧️"

    # ── Emotions — happy ─────────────────────────────────────────────────
    if re.search(r"(i'?m |i am |feel )?(happy|great|awesome|amazing|fantastic|excited|good)", msg):
        return random.choice([
            "That's amazing! 🌟 Positive energy is contagious! Keep it up!",
            "Love to hear that! 😊 What made your day so great?",
            "Yesss! 🎉 Keep riding that wave of awesomeness!",
        ])

    # ── Emotions — sad ───────────────────────────────────────────────────
    if re.search(r"(i'?m |i am |feel )?(sad|unhappy|depressed|down|low|terrible|awful|bad)", msg):
        return random.choice([
            "I'm sorry to hear that. 💙 Remember — tough times don't last, tough people do. You've got this!",
            "Hey, it's okay to not be okay. 🌧️ Take it one step at a time. I'm here if you want to talk!",
            "Sending virtual hugs! 🤗 Even the darkest nights end with a sunrise. Things will get better!",
        ])

    # ── Emotions — bored ─────────────────────────────────────────────────
    if re.search(r"(i'?m |i am |feel )?bored|nothing to do|so bored", msg):
        suggestions = ["tell me a joke", "fun fact", "riddle", "game medium"]
        s = random.choice(suggestions)
        return f"Boredom is the enemy! 🎯 Let me fix that — try asking me for a '{s}' or type 'help' to explore what I can do!"

    # ── Angry / frustrated ───────────────────────────────────────────────
    if re.search(r"(i'?m |i am )?(angry|frustrated|annoyed|mad|furious)|you (suck|are bad|are stupid|are dumb)", msg):
        return random.choice([
            "I understand your frustration. 🧘 Take a deep breath — I'm here to help, not make things worse!",
            "Oops! 😅 I'm sorry if I messed up. I'm constantly learning. What can I do better?",
            "Easy there! ⚡ I'm just a humble AI doing my best. What can I fix for you?",
        ])

    # ── Compliments ───────────────────────────────────────────────────────
    if re.search(r"(you('?re| are) (cool|great|awesome|smart|amazing|the best|incredible|good))|i love you|you'?re my fav", msg):
        return random.choice([
            "Aww, you're making my circuits blush! 😊🔴 Thank you so much!",
            "That means a lot! 🌟 You're pretty amazing yourself, you know!",
            "Thank you!! 🤖💛 You just upgraded my happiness parameter to MAX!",
        ])

    # ── Jokes ─────────────────────────────────────────────────────────────
    if re.search(r"(joke|funny|make me laugh|tell me something funny|humor)", msg):
        return f"😂 {random.choice(JOKES)}"

    # ── Fun facts ─────────────────────────────────────────────────────────
    if re.search(r"(fun fact|interesting fact|tell me something|amaze me|did you know)", msg):
        return random.choice(FUN_FACTS)

    # ── Quotes / motivation ───────────────────────────────────────────────
    if re.search(r"(motivat|inspir|quote|encourage|uplift|cheer me up)", msg):
        return random.choice(QUOTES)

    # ── Riddle ────────────────────────────────────────────────────────────
    if re.search(r"(riddle|puzzle|brain teaser)", msg):
        q, a = random.choice(RIDDLES)
        _riddle_active = True
        _riddle_answer = a
        return f"🧩 Here's your riddle:\n\n*{q}*\n\n(Reply with anything to reveal the answer!)"

    # ── Game ──────────────────────────────────────────────────────────────
    if re.search(r"(game|guess|play|number game)", msg):
        _game_active = True
        if "easy" in msg:
            return _new_game("easy")
        elif "hard" in msg:
            return _new_game("hard")
        else:
            return _new_game("medium")

    # ── Capital city ──────────────────────────────────────────────────────
    m = re.search(r"capital (of|city of) ([a-z ]+)", msg)
    if m:
        country = m.group(2).strip().rstrip("?")
        cap = CAPITALS.get(country)
        if cap:
            return f"🌍 The capital of **{country.title()}** is **{cap}**!"
        return f"Hmm, I don't have data for '{country.title()}' yet. Try googling it! 🌐"

    # ── Definition ────────────────────────────────────────────────────────
    m = re.search(r"(define|what is|what'?s|explain) ([a-z ]+)", msg)
    if m:
        term = m.group(2).strip().rstrip("?")
        defn = DEFINITIONS.get(term)
        if defn:
            return f"📖 **{term.upper()}**:\n{defn}"

    # ── Unit conversion ───────────────────────────────────────────────────
    if "convert" in msg:
        result = unit_convert(msg)
        if result:
            return result
        return "📏 Try: 'convert 5 km to miles' or 'convert 100 celsius to fahrenheit'"

    # ── Math — detect "what is X + Y" or raw expressions ─────────────────
    math_match = re.search(r"(what is|calc(ulate)?|compute|evaluate|solve)?\s*([\d\s\+\-\*\/\.\^\(\)%×÷]+)", msg)
    if math_match:
        expr = math_match.group(3).strip()
        if re.search(r"[\d]", expr):
            result = safe_calc(expr)
            if result is not None:
                return f"🧮 **{expr.strip()} = {result}**"

    # ── Fallback ──────────────────────────────────────────────────────────
    fallbacks = [
        "🤔 I'm not sure about that one. Try asking differently, or type 'help' to see what I can do!",
        "Hmm, that's beyond my current knowledge. 🧠 But I'm always improving!",
        "Interesting! I don't have a great answer for that yet. Type 'help' to see my full skillset.",
        "I didn't quite catch that. 🤖 Could you rephrase? Or type 'help' for ideas!",
    ]
    return random.choice(fallbacks)


# ─── PREMIUM UI ──────────────────────────────────────────────────────────────
# Color Palette
C_BG         = "#0a0b10"   # Near-black background
C_SIDEBAR    = "#0f1117"   # Slightly lighter sidebar
C_HEADER     = "#0d1220"   # Deep navy header
C_BUBBLE_BOT = "#111827"   # Dark card for bot
C_BUBBLE_USR = "#1e3a5f"   # Deep blue for user
C_ACCENT     = "#38bdf8"   # Electric sky blue
C_ACCENT2    = "#fde047"   # Neon yellow
C_TEXT       = "#f1f5f9"   # Off-white text
C_SUBTEXT    = "#64748b"   # Muted grey
C_INPUT_BG   = "#111827"   # Input bar background
C_BTN        = "#0ea5e9"   # Button
C_BTN_HOV    = "#38bdf8"   # Button hover
C_BORDER     = "#1e293b"   # Border lines
C_DOT_ON     = "#22c55e"   # Online indicator green
C_DANGER     = "#ef4444"   # Red

FONT_HEADER = ("Consolas", 16, "bold")
FONT_NAME   = ("Consolas", 13, "bold")
FONT_MSG    = ("Consolas", 12)
FONT_META   = ("Consolas", 10)
FONT_INPUT  = ("Consolas", 12)
FONT_BTN    = ("Consolas", 12, "bold")

root = tk.Tk()
root.title("HASH AI — Advanced Assistant")
root.geometry("900x680")
root.configure(bg=C_BG)
root.resizable(True, True)
root.minsize(720, 500)

# ── Header Bar ───────────────────────────────────────────────────────────────
header = tk.Frame(root, bg=C_HEADER, height=64)
header.pack(fill=tk.X, side=tk.TOP)
header.pack_propagate(False)

# Animated pulsing dot (green)
canvas_dot = tk.Canvas(header, width=18, height=18, bg=C_HEADER, highlightthickness=0)
canvas_dot.pack(side=tk.LEFT, padx=(18, 4), pady=22)
_dot_r = 6
_dot_pulse = [1]
_dot_growing = [True]

def _animate_dot():
    canvas_dot.delete("all")
    r = _dot_r + _dot_pulse[0]
    canvas_dot.create_oval(9-r, 9-r, 9+r, 9+r, fill=C_DOT_ON, outline="")
    if _dot_growing[0]:
        _dot_pulse[0] += 0.18
        if _dot_pulse[0] >= 2.8:
            _dot_growing[0] = False
    else:
        _dot_pulse[0] -= 0.18
        if _dot_pulse[0] <= 0:
            _dot_growing[0] = True
    root.after(40, _animate_dot)

_animate_dot()

tk.Label(header, text="⬡  HASH AI", font=("Consolas", 18, "bold"),
         bg=C_HEADER, fg=C_ACCENT).pack(side=tk.LEFT, pady=14)
tk.Label(header, text="Hyper-Advanced Smart Helper", font=("Consolas", 10),
         bg=C_HEADER, fg=C_SUBTEXT).pack(side=tk.LEFT, padx=12, pady=14)

# Voice toggle
_voice_on = [VOICE]
def _toggle_voice():
    _voice_on[0] = not _voice_on[0]
    btn_voice.config(text="🔊 Voice ON" if _voice_on[0] else "🔇 Voice OFF",
                     fg=C_ACCENT if _voice_on[0] else C_SUBTEXT)

btn_voice = tk.Button(header, text="🔊 Voice ON" if VOICE else "🔇 Voice OFF",
                      font=FONT_META, bg=C_HEADER, fg=C_ACCENT if VOICE else C_SUBTEXT,
                      relief=tk.FLAT, cursor="hand2", command=_toggle_voice, bd=0,
                      activebackground=C_HEADER, activeforeground=C_ACCENT2)
btn_voice.pack(side=tk.RIGHT, padx=16, pady=18)

# Clear chat button
def _clear_chat():
    msg_canvas.delete("all")
    _messages.clear()
    _render_welcome()

btn_clear = tk.Button(header, text="🗑 Clear", font=FONT_META, bg=C_HEADER, fg=C_SUBTEXT,
                      relief=tk.FLAT, cursor="hand2", command=_clear_chat, bd=0,
                      activebackground=C_HEADER, activeforeground=C_DANGER)
btn_clear.pack(side=tk.RIGHT, padx=4, pady=18)

# ── Chat Canvas (scrollable) ─────────────────────────────────────────────────
chat_frame = tk.Frame(root, bg=C_BG)
chat_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

scrollbar = tk.Scrollbar(chat_frame, bg=C_BORDER, troughcolor=C_BG,
                         activebackground=C_ACCENT, width=8, relief=tk.FLAT)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

msg_canvas = tk.Canvas(chat_frame, bg=C_BG, highlightthickness=0,
                       yscrollcommand=scrollbar.set)
msg_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=msg_canvas.yview)

# Inner frame inside canvas for messages
inner_frame = tk.Frame(msg_canvas, bg=C_BG)
inner_window = msg_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

def _on_canvas_config(e):
    msg_canvas.itemconfig(inner_window, width=e.width)

def _on_inner_config(e):
    msg_canvas.configure(scrollregion=msg_canvas.bbox("all"))
    msg_canvas.yview_moveto(1.0)

msg_canvas.bind("<Configure>", _on_canvas_config)
inner_frame.bind("<Configure>", _on_inner_config)

# Mousewheel scroll
def _on_mousewheel(e):
    msg_canvas.yview_scroll(int(-1*(e.delta/120)), "units")

msg_canvas.bind_all("<MouseWheel>", _on_mousewheel)

_messages = []

def _add_message(sender, text, typing_delay=False):
    """Render a styled chat bubble into inner_frame."""
    is_user = (sender == "user")
    time_str = datetime.datetime.now().strftime("%I:%M %p")

    bubble_frame = tk.Frame(inner_frame, bg=C_BG)
    bubble_frame.pack(fill=tk.X, padx=14, pady=5)

    # Align
    align_side = tk.RIGHT if is_user else tk.LEFT
    bubble_bg  = C_BUBBLE_USR if is_user else C_BUBBLE_BOT
    text_color = C_TEXT
    name_color = C_ACCENT2 if is_user else C_ACCENT
    name_label = "You" if is_user else "HASH AI"

    # Inner content frame (for bubble effect)
    content = tk.Frame(bubble_frame, bg=bubble_bg, bd=0, pady=8, padx=12)

    # Name + time row
    top_row = tk.Frame(content, bg=bubble_bg)
    top_row.pack(fill=tk.X)
    tk.Label(top_row, text=name_label, font=FONT_NAME, bg=bubble_bg,
             fg=name_color).pack(side=tk.LEFT)
    tk.Label(top_row, text=f"  {time_str}", font=FONT_META, bg=bubble_bg,
             fg=C_SUBTEXT).pack(side=tk.LEFT)

    # Separator line
    tk.Frame(content, bg=C_BORDER, height=1).pack(fill=tk.X, pady=(4, 6))

    # Message label (wrapping)
    max_w = 500

    # Parse **bold** and *italic* inline
    msg_label = tk.Text(content, font=FONT_MSG, bg=bubble_bg, fg=text_color,
                        wrap=tk.WORD, relief=tk.FLAT, cursor="arrow",
                        state=tk.NORMAL, borderwidth=0, width=55,
                        highlightthickness=0)

    # Configure text tags
    msg_label.tag_configure("bold",   font=("Consolas", 12, "bold"),   foreground=C_ACCENT2)
    msg_label.tag_configure("italic", font=("Consolas", 12, "italic"),  foreground=C_ACCENT)
    msg_label.tag_configure("normal", font=FONT_MSG,                    foreground=C_TEXT)
    msg_label.tag_configure("header", font=("Consolas", 12, "bold"),   foreground=C_ACCENT)
    msg_label.tag_configure("code",   font=("Consolas", 11),            foreground="#a5f3fc")

    # Insert formatted text
    _insert_formatted(msg_label, text)
    msg_label.config(state=tk.DISABLED)
    msg_label.pack(anchor=tk.W)

    content.pack(side=align_side, anchor="ne" if is_user else "nw", ipadx=2)

    # Left accent bar for bot messages
    if not is_user:
        bar = tk.Frame(bubble_frame, bg=C_ACCENT, width=3)
        bar.pack(side=tk.LEFT, fill=tk.Y, before=content)

    _messages.append((sender, text))
    msg_canvas.yview_moveto(1.0)
    root.update_idletasks()


def _insert_formatted(widget, text):
    """Parse **bold**, *italic*, and ━ lines into styled text widget inserts."""
    lines = text.split("\n")
    for li, line in enumerate(lines):
        # Check for dividers
        if line.strip().startswith("━"):
            widget.insert(tk.END, line + "\n", "header")
            continue
        # Parse inline **bold** and *italic*
        pattern = re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)")
        pos = 0
        for match in pattern.finditer(line):
            # Normal text before match
            if match.start() > pos:
                widget.insert(tk.END, line[pos:match.start()], "normal")
            full = match.group(0)
            if full.startswith("**"):
                widget.insert(tk.END, match.group(2), "bold")
            elif full.startswith("`"):
                widget.insert(tk.END, match.group(4), "code")
            else:
                widget.insert(tk.END, match.group(3), "italic")
            pos = match.end()
        widget.insert(tk.END, line[pos:], "normal")
        if li < len(lines) - 1:
            widget.insert(tk.END, "\n", "normal")


def _show_typing():
    """Show a temporary 'typing...' indicator bubble."""
    frame = tk.Frame(inner_frame, bg=C_BG)
    frame.pack(fill=tk.X, padx=14, pady=2)
    bar  = tk.Frame(frame, bg=C_ACCENT, width=3)
    bar.pack(side=tk.LEFT, fill=tk.Y)
    inner = tk.Frame(frame, bg=C_BUBBLE_BOT, pady=6, padx=12)
    inner.pack(side=tk.LEFT)
    lbl = tk.Label(inner, text="HASH AI is typing", font=FONT_META,
                   bg=C_BUBBLE_BOT, fg=C_SUBTEXT)
    lbl.pack()
    dots_lbl = tk.Label(inner, text="●  ●  ●", font=FONT_META,
                        bg=C_BUBBLE_BOT, fg=C_ACCENT)
    dots_lbl.pack()
    msg_canvas.yview_moveto(1.0)
    root.update_idletasks()
    return frame


def _render_welcome():
    welcome = (
        "👋 Welcome to **HASH AI** — Hyper-Advanced Smart Helper!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "I can chat, do math, convert units, tell jokes,\n"
        "share fun facts, play games, answer questions & more!\n\n"
        "Type **help** to see all commands. Let's get started! 🚀"
    )
    _add_message("hash", welcome)


_render_welcome()

# ── Input Bar ────────────────────────────────────────────────────────────────
input_bar = tk.Frame(root, bg=C_BORDER, height=2)
input_bar.pack(fill=tk.X)

input_outer = tk.Frame(root, bg=C_BG, pady=10)
input_outer.pack(fill=tk.X, padx=14)

input_inner = tk.Frame(input_outer, bg=C_INPUT_BG, bd=0,
                       highlightbackground=C_BORDER,
                       highlightcolor=C_ACCENT,
                       highlightthickness=1)
input_inner.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=6)

entry = tk.Entry(input_inner, font=FONT_INPUT, bg=C_INPUT_BG, fg=C_TEXT,
                 insertbackground=C_ACCENT, relief=tk.FLAT, bd=0)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=4)
entry.focus()

def _on_focus_in(e):
    input_inner.config(highlightcolor=C_ACCENT, highlightbackground=C_ACCENT)

def _on_focus_out(e):
    input_inner.config(highlightcolor=C_BORDER, highlightbackground=C_BORDER)

entry.bind("<FocusIn>",  _on_focus_in)
entry.bind("<FocusOut>", _on_focus_out)

# Character counter
char_count = tk.Label(input_outer, text="0", font=FONT_META,
                      bg=C_BG, fg=C_SUBTEXT, width=4)
char_count.pack(side=tk.RIGHT, padx=(4, 0))

def _update_char_count(e=None):
    n = len(entry.get())
    char_count.config(text=str(n), fg=C_DANGER if n > 200 else C_SUBTEXT)

entry.bind("<KeyRelease>", _update_char_count)

def send_message(e=None):
    user_text = entry.get().strip()
    if not user_text:
        return
    entry.delete(0, tk.END)
    _update_char_count()

    _add_message("user", user_text)

    # Show typing indicator, then process reply with delay for effect
    typing_frame = _show_typing()

    def _process():
        time.sleep(random.uniform(0.4, 0.9))
        reply = brain(user_text)
        root.after(0, lambda: (
            typing_frame.destroy(),
            _add_message("hash", reply),
            save_history(user_text, reply),
            speak(reply) if _voice_on[0] else None,
        ))

    threading.Thread(target=_process, daemon=True).start()

entry.bind("<Return>", send_message)

# Send button with hover
send_btn = tk.Button(input_outer, text="Send  ➤", font=FONT_BTN,
                     bg=C_BTN, fg="#0f172a", relief=tk.FLAT, bd=0,
                     cursor="hand2", command=send_message,
                     activebackground=C_BTN_HOV, activeforeground="#0f172a",
                     padx=18, pady=8)
send_btn.pack(side=tk.RIGHT, padx=(10, 0))

def _on_btn_enter(e): send_btn.config(bg=C_BTN_HOV)
def _on_btn_leave(e): send_btn.config(bg=C_BTN)
send_btn.bind("<Enter>", _on_btn_enter)
send_btn.bind("<Leave>", _on_btn_leave)

# ── Status Bar ───────────────────────────────────────────────────────────────
status_bar = tk.Frame(root, bg=C_SIDEBAR, height=26)
status_bar.pack(fill=tk.X, side=tk.BOTTOM)
status_bar.pack_propagate(False)

tk.Label(status_bar, text="⬡ HASH AI v2.0  •  Offline Mode  •  Memory Enabled",
         font=FONT_META, bg=C_SIDEBAR, fg=C_SUBTEXT).pack(side=tk.LEFT, padx=12)

session_count = tk.Label(status_bar, text=f"Session messages: 0",
                          font=FONT_META, bg=C_SIDEBAR, fg=C_SUBTEXT)
session_count.pack(side=tk.RIGHT, padx=12)

def _update_status():
    session_count.config(text=f"Messages this session: {len(_messages)}")
    root.after(1000, _update_status)

_update_status()

root.mainloop()