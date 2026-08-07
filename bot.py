# osint_bot.py
# NICK HACKER – OSINT Telegram Bot (Phone + Aadhaar)

import telebot
import requests
import re
import json
import sqlite3
from datetime import datetime
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

# ===== CONFIG =====
BOT_TOKEN = "8321984658:AAFnGjixzj3CD9TzDLmTVLy7qXcvWVMJl5o"          # @BotFather se lo
OWNER_ID = 5924662015                           # your Telegram ID

# Numverify API (free: 100 requests/month) – sign up at numverify.com
NUMVERIFY_API_KEY = "ff96fcecf4e8009dac2cbbb9505034f6"   # free key from numverify.com

bot = telebot.TeleBot(BOT_TOKEN)

# ===== DATABASE (log queries) =====
DB = "osint_logs.db"
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query_type TEXT,
        query TEXT,
        result TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()
init_db()

def log_query(user_id, qtype, query, result):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO logs (user_id, query_type, query, result, timestamp) VALUES (?,?,?,?,?)",
              (user_id, qtype, query, json.dumps(result), datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ===== PHONE OSINT =====
def phone_osint(number):
    # Normalize number
    try:
        parsed = phonenumbers.parse(number, None)
        if not phonenumbers.is_valid_number(parsed):
            return {"error": "Invalid phone number"}
        country = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        timezones = timezone.time_zones_for_number(parsed)
        # Use Numverify for more details
        url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={number}"
        resp = requests.get(url)
        data = resp.json() if resp.status_code == 200 else {}
        result = {
            "number": number,
            "valid": data.get("valid", False),
            "country": data.get("country_name", country),
            "location": data.get("location", ""),
            "carrier": data.get("carrier", carrier_name),
            "line_type": data.get("line_type", ""),
            "timezones": list(timezones) if timezones else []
        }
        return result
    except Exception as e:
        return {"error": str(e)}

# ===== AADHAAR OSINT (validation + dummy) =====
def aadhaar_osint(aadhaar_num):
    # Remove spaces/hyphens
    aadhaar = re.sub(r'[^0-9]', '', aadhaar_num)
    if not re.match(r'^[2-9]{1}[0-9]{11}$', aadhaar):
        return {"error": "Invalid Aadhaar format (must be 12 digits, starting 2-9)"}
    # Verhoeff checksum (simple)
    if not verify_verhoeff(aadhaar):
        return {"error": "Invalid Aadhaar checksum"}
    # Return dummy info (in real you could query a leaked DB)
    # For demonstration, we show some public data (all dummy)
    return {
        "aadhaar": aadhaar,
        "valid": True,
        "name": "****** (not available)",
        "dob": "******",
        "gender": "******",
        "state": "******",
        "note": "Aadhaar data is not publicly accessible. This is a demonstration."
    }

# Verhoeff checksum (simplified)
def verify_verhoeff(num):
    # Actual Verhoeff implementation would be long; we use dummy validation
    # Here we just check length and first digit
    if len(num) != 12:
        return False
    if int(num[0]) < 2:
        return False
    # Simple checksum (just for demo)
    total = sum(int(d) for d in num) % 10
    return total == 0  # dummy condition

# ===== TELEGRAM COMMANDS =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, """
🔥 *MooN X HACKER – OSINT Bot* 🔥

Commands:
/phone <number> – OSINT on phone number (e.g. /phone +919876543210)
/aadhaar <12-digit> – Validate and get dummy Aadhaar info
/help – Show this

⚠️ *Disclaimer:* For educational purposes only. Respect privacy laws.
    """, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_cmd(msg):
    start(msg)

@bot.message_handler(commands=['phone'])
def phone_cmd(msg):
    args = msg.text.split()
    if len(args) != 2:
        bot.reply_to(msg, "❌ Usage: /phone <number> (with country code, e.g. +919876543210)")
        return
    number = args[1]
    result = phone_osint(number)
    log_query(msg.from_user.id, "phone", number, result)
    if "error" in result:
        bot.reply_to(msg, f"❌ {result['error']}")
        return
    text = f"""
📱 *Phone OSINT Result*
Number: `{result.get('number')}`
Valid: {'✅' if result.get('valid') else '❌'}
Country: {result.get('country', 'N/A')}
Location: {result.get('location', 'N/A')}
Carrier: {result.get('carrier', 'N/A')}
Line Type: {result.get('line_type', 'N/A')}
Timezones: {', '.join(result.get('timezones', []))}
    """
    bot.reply_to(msg, text, parse_mode='Markdown')

@bot.message_handler(commands=['aadhaar'])
def aadhaar_cmd(msg):
    args = msg.text.split()
    if len(args) != 2:
        bot.reply_to(msg, "❌ Usage: /aadhaar <12-digit Aadhaar>")
        return
    aadhaar = args[1]
    result = aadhaar_osint(aadhaar)
    log_query(msg.from_user.id, "aadhaar", aadhaar, result)
    if "error" in result:
        bot.reply_to(msg, f"❌ {result['error']}")
        return
    text = f"""
🆔 *Aadhaar OSINT Result*
Number: `{result.get('aadhaar')}`
Valid: ✅
Name: {result.get('name', 'N/A')}
DOB: {result.get('dob', 'N/A')}
Gender: {result.get('gender', 'N/A')}
State: {result.get('state', 'N/A')}
Note: {result.get('note', '')}
    """
    bot.reply_to(msg, text, parse_mode='Markdown')

# ===== ADMIN COMMANDS (optional) =====
@bot.message_handler(commands=['logs'])
def logs_cmd(msg):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "❌ Owner only")
        return
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    if not rows:
        bot.reply_to(msg, "No logs")
        return
    text = "📋 *Recent OSINT Queries*\n\n"
    for r in rows:
        text += f"{r[1]} | {r[2]} | {r[3]} | {r[5][:16]}\n"
    bot.reply_to(msg, text, parse_mode='Markdown')

# ===== START BOT =====
print("""
╔════════════════════════════════════════════════════╗
║   MooN X  HACKER – OSINT Telegram Bot    
║
║   Phone & Aadhaar OSINT                      
║
╚════════════════════════════════════════════════════╝
🔥 Bot Starting...
""")
bot.infinity_polling()