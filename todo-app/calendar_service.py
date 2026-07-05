"""Google Calendar API との連携（OAuth 2.0 ユーザー認証）。

スプレッドシート用のサービスアカウントとは別に、ユーザー本人のGoogleカレンダーへ
予定を作成・更新・削除するために OAuth 2.0 クライアントを使う。

環境変数:
    GOOGLE_OAUTH_CLIENT_SECRET_FILE  OAuthクライアントのシークレットJSONへのパス
                                      (デフォルト: oauth_client_secret.json)
    GOOGLE_OAUTH_TOKEN_FILE          認証後に発行されるトークンの保存先
                                      (デフォルト: token.json)
"""

import os
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

CLIENT_SECRET_FILE = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET_FILE", "oauth_client_secret.json")
TOKEN_FILE = os.environ.get("GOOGLE_OAUTH_TOKEN_FILE", "token.json")

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
CALENDAR_ID = "primary"


def _build_flow(redirect_uri):
    return Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES, redirect_uri=redirect_uri
    )


def get_authorization_url(redirect_uri):
    """認可画面のURLとCSRF対策用stateを返す。"""
    flow = _build_flow(redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    return auth_url, state


def exchange_code(redirect_uri, state, authorization_response):
    """認可コードをトークンに交換し、トークンファイルへ保存する。"""
    flow = _build_flow(redirect_uri)
    flow.state = state
    flow.fetch_token(authorization_response=authorization_response)
    _save_credentials(flow.credentials)


def disconnect():
    """保存済みトークンを削除し、連携を解除する。"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def is_connected():
    """有効な認証情報があるかどうか。"""
    return _load_credentials() is not None


def _save_credentials(creds):
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


def _load_credentials():
    if not os.path.exists(TOKEN_FILE):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_credentials(creds)
    return creds if creds and creds.valid else None


def _get_service():
    creds = _load_credentials()
    if creds is None:
        return None
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def _event_body(title, content, due_date):
    due = datetime.strptime(due_date, "%Y-%m-%d").date()
    next_day = due + timedelta(days=1)
    return {
        "summary": title,
        "description": content,
        "start": {"date": due.isoformat()},
        "end": {"date": next_day.isoformat()},
    }


def create_event(title, content, due_date):
    """期日ありのやること用にカレンダー予定を作成し、イベントIDを返す。

    未連携、または期日が空の場合は何もせず None を返す。
    """
    if not due_date:
        return None
    service = _get_service()
    if service is None:
        return None
    event = service.events().insert(
        calendarId=CALENDAR_ID, body=_event_body(title, content, due_date)
    ).execute()
    return event.get("id")


def update_event(event_id, title, content, due_date):
    """既存イベントを更新する。

    期日が空になった場合は既存イベントを削除して None を返す。
    event_id が無くまだ期日がある場合は新規作成する。
    """
    if not due_date:
        delete_event(event_id)
        return None
    if not event_id:
        return create_event(title, content, due_date)

    service = _get_service()
    if service is None:
        return event_id
    service.events().update(
        calendarId=CALENDAR_ID, eventId=event_id, body=_event_body(title, content, due_date)
    ).execute()
    return event_id


def mark_event_status(event_id, title, completed):
    """完了・未完了に応じてイベントのタイトルを更新する。"""
    if not event_id:
        return
    service = _get_service()
    if service is None:
        return
    summary = f"✅ {title}" if completed else title
    service.events().patch(
        calendarId=CALENDAR_ID, eventId=event_id, body={"summary": summary}
    ).execute()


def delete_event(event_id):
    """イベントを削除する。event_id が無ければ何もしない。"""
    if not event_id:
        return
    service = _get_service()
    if service is None:
        return
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
