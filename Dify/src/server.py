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

DIFY_API_BASE_URL = os.environ.get("DIFY_API_BASE_URL", "https://api.dify.ai/v1").rstrip("/")

# LINEユーザーID -> Difyの会話ID。サーバー再起動でリセットされる。
conversation_ids: dict[str, str] = {}


def verify_signature(body: bytes, signature: str) -> bool:
    secret = os.environ["LINE_CHANNEL_SECRET"].encode("utf-8")
    digest = hmac.new(secret, body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def ask_dify(user_id: str, text: str) -> str:
    payload = {
        "inputs": {},
        "query": text,
        "response_mode": "blocking",
        "conversation_id": conversation_ids.get(user_id, ""),
        "user": user_id,
    }
    response = requests.post(
        f"{DIFY_API_BASE_URL}/chat-messages",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['DIFY_API_KEY']}",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    conversation_ids[user_id] = data["conversation_id"]
    return data["answer"]


def reply_text(reply_token: str, text: str) -> None:
    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}",
        },
        json={"replyToken": reply_token, "messages": [{"type": "text", "text": text}]},
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
        if event.get("type") != "message" or event.get("message", {}).get("type") != "text":
            continue

        user_id = event.get("source", {}).get("userId", "unknown")
        reply_token = event.get("replyToken")
        text = event["message"]["text"]

        try:
            answer = ask_dify(user_id, text)
        except requests.HTTPError as e:
            print(f"[ERROR] Dify API request failed: {e}")
            answer = "すみません、うまく回答できませんでした。少し時間をおいて試してください。"

        reply_text(reply_token, answer)

    return {"status": "ok"}
