import httpx, uvicorn, json, os
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from x7m import *

app = FastAPI()

# Render uses PORT environment variable
PORT = int(os.environ.get("PORT", 6677))

# Use 0.0.0.0 for Render
HOST = "0.0.0.0"

Key, Iv = b'Yg&tc%DEuh6%Zc^8', b'6oyZDr22E3ychjM%'

def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(HeX, AES.block_size)).hex()

def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(HeX), AES.block_size).hex()

@app.api_route("/ver.php", methods=["GET", "POST"])
async def manual(request: Request):
    print("🔄 ver.php called")
    target = "https://version.ggwhitehawk.com/live/ver.php"

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "connection")
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        r = await client.request(
            request.method,
            target,
            params=dict(request.query_params),
            headers=headers,
            content=await request.body()
        )

    data = r.json()
    # Use Render URL or localhost
    render_url = os.environ.get("RENDER_URL", "http://127.0.0.1:6677")
    data["server_url"] = f"{render_url}/"

    HOP_BY_HOP = {'transfer-encoding', 'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'upgrade', 'proxy-connection'}
    response_headers = {
        k: v for k, v in r.headers.items()
        if k.lower() not in HOP_BY_HOP and k.lower() not in ("content-length", "content-encoding")
    }

    return JSONResponse(content=data, status_code=r.status_code, headers=response_headers)

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
            status_code=500,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            content="Error",
            status_code=500,
            media_type="application/octet-stream"
        )

@app.api_route("/", methods=["GET"])
async def root():
    return JSONResponse({
        "status": "running",
        "server": "PARAHEX",
        "endpoints": ["/ver.php", "/MajorLogin"]
    })

@app.api_route("/health", methods=["GET"])
async def health():
    return JSONResponse({"status": "healthy"})

if __name__ == "__main__":
    print(f"\n🚀 Starting server on http://{HOST}:{PORT}")
    print(f"📡 ver.php -> https://version.ggwhitehawk.com/live/ver.php")
    print(f"📡 MajorLogin -> Capture token")
    print("="*80 + "\n")
    uvicorn.run(app, host=HOST, port=PORT, log_level='info')
