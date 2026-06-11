import os
import json
import anthropic
import requests
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()


def generate_meal_plan() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    "今週（月曜〜日曜）の夕食の献立を7日分考えてください。\n"
                    "予算は食材費合計で週6,500円以内に収めてください。\n"
                    "バリエーション豊かで栄養バランスの良い献立にしてください。\n\n"
                    "以下の形式で出力してください（絵文字・記号はそのまま使用）：\n\n"
                    "🍽 今週の夕食献立\n"
                    "━━━━━━━━━━━━\n"
                    "🗓 月｜〇〇\n"
                    "　　🛒 〇〇、〇〇、〇〇\n"
                    "　　💴 約〇〇円\n"
                    "🗓 火｜〇〇\n"
                    "　　🛒 〇〇、〇〇、〇〇\n"
                    "　　💴 約〇〇円\n"
                    "🗓 水｜〇〇\n"
                    "　　🛒 〇〇、〇〇、〇〇\n"
                    "　　💴 約〇〇円\n"
                    "🗓 木｜〇〇\n"
                    "　　🛒 〇〇、〇〇、〇〇\n"
                    "　　💴 約〇〇円\n"
                    "🗓 金｜〇〇\n"
                    "　　🛒 〇〇、〇〇、〇〇\n"
                    "　　💴 約〇〇円\n"
                    "🗓 土｜〇〇\n"
                    "　　🛒 〇〇、〇〇、〇〇\n"
                    "　　💴 約〇〇円\n"
                    "🗓 日｜〇〇\n"
                    "　　🛒 〇〇、〇〇、〇〇\n"
                    "　　💴 約〇〇円\n"
                    "━━━━━━━━━━━━\n"
                    "💰 週合計：約〇〇円"
                ),
            }
        ],
    )

    return message.content[0].text


def send_to_line(text: str) -> None:
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        data=json.dumps(
            {
                "to": user_id,
                "messages": [{"type": "text", "text": text}],
            }
        ),
    )
    response.raise_for_status()


def main():
    print(f"[{datetime.now()}] 献立生成開始")
    meal_plan = generate_meal_plan()
    print(f"生成された献立:\n{meal_plan}")
    send_to_line(meal_plan)
    print("LINE への送信完了")


if __name__ == "__main__":
    main()
