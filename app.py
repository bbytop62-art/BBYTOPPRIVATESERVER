import httpx
import uvicorn
import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

app = FastAPI()

# Get keys from environment variables for security
Key = os.getenv('AES_KEY', 'Yg&tc%DEuh6%Zc^8').encode()
Iv = os.getenv('AES_IV', '6oyZDr22E3ychjM%').encode()

def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(HeX, AES.block_size)).hex()
    
def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(HeX), AES.block_size).hex()

@app.api_route("/ver.php", methods=["GET", "POST"])
async def manual(request: Request):
    target = "https://version.ggwhitehawk.com/live/ver.php"
    
    # Get base URL from environment or use default
    base_url = os.getenv('BASE_URL', 'http://192.168.1.11:6677/')
    
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
    data["server_url"] = base_url
    
    HOP_BY_HOP = {
        'transfer-encoding', 'connection', 'keep-alive', 
        'proxy-authenticate', 'proxy-authorization', 'te', 
        'trailers', 'upgrade', 'proxy-connection'
    }
    response_headers = {
        k: v for k, v in r.headers.items()
        if k.lower() not in HOP_BY_HOP and k.lower() not in ("content-length", "content-encoding")
    }
    
    return JSONResponse(content=data, status_code=r.status_code, headers=response_headers)

@app.api_route("/MajorLogin", methods=["POST"])
async def MajorLoginProxy(request: Request):
    try:
        PyL = await request.body()
        # Assuming decrypt_api and get_available_room are available
        # You might need to import these from x7m or implement them
        x7m = json.loads(get_available_room(decrypt_api(PyL.hex())))
        acess_token, open_id = x7m["29"], x7m["22"]
        
        nikomLhnoud = f""" [b][c][279CF5]














██████╗░██████╗░██╗░░░██╗████████╗░█████╗░██████╗░
██╔══██╗██╔══██╗╚██╗░██╔╝╚══██╔══╝██╔══██╗██╔══██╗
██████╦╝██████╦╝░╚████╔╝░░░░██║░░░██║░░██║██████╔╝
██╔══██╗██╔══██╗░░╚██╔╝░░░░░██║░░░██║░░██║██╔═══╝░
██████╦╝██████╦╝░░░██║░░░░░░██║░░░╚█████╔╝██║░░░░░
╚═════╝░╚═════╝░░░░╚═╝░░░░░░╚═╝░░░░╚════╝░╚═╝░░░░░


─────────────────────────────────────

[cccccc]access Token => [ff0000]{acess_token} [cccccc]| open id => [00ff00]{open_id}

[00ff00]TeLeGram => @BBYTOP3




















                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    """
        
        return Response(content=nikomLhnoud, status_code=500, media_type="application/octet-stream")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# For Render deployment - use this instead of uvicorn.run()
if __name__ == "__main__":
    port = int(os.getenv('PORT', 6677))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')
