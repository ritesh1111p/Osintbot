# osint_bot_final.py
import telebot
import re
import sqlite3
import requests
from datetime import datetime
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

# ===== YOUR CREDENTIALS =====
BOT_TOKEN = "8321984658:AAFnGjixzj3CD9TzDLmTVLy7qXcvWVMJl5o"
OWNER_ID = 5924662015
API_KEY = "ff96fcecf4e8009dac2cbbb9505034f6"   # aapki di hui key

bot = telebot.TeleBot(BOT_TOKEN)

# ===== DATABASE =====
DB = "osint_logs.db"
conn = sqlite3.connect(DB, check_same_thread=False)
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

def log(user_id, qtype, query, result):
    c.execute("INSERT INTO logs (user_id, query_type, query, result, timestamp) VALUES (?,?,?,?,?)",
              (user_id, qtype, query, str(result), datetime.now().isoformat()))
    conn.commit()

# ========== PHONE OSINT (Numverify API) ==========
def phone_lookup(number):
    try:
        parsed = phonenumbers.parse(number, None)
        if not phonenumbers.is_valid_number(parsed):
            return {"error": "Invalid phone number"}
    except:
        return {"error": "Invalid phone number format"}
    
    url = f"http://apilayer.net/api/validate?access_key={API_KEY}&number={number}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("valid"):
            return {
                "number": data.get("number"),
                "country": data.get("country_name"),
                "location": data.get("location"),
                "carrier": data.get("carrier"),
                "line_type": data.get("line_type"),
                "is_valid": True
            }
        else:
            return {"error": "Number not valid or API limit exceeded"}
    except Exception as e:
        return {"error": f"API error: {str(e)}"}

# ========== AADHAAR VALIDATION ==========
def aadhaar_check(num):
    num = re.sub(r'\D', '', num)
    if not re.match(r'^[2-9]\d{11}$', num):
        return {"error": "Invalid format. Must be 12 digits starting 2-9."}
    # Simple validation (no real data)
    return {
        "aadhaar": num,
        "valid": True,
        "note": "Aadhaar data is not publicly available. Only format validation is done."
    }

# ========== TELEGRAM COMMANDS ==========
@bot.message_handler(commands=['start', 'help'])
def start(msg):
    bot.reply_to(msg, """
🔥 *MOONHACKER OSINT Bot* 🔥

Commands:
/phone +919876543210 → Get country, carrier, location, line type
/aadhaar 123456789012 → Validate Aadhaar (format only)
/logs (owner only) → View query logs

⚠️ *Note:* Phone OSINT uses Numverify API (100 req/month free).
    """, parse_mode='Markdown')

@bot.message_handler(commands=['phone'])
def phone_cmd(msg):
    args = msg.text.split()
    if len(args) != 2:
        return bot.reply_to(msg, "❌ Usage: /phone +<country_code><number>")
    result = phone_lookup(args[1])
    log(msg.from_user.id, "phone", args[1], result)
    if "error" in result:
        return bot.reply_to(msg, f"❌ {result['error']}")
    text = f"""📱 *Phone OSINT*
Number: `{result['number']}`
Country: {result['country']}
Location: {result['location']}
Carrier: {result['carrier']}
Line Type: {result['line_type']}
✅ Valid
    """
    bot.reply_to(msg, text, parse_mode='Markdown')

@bot.message_handler(commands=['aadhaar'])
def aadhaar_cmd(msg):
    args = msg.text.split()
    if len(args) != 2:
        return bot.reply_to(msg, "❌ Usage: /aadhaar <12-digit>")
    result = aadhaar_check(args[1])
    log(msg.from_user.id, "aadhaar", args[1], result)
    if "error" in result:
        return bot.reply_to(msg, f"❌ {result['error']}")
    text = f"""🆔 *Aadhaar Validation*
Number: `{result['aadhaar']}`
Status: ✅ Valid
Note: {result['note']}
    """
    bot.reply_to(msg, text, parse_mode='Markdown')

@bot.message_handler(commands=['logs'])
def logs(msg):
    if msg.from_user.id != OWNER_ID:
        return bot.reply_to(msg, "❌ Owner only")
    c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    if not rows:
        return bot.reply_to(msg, "No logs")
    text = "📋 *Recent Queries*\n"
    for r in rows:
        text += f"{r[1]} | {r[2]} | {r[3]} | {r[5][:16]}\n"
    bot.reply_to(msg, text, parse_mode='Markdown')

# ===== START =====
print("""
╔════════════════════════════════════════════════════╗
║   MOON HACKER – OSINT Bot                        ║
║   Phone + Aadhaar OSINT                          ║
╚════════════════════════════════════════════════════╝
🔥 Bot Started with your credentials!
""")
bot.infinity_polling()
