import os
import hashlib
import random
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from web3 import Web3

# --- KONFIGURASI ---
VALIDATOR_URL = "http://localhost:20371"
RPC_URL = "https://sepolia-rpc.scroll.io"

# Setup Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Limiter (Cloudflare Support)
def get_real_user_ip(request: Request):
    if request.headers.get("CF-Connecting-IP"):
        return request.headers.get("CF-Connecting-IP")
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_user_ip)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class ClientRequest(BaseModel):
    input_hash: str
    output_hash: str

# --- FUNGSI BARU: GENERATE ID DARI BLOCKCHAIN TIME ---
def generate_blockchain_based_id(source: str, result: str):
    try:
        # 1. Ambil Timestamp dari Block Terakhir (Real-time Blockchain)
        latest_block = w3.eth.get_block('latest')
        block_timestamp = latest_block.timestamp
        block_number = latest_block.number
        
        print(f"[Relay] Using Block #{block_number} Time: {block_timestamp}")
    except Exception as e:
        print(f"[Relay] RPC Error: {e}, fallback to local time")
        block_timestamp = int(os.times().elapsed) # Fallback darurat

    # 2. Tambahkan Salt (Angka Acak) 
    # Agar jika ada 2 request di blok yang sama, ID tetap beda
    salt = random.randint(1000, 9999)

    # 3. Racik ID
    # Format: Source + Result + BlockTime + Salt
    raw_str = f"{source}{result}{block_timestamp}{salt}"
    
    # 4. Hash jadi bytes32 hex
    return "0x" + hashlib.sha256(raw_str.encode()).hexdigest()

# --- ENDPOINTS ---
@app.post("/relay/anchor")
@limiter.limit("5/minute")
async def anchor_evidence(request: Request, data: ClientRequest):
    
    # Generate ID pakai Waktu Blockchain
    proc_id = generate_blockchain_based_id(data.input_hash, data.output_hash)
    
    payload = {
        "processingId": proc_id,
        "sourceHash": data.input_hash,
        "resultHash": data.output_hash
    }

    print(f"[Relay] ID Generated: {proc_id}")

    try:
        # Kirim ke Validator (yang mungkin ada di localhost port 3000)
        response = requests.post(f"{VALIDATOR_URL}/validate", json=payload, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "SUCCESS",
                "relay_processed_id": proc_id,
                "timestamp_source": "Blockchain Block Time", # Info ke user
                "validator_response": response.json()
            }
        else:
            return {"status": "FAILED", "validator_error": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))