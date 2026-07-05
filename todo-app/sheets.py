"""Googleスプレッドシートをデータ保存先として使うためのデータ層。

各やること（Todo）は1行で、列は次の通り:
    タイトル | 内容 | 期日 | 優先度 | 完了 | カレンダーイベントID

環境変数:
    GOOGLE_CREDENTIALS_FILE  サービスアカウントの認証JSONへのパス
                             (デフォルト: credentials.json)
    SPREADSHEET_NAME         スプレッドシートの名前 (デフォルト: TodoApp)
"""

import json
import os
from datetime import datetime, timedelta

import gspread
from google.oauth2.service_account import Credentials

import calendar_service

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "TodoApp")

HEADER = ["タイトル", "内容", "期日", "優先度", "完了", "カレンダーイベントID"]

PRIORITIES = ["高", "中", "低"]
DEFAULT_PRIORITY = "中"
_PRIORITY_ORDER = {value: index for index, value in enumerate(PRIORITIES)}


def _get_worksheet():
    """スプレッドシートの最初のワークシートを取得する。

    スプレッドシートが無ければ作成し、ヘッダー行も用意する。
    認証は credentials.json ファイルまたは環境変数 GOOGLE_CREDENTIALS_JSON から読む。
    """
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if credentials_json:
        info = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(SPREADSHEET_NAME)

    worksheet = spreadsheet.sheet1

    if worksheet.row_values(1) != HEADER:
        end_column = gspread.utils.rowcol_to_a1(1, len(HEADER))
        worksheet.update([HEADER], f"A1:{end_column}")

    return worksheet


def _row_to_todo(row_index, row):
    priority = row[3] if len(row) > 3 and row[3] in PRIORITIES else DEFAULT_PRIORITY
    return {
        "id": row_index,
        "title": row[0] if len(row) > 0 else "",
        "content": row[1] if len(row) > 1 else "",
        "due_date": row[2] if len(row) > 2 else "",
        "priority": priority,
        "completed": len(row) > 4 and row[4] == "TRUE",
        "event_id": row[5] if len(row) > 5 else "",
    }


def list_todos():
    """全てのやることを辞書のリストで返す。

    行番号をidとして付与し、未完了かつ優先度の高いものが上に来るよう並び替える。
    """
    worksheet = _get_worksheet()
    rows = worksheet.get_all_values()
    if len(rows) <= 1:
        return []
    todos = [_row_to_todo(i, row) for i, row in enumerate(rows[1:], start=2)]
    todos.sort(key=lambda todo: (todo["completed"], _PRIORITY_ORDER[todo["priority"]]))
    return todos


def get_todo(todo_id):
    """行番号で1件のやることを取得する。無ければ None。"""
    worksheet = _get_worksheet()
    row = worksheet.row_values(int(todo_id))
    if not row:
        return None
    return _row_to_todo(int(todo_id), row)


def add_todo(title, content, due_date, priority=DEFAULT_PRIORITY):
    """新しいやることを追加する。期日があればGoogleカレンダーにも予定を作成する。"""
    worksheet = _get_worksheet()
    event_id = ""
    try:
        event_id = calendar_service.create_event(title, content, due_date) or ""
    except Exception as e:
        print(f"[calendar] イベント作成に失敗しました: {e}", flush=True)
    worksheet.append_row([title, content, due_date, priority, "FALSE", event_id])


def update_todo(todo_id, title, content, due_date, priority=DEFAULT_PRIORITY):
    """行番号で既存のやることを更新する（完了状態は変更しない）。

    対応するGoogleカレンダーの予定があれば内容を更新し、期日が無くなった場合は削除する。
    """
    worksheet = _get_worksheet()
    row = int(todo_id)
    existing = worksheet.row_values(row)
    if not existing:
        return False

    event_id = existing[5] if len(existing) > 5 else ""
    try:
        event_id = calendar_service.update_event(event_id, title, content, due_date) or ""
    except Exception as e:
        print(f"[calendar] イベント更新に失敗しました: {e}", flush=True)

    worksheet.update([[title, content, due_date, priority]], f"A{row}:D{row}")
    worksheet.update([[event_id]], f"F{row}")
    return True


def toggle_todo(todo_id):
    """行番号で指定したやることの完了状態を反転させる。

    対応するGoogleカレンダーの予定があればタイトルに完了マークを反映する。
    """
    worksheet = _get_worksheet()
    row = int(todo_id)
    values = worksheet.row_values(row)
    current = values[4] if len(values) > 4 else ""
    new_value = "FALSE" if current == "TRUE" else "TRUE"
    worksheet.update([[new_value]], f"E{row}")

    event_id = values[5] if len(values) > 5 else ""
    title = values[0] if len(values) > 0 else ""
    if event_id:
        try:
            calendar_service.mark_event_status(event_id, title, completed=(new_value == "TRUE"))
        except Exception as e:
            print(f"[calendar] イベント状態更新に失敗しました: {e}", flush=True)
    return True


def delete_todo(todo_id):
    """行番号で指定したやることを削除する。対応するGoogleカレンダーの予定も削除する。"""
    worksheet = _get_worksheet()
    row = int(todo_id)
    values = worksheet.row_values(row)
    event_id = values[5] if len(values) > 5 else ""
    if event_id:
        try:
            calendar_service.delete_event(event_id)
        except Exception as e:
            print(f"[calendar] イベント削除に失敗しました: {e}", flush=True)
    worksheet.delete_rows(row)


def _parse_due_date(due_date):
    """期日文字列を date に変換する。空・不正な場合は None。"""
    try:
        return datetime.strptime(due_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _summarize(todos):
    """やることのリストから件数・完了数・達成率をまとめる。"""
    total = len(todos)
    completed = sum(1 for todo in todos if todo["completed"])
    rate = round(completed / total * 100, 1) if total else 0.0
    return {"total": total, "completed": completed, "rate": rate}


def get_stats():
    """完了数や今週・今月の達成率などの統計情報を返す。

    週・月の達成率は完了日を記録していないため、各やることの「期日」が
    今週・今月に入っているものを対象に、その中での完了割合として算出する。
    """
    todos = list_todos()
    today = datetime.now().date()

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = today.replace(day=1)
    next_month = (
        month_start.replace(year=month_start.year + 1, month=1)
        if month_start.month == 12
        else month_start.replace(month=month_start.month + 1)
    )
    month_end = next_month - timedelta(days=1)

    dated_todos = [(todo, _parse_due_date(todo["due_date"])) for todo in todos]
    week_todos = [todo for todo, due in dated_todos if due and week_start <= due <= week_end]
    month_todos = [todo for todo, due in dated_todos if due and month_start <= due <= month_end]

    priority_stats = {
        priority: _summarize([todo for todo in todos if todo["priority"] == priority])
        for priority in PRIORITIES
    }

    overall = _summarize(todos)
    return {
        "total": overall["total"],
        "completed": overall["completed"],
        "incomplete": overall["total"] - overall["completed"],
        "rate": overall["rate"],
        "week": _summarize(week_todos),
        "month": _summarize(month_todos),
        "priority": priority_stats,
    }


def validate_due_date(due_date):
    """期日が YYYY-MM-DD 形式か、または空かを確認する。"""
    if not due_date:
        return True
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_priority(priority):
    """優先度が既定の値のいずれかかを確認する。"""
    return priority in PRIORITIES
