import os
import yaml
import requests
from datetime import datetime
import pytz

from dotenv import load_dotenv
load_dotenv()


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "medicines.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_time_of_day() -> str:
    jst = pytz.timezone("Asia/Tokyo")
    hour = datetime.now(jst).hour
    return "morning" if 5 <= hour < 15 else "evening"


def build_flex_message(medicines: list, time_of_day: str) -> dict | None:
    time_label = "朝" if time_of_day == "morning" else "夜"
    time_emoji = "🌅" if time_of_day == "morning" else "🌙"

    relevant = [m for m in medicines if time_of_day in m.get("timing", [])]
    if not relevant:
        return None

    med_lines = []
    for med in relevant:
        note = f"（{med['note']}）" if med.get("note") else ""
        med_lines.append({
            "type": "text",
            "text": f"・{med['name']}{note}",
            "size": "sm",
            "color": "#555555",
        })

    return {
        "type": "flex",
        "altText": f"{time_emoji} {time_label}のお薬の時間です！",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"💊 {time_emoji} {time_label}のお薬",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#ffffff",
                    }
                ],
                "backgroundColor": "#2196F3",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "以下のお薬を飲んでください",
                        "size": "sm",
                        "color": "#888888",
                    },
                    {"type": "separator"},
                    *med_lines,
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#4CAF50",
                        "action": {
                            "type": "postback",
                            "label": "✅ 飲んだ",
                            "data": "medicine_taken",
                            "displayText": "お薬を飲みました",
                        },
                    }
                ],
            },
        },
    }


def send_to_line(message: dict, user_id: str) -> None:
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={"to": user_id, "messages": [message]},
    ).raise_for_status()


def main():
    config = load_config()
    time_of_day = os.environ.get("TIME_OF_DAY") or get_time_of_day()

    print(f"[{datetime.now()}] お薬リマインダー実行 ({time_of_day})")

    flex_message = build_flex_message(config["medicines"], time_of_day)
    if not flex_message:
        print("この時間帯のお薬はありません")
        return

    user_id = os.environ.get("LINE_USER_ID", "")
    if not user_id:
        raise ValueError("LINE_USER_ID が設定されていません")

    send_to_line(flex_message, user_id)
    print(f"LINE送信完了: {user_id}")


if __name__ == "__main__":
    main()
