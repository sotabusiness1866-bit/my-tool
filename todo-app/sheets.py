"""Googleスプレッドシートをデータ保存先として使うためのデータ層。

各やること（Todo）は1行で、列は次の通り:
    タイトル | 内容 | 期日

環境変数:
    GOOGLE_CREDENTIALS_FILE  サービスアカウントの認証JSONへのパス
                             (デフォルト: credentials.json)
    SPREADSHEET_NAME         スプレッドシートの名前 (デフォルト: TodoApp)
"""

import json
import os
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "TodoApp")

HEADER = ["タイトル", "内容", "期日"]


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
        worksheet.update([HEADER], "A1:C1")

    return worksheet


def list_todos():
    """全てのやることを辞書のリストで返す。行番号をidとして付与する。"""
    worksheet = _get_worksheet()
    rows = worksheet.get_all_values()
    if len(rows) <= 1:
        return []
    todos = []
    for i, row in enumerate(rows[1:], start=2):
        todos.append({
            "id": i,
            "title": row[0] if len(row) > 0 else "",
            "content": row[1] if len(row) > 1 else "",
            "due_date": row[2] if len(row) > 2 else "",
        })
    return todos


def get_todo(todo_id):
    """行番号で1件のやることを取得する。無ければ None。"""
    worksheet = _get_worksheet()
    row = worksheet.row_values(int(todo_id))
    if not row:
        return None
    return {
        "id": int(todo_id),
        "title": row[0] if len(row) > 0 else "",
        "content": row[1] if len(row) > 1 else "",
        "due_date": row[2] if len(row) > 2 else "",
    }


def add_todo(title, content, due_date):
    """新しいやることを追加する。"""
    worksheet = _get_worksheet()
    worksheet.append_row([title, content, due_date])


def update_todo(todo_id, title, content, due_date):
    """行番号で既存のやることを更新する。"""
    worksheet = _get_worksheet()
    row = int(todo_id)
    worksheet.update([[title, content, due_date]], f"A{row}:C{row}")
    return True


def delete_todo(todo_id):
    """行番号で指定したやることを削除する。"""
    worksheet = _get_worksheet()
    worksheet.delete_rows(int(todo_id))


def validate_due_date(due_date):
    """期日が YYYY-MM-DD 形式か、または空かを確認する。"""
    if not due_date:
        return True
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
