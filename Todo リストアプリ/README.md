# Todo リストアプリ

Python (Flask) 製の Todo リストアプリです。データの保存には Google スプレッドシートを使います。

## 機能

- **登録・編集** — やることを登録、あとから編集できる
- **3つの項目** — タイトル・内容・期日を設定できる
- **一覧ページ** — 登録したやることをまとめて確認できる

## 構成

| ファイル | 役割 |
|---|---|
| `app.py` | Flask 本体（ページとルーティング） |
| `sheets.py` | Google スプレッドシートへの読み書き |
| `templates/` | 画面（一覧・登録/編集フォーム） |

## セットアップ

### 1. ライブラリのインストール

```bash
cd "Todo リストアプリ"
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

### 3. 起動

```bash
python3 app.py
```

ブラウザで http://localhost:5000 を開きます。

## 環境変数（任意）

| 変数 | デフォルト | 説明 |
|---|---|---|
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | 認証 JSON のパス |
| `SPREADSHEET_NAME` | `TodoApp` | 使用するスプレッドシートの名前 |

## 注意

`credentials.json` は秘密情報です。`.gitignore` で git にコミットされないように
してあります。絶対に公開しないでください。
