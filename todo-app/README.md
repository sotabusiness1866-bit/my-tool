# Todo リストアプリ

Python (Flask) 製の Todo リストアプリです。データの保存には Google スプレッドシートを使います。

## 機能

- **登録・編集** — やることを登録、あとから編集できる
- **4つの項目** — タイトル・内容・期日・優先度（高・中・低）を設定できる
- **一覧ページ** — 登録したやることをまとめて確認できる（未完了かつ優先度の高い順）
- **完了・未完了の切り替え** — チェックボックスでワンクリック
- **削除**
- **統計・分析** — 完了数、全体の達成率、今週・今月の達成率（期日基準）、優先度別の達成率を確認できる
- **Googleカレンダー連携** — OAuth 2.0でユーザー認証し、期日ありのやることを登録・編集・完了切替・削除すると、対応するGoogleカレンダーの予定も自動で作成・更新・削除される

## 構成

| ファイル | 役割 |
|---|---|
| `app.py` | Flask 本体（ページとルーティング） |
| `sheets.py` | Google スプレッドシートへの読み書き |
| `calendar_service.py` | Google カレンダーとの連携（OAuth 2.0） |
| `templates/` | 画面（一覧・登録/編集フォーム・統計） |

## セットアップ

### 1. ライブラリのインストール

```bash
cd todo-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Google スプレッドシートの準備

データ保存先として Google の「サービスアカウント」を使います。

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. 「API とサービス」→ **Google Sheets API** と **Google Drive API** を有効化
3. 「認証情報」→ **サービスアカウント** を作成
4. 作成したサービスアカウントの **鍵（JSON）** をダウンロードし、
   このフォルダに `credentials.json` という名前で置く
5. `credentials.json` の中の `client_email`（`...@....iam.gserviceaccount.com`）を
   コピーしておく

> アプリは `TodoApp` という名前のスプレッドシートを自動で作成します。
> 既存のシートを使いたい場合は、そのシートを上記のサービスアカウントの
> メールアドレスに「編集者」として共有してください。

### 3. Googleカレンダー連携の準備（任意）

カレンダー連携を使わない場合はこの手順は不要です（連携ボタンは表示されますが、押すとエラーになるだけでTodoの登録・編集自体は問題なく使えます）。

1. 上記と**同じ** Google Cloud プロジェクトで「API とサービス」→ **Google Calendar API** を有効化
2. 「認証情報」→ **認証情報を作成** → **OAuth クライアント ID**
   - アプリケーションの種類: **ウェブアプリケーション**
   - 承認済みのリダイレクト URI に `http://127.0.0.1:5000/oauth2callback` を追加
3. ダウンロードしたJSONを `oauth_client_secret.json` という名前でこのフォルダに置く
4. 「OAuth 同意画面」の公開ステータスが「テスト」の場合、**テストユーザー**に自分のGoogleアカウントを追加

### 4. 起動

```bash
python3 app.py
```

ブラウザで http://127.0.0.1:5000 を開きます。カレンダー連携は一覧ページの「📅 Googleカレンダーと連携する」から行います（初回はGoogleのログイン・許可画面が表示されます）。認証後は `token.json` にトークンが保存されます。

## 環境変数

| 変数 | デフォルト | 説明 |
|---|---|---|
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | サービスアカウント認証JSONのパス |
| `GOOGLE_CREDENTIALS_JSON` | なし | サービスアカウント認証JSONの中身そのもの（本番向け、設定されていればファイルより優先） |
| `SPREADSHEET_NAME` | `TodoApp` | 使用するスプレッドシートの名前 |
| `GOOGLE_OAUTH_CLIENT_SECRET_FILE` | `oauth_client_secret.json` | OAuthクライアントのシークレットJSONのパス |
| `GOOGLE_OAUTH_CLIENT_SECRET_JSON` | なし | OAuthクライアントのシークレットJSONの中身そのもの（本番向け、設定されていればファイルより優先） |
| `GOOGLE_OAUTH_TOKEN_FILE` | `token.json` | カレンダー連携の認証トークンの保存先パス |
| `GOOGLE_OAUTH_TOKEN_JSON` | なし | 認証トークンJSONの中身そのもの（本番向け、設定されていればファイルより優先。ディスクが永続化されないホスティング環境ではこちらを使う） |
| `FLASK_SECRET_KEY` | 開発用の固定値 | Flaskのセッション署名鍵（本番では必ず固有のランダム値を設定する） |

本番（Render）では `render.yaml` に定義済みの環境変数をダッシュボードの「Environment」タブから設定します（`sync: false` のものは値がリポジトリに含まれないため、必ず手動で設定が必要です）。

## 注意

`credentials.json`・`oauth_client_secret.json`・`token.json` はいずれも秘密情報です。`.gitignore` で git にコミットされないようにしてあります。絶対に公開しないでください。
