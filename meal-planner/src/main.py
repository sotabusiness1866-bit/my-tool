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
                    "2人分（夫婦2人）の今週（月曜〜日曜）の夕食の献立を7日分考えてください。\n"
                    "予算は食材費合計で週6,500円以内に収めてください。\n"
                    "バリエーション豊かで栄養バランスの良い献立にしてください。\n"
                    "買い物リストは1週間分をまとめて、同じ食材は合算してグラム数・個数を明記してください。\n\n"
                    "以下の形式で出力してください（絵文字・記号はそのまま使用）：\n\n"
                    "🍽 今週の夕食献立（2人分）\n"
                    "━━━━━━━━━━━━\n"
                    "🗓 月｜〇〇\n"
                    "🗓 火｜〇〇\n"
                    "🗓 水｜〇〇\n"
                    "🗓 木｜〇〇\n"
                    "🗓 金｜〇〇\n"
                    "🗓 土｜〇〇\n"
                    "🗓 日｜〇〇\n"
                    "━━━━━━━━━━━━\n"
                    "🛒 今週の買い物リスト\n"
                    "【肉・魚】\n"
                    "・〇〇 〇〇g\n"
                    "【野菜】\n"
                    "・〇〇 〇〇個\n"
                    "【その他】\n"
                    "・〇〇 〇〇g\n"
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
