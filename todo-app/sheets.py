"""Googleスプレッドシートをデータ保存先として使うためのデータ層。

各やること（Todo）は1行で、列は次の通り:
    id | title | content | due_date

環境変数:
    GOOGLE_CREDENTIALS_FILE  サービスアカウントの認証JSONへのパス
                             (デフォルト: credentials.json)
    SPREADSHEET_NAME         スプレッドシートの名前 (デフォルト: TodoApp)
"""

import json
import os
import uuid
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "TodoApp")

HEADER = ["id", "title", "content", "due_date"]


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

    # ヘッダー行が無ければ作る
    if worksheet.row_values(1) != HEADER:
        worksheet.update([HEADER], "A1:D1")

    return worksheet


def list_todos():
    """全てのやることを辞書のリストで返す。"""
    worksheet = _get_worksheet()
    return worksheet.get_all_records()


def get_todo(todo_id):
    """IDで1件のやることを取得する。無ければ None。"""
    for todo in list_todos():
        if str(todo["id"]) == str(todo_id):
            return todo
    return None


def add_todo(title, content, due_date):
    """新しいやることを追加する。生成したIDを返す。"""
    worksheet = _get_worksheet()
    todo_id = uuid.uuid4().hex[:8]
    worksheet.append_row([todo_id, title, content, due_date])
    return todo_id


def update_todo(todo_id, title, content, due_date):
    """既存のやることを更新する。見つかれば True。"""
    worksheet = _get_worksheet()
    cell = worksheet.find(str(todo_id), in_column=1)
    if cell is None:
        return False
    row = cell.row
    worksheet.update(
        [[str(todo_id), title, content, due_date]],
        f"A{row}:D{row}",
    )
    return True


def validate_due_date(due_date):
    """期日が YYYY-MM-DD 形式か、または空かを確認する。"""
    if not due_date:
        return True
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
