import os
import json
import hmac
import hashlib
import base64
import requests
from fastapi import FastAPI, Request, HTTPException

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


def verify_signature(body: bytes, signature: str) -> bool:
    secret = os.environ["LINE_CHANNEL_SECRET"].encode("utf-8")
    digest = hmac.new(secret, body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def push_text(user_id: str, text: str) -> None:
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}",
        },
        json={"to": user_id, "messages": [{"type": "text", "text": text}]},
    ).raise_for_status()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    if not verify_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    events = json.loads(body).get("events", [])
    for event in events:
        if (
            event.get("type") == "postback"
            and event.get("postback", {}).get("data") == "medicine_taken"
        ):
            family_ids = [
                uid.strip()
                for uid in os.environ.get("LINE_FAMILY_IDS", "").split(",")
                if uid.strip()
            ]
            for family_id in family_ids:
                push_text(family_id, "✅ お薬を飲みました！")

    return {"status": "ok"}
