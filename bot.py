import json
import logging
import asyncio
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# ===== CONFIGURATION =====
BOT_TOKEN = "8321984658:AAH4IwP62LXQfHbf1rMdVNdUWhuqnsyEYb8"  # Replace with your bot token

# Developer Info
DEV_NAME = "Mᴏᴏɴ x Xᴅ"
ADMIN_USERNAME = "mooN_X_2006"
ADMIN_URL = f"http://t.me/{ADMIN_USERNAME}"

# Channel Info
TELEGRAM_CHANNEL = "@chandxxd"
TELEGRAM_CHANNEL_ID = -1003233462140
WHATSAPP_CHANNEL = "https://whatsapp.com/channel/0029Vb7HL5C0rGiUaquNz21g"
PHOTO_URL = "https://files.catbox.moe/ur82q7.png"

# ===== LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== RATE LIMIT =====
user_requests = {}
DAILY_LIMIT = 7
REFERRAL_LIMIT = 5

# ===== API ENDPOINTS =====
APIS = {
    "number": "https://leak-osint.noob73613.workers.dev/?query={query}",
    "vehicle": "https://rc-x.paskhinpf9.workers.dev/?vehicle={query}",
    "ifsc": "https://ifsc.razorpay.com/{query}",
    "ff": "https://api.dictech.dev/freefire/player?id={query}",
    "ffban": "https://api.dictech.dev/freefire/player?id={query}",
    "mail": "https://leak-osint.noob73613.workers.dev/?query={query}",
    "pan": "https://api.data.gov.in/resource/pan?pan={query}",
    "indian": "https://leak-osint.noob73613.workers.dev/?query={query}",
    "ip": "http://ip-api.com/json/{query}",
    "github": "https://api.github.com/users/{query}",
    "instagram": "https://api.instagram.com/v1/users/{query}/info"
}

# ===== HELPER FUNCTIONS =====
def get_developer_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("✨ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=ADMIN_URL)]])

def check_rate_limit(user_id):
    today = datetime.now().date()
    if user_id not in user_requests:
        user_requests[user_id] = {"date": today, "count": 0}
    
    data = user_requests[user_id]
    if data["date"] != today:
        data["date"] = today
        data["count"] = 0
    
    if data["count"] >= DAILY_LIMIT:
        return False
    
    data["count"] += 1
    return True

async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(TELEGRAM_CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def fetch_api(url):
    """Fetch data from API using requests"""
    try:
        logger.info(f"Fetching: {url}")
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None

async def delete_after(context, chat_id, msg_id, delay=60):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id, msg_id)
    except:
        pass

# ===== COMMAND HANDLERS =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if await check_membership(user_id, context):
        menu = f"""┌───  「 ⚙️ ʙᴏᴛ ɪɴғᴏ 」
│ 👤 ᴅᴇᴠᴇʟᴏᴘᴇʀ: {DEV_NAME}
│ 🏷 ʙᴏᴛ-ɴᴀᴍᴇ: ᴄʜᴀɴᴅ x ᴏsɪɴᴛ ʙᴏᴛ
│ 🛡 sᴜᴘᴘᴏʀᴛ  : ᴍᴏᴏɴ x xᴅ ᴛᴇᴄʜ
└───────────────────╼

┌───  「 🕹 ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴍᴅꜱ 」
│
│ 📱 /num   ➜ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ᴅɪᴛᴀɪʟꜱ
│ 🏍️ /vehicle  ➜ ᴠᴇʜɪᴄʟᴇꜱ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ
│ 🏦 /ifsc  ➜ ʙᴀɴᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
│ 🎮 /ff    ➜ ғғ ᴘʟᴀʏᴇʀ ᴅᴇᴛᴀɪʟs
│ 🚫 /ffban ➜ ғғ ɪᴅ ʙᴀɴ ᴄʜᴇᴄᴋ
│ 📧 /mail  ➜ ᴇᴍᴀɪʟ ᴠᴇʀɪғɪᴇʀ
│ 💳 /pan   ➜ ᴘᴀɴ ᴄᴀʀᴅ ᴅᴇᴛᴀɪʟs
│ 🇮🇳 /in   ➜ ɪɴᴅɪᴀɴ ᴅᴀᴛᴀ
│ 🌐 /ip    ➜ ɪᴘ ᴀᴅᴅʀᴇss ᴛʀᴀᴄᴋᴇʀ
│ 🐙 /git   ➜ ɢɪᴛʜᴜʙ ᴘʀᴏғɪʟᴇ
│ 📸 /insta ➜ ɪɢ ᴜsᴇʀ ɪɴғᴏ
│ 🎭 /mask  ➜ ɴᴀᴍᴇ ᴍᴀsᴋɪɴɢ
│
└───────────────────╼

┌───  「 🚀 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ 」
│ ➊ sᴛᴀʀᴛ ʙᴏᴛ ʙʏ ꜱᴇɴᴅɪɴɢ /start
│ ➋ ᴊᴏɪɴ ᴛʜᴇ ᴀʙᴏᴠᴇ ᴄʜᴀɴɴᴇʟꜱ (ᴍᴜsᴛ)
│ ➌ ᴜsᴇ ᴄᴍᴅ + ɪɴᴘᴜᴛ
│ ➍ ɢᴇᴛ ɪɴsᴛᴀɴᴛ ᴘʀᴇᴍɪᴜᴍ ᴅᴀᴛᴀ
│ ➎ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ: 𝟼𝟶ꜱ
└───────────────────╼

┌───  「 ⚠️ ᴀᴅᴍɪɴ ɴᴏᴛᴇ 」
│ ᴅᴀɪʟʏ ʟɪᴍɪᴛ: {DAILY_LIMIT:02d} ʀᴇǫᴜᴇsᴛs. 
│ ɴᴇᴇᴅ ᴍᴏʀᴇ? 𝐂𝙾𝙼𝙿𝙻𝙴𝚃𝙴 {REFERRAL_LIMIT} 𝚁𝙴𝙵𝙵𝙴𝚁𝚂
└───────────────────╼"""
        
        await update.message.reply_photo(
            photo=PHOTO_URL,
            caption=menu,
            reply_markup=get_developer_keyboard()
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📱 ᴊᴏɪɴ ᴡʜᴀᴛsᴀᴘᴘ ᴄʜᴀɴɴᴇʟ", url=WHATSAPP_CHANNEL)],
            [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{TELEGRAM_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ ᴄʜᴇᴄᴋ ᴍᴇᴍʙᴇʀsʜɪᴘ", callback_data="check_membership")]
        ]
        
        welcome = f"""🌟 *ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴄʜᴀɴᴅ-x-ɪɴғᴏ-ʙᴏᴛ* 🌟

👋 ʜᴇʟʟᴏ {user.first_name}!

⚠️ *ɪᴍᴘᴏʀᴛᴀɴᴛ:* ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs!

📱 ᴊᴏɪɴ ᴡʜᴀᴛsᴀᴘᴘ ᴄʜᴀɴɴᴇʟ
📢 ᴊᴏɪɴ ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ

ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴄʟɪᴄᴋ 'ᴄʜᴇᴄᴋ ᴍᴇᴍʙᴇʀsʜɪᴘ'"""
        
        await update.message.reply_photo(
            photo=PHOTO_URL,
            caption=welcome,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if await check_membership(user_id, context):
        await query.message.edit_caption(
            caption="✅ *ᴍᴇᴍʙᴇʀsʜɪᴘ ᴄᴏɴғɪʀᴍᴇᴅ!*\n\nʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.\nsᴇɴᴅ /start ᴛᴏ sᴇᴇ ᴛʜᴇ ᴍᴇɴᴜ.",
            reply_markup=get_developer_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.message.edit_caption(
            caption="❌ *ɴᴏᴛ ᴊᴏɪɴᴇᴅ ʏᴇᴛ!*\n\nᴘʟᴇᴀsᴇ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!",
            reply_markup=query.message.reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

# ===== API COMMAND HANDLER =====
async def handle_api(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str, title: str, usage: str):
    """Generic handler for all API commands"""
    user = update.effective_user
    user_id = user.id
    
    # Check membership
    if not await check_membership(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📱 ᴡʜᴀᴛsᴀᴘᴘ", url=WHATSAPP_CHANNEL)],
            [InlineKeyboardButton("📢 ᴛᴇʟᴇɢʀᴀᴍ", url=f"https://t.me/{TELEGRAM_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ ᴄʜᴇᴄᴋ", callback_data="check_membership")]
        ]
        await update.message.reply_text("❌ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Check rate limit
    if not check_rate_limit(user_id):
        await update.message.reply_text(f"❌ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ! ({DAILY_LIMIT} ʀᴇǫᴜᴇsᴛs)\nᴄᴏᴍᴘʟᴇᴛᴇ {REFERRAL_LIMIT} ʀᴇғᴇʀʀᴀʟs ғᴏʀ ᴍᴏʀᴇ.")
        return
    
    # Check input
    if not context.args:
        await update.message.reply_text(f"❌ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ɪɴᴘᴜᴛ!\n\nᴜsᴀɢᴇ: {usage}")
        return
    
    query = " ".join(context.args)
    msg = await update.message.reply_text("🔄 ᴘʀᴏᴄᴇssɪɴɢ...")
    
    # Fetch from API
    url = APIS[api_key].format(query=query)
    data = fetch_api(url)
    
    if data:
        try:
            # Try to format as JSON
            json_data = json.loads(data)
            formatted = json.dumps(json_data, indent=2, ensure_ascii=False)
            response = f"{title}\n\n```json\n{formatted}\n```"
        except:
            response = f"{title}\n\n{data}"
        
        # Send response
        try:
            result = await update.message.reply_photo(
                photo=PHOTO_URL,
                caption=response[:1024],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_developer_keyboard()
            )
        except:
            result = await update.message.reply_text(
                response[:4000],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_developer_keyboard()
            )
        
        # Auto-delete after 60 seconds
        asyncio.create_task(delete_after(context, update.effective_chat.id, result.message_id, 60))
    else:
        await update.message.reply_text(
            "❌ ɴᴏ ᴅᴀᴛᴀ ғᴏᴜɴᴅ.\n\nᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɪɴᴘᴜᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.",
            reply_markup=get_developer_keyboard()
        )
    
    await msg.delete()

# ===== INDIVIDUAL COMMANDS =====
async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "number", "📱 ɴᴜᴍʙᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ", "/num <number>")

async def vehicle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "vehicle", "🏍️ ᴠᴇʜɪᴄʟᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ", "/vehicle <vehicle_number>")

async def ifsc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "ifsc", "🏦 ʙᴀɴᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ", "/ifsc <ifsc_code>")

async def ff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "ff", "🎮 ғғ ᴘʟᴀʏᴇʀ ᴅᴇᴛᴀɪʟs", "/ff <player_id>")

async def ffban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "ffban", "🚫 ғғ ʙᴀɴ ᴄʜᴇᴄᴋ", "/ffban <player_id>")

async def mail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "mail", "📧 ᴇᴍᴀɪʟ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ", "/mail <email>")

async def pan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "pan", "💳 ᴘᴀɴ ᴄᴀʀᴅ ᴅᴇᴛᴀɪʟs", "/pan <pan_number>")

async def indian_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "indian", "🇮🇳 ɪɴᴅɪᴀɴ ᴅᴀᴛᴀ", "/in <query>")

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "ip", "🌐 ɪᴘ ᴛʀᴀᴄᴋᴇʀ", "/ip <ip_address>")

async def git_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "github", "🐙 ɢɪᴛʜᴜʙ ᴘʀᴏғɪʟᴇ", "/git <username>")

async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_api(update, context, "instagram", "📸 ɪɴsᴛᴀɢʀᴀᴍ ᴘʀᴏғɪʟᴇ", "/insta <username>")

async def mask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if not await check_membership(user_id, context):
        await update.message.reply_text("❌ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ɴᴀᴍᴇ!\n\nᴜsᴀɢᴇ: /mask <name>")
        return
    
    name = " ".join(context.args)
    masked = "".join(c if i % 2 == 0 or c == " " else "*" for i, c in enumerate(name))
    
    result = f"🎭 *ɴᴀᴍᴇ ᴍᴀsᴋɪɴɢ*\n\n📝 ᴏʀɪɢɪɴᴀʟ: `{name}`\n🎭 ᴍᴀsᴋᴇᴅ: `{masked}`"
    
    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=result,
        reply_markup=get_developer_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("num", num_command))
    app.add_handler(CommandHandler("vehicle", vehicle_command))
    app.add_handler(CommandHandler("ifsc", ifsc_command))
    app.add_handler(CommandHandler("ff", ff_command))
    app.add_handler(CommandHandler("ffban", ffban_command))
    app.add_handler(CommandHandler("mail", mail_command))
    app.add_handler(CommandHandler("pan", pan_command))
    app.add_handler(CommandHandler("in", indian_command))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("git", git_command))
    app.add_handler(CommandHandler("insta", insta_command))
    app.add_handler(CommandHandler("mask", mask_command))
    
    # Callback handler
    app.add_handler(CallbackQueryHandler(check_callback, pattern="check_membership"))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    print("""
╔══════════════════════════════════╗
║     🤖 ᴍɴx-INFO-BOT STARTED     ║
║     Developer: ᴍᴏᴏɴ x xᴅ      ║
║     Bot is now running...       ║
╚══════════════════════════════════╝
    """)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()