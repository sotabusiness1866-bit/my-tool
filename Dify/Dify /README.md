# Dify LINE チャットボット

Dify で作成したチャットボットを LINE 上で利用できるようにする連携ツールです。LINEで送ったメッセージを Dify の Chat API に転送し、返ってきた回答をそのままLINEに返信します。

## ファイル構成

```
Dify/
├── src/
│   └── server.py     # LINE Webhook サーバー（Dify API 連携）
├── requirements.txt
└── .env.example
```

## 仕組み

1. LINEでユーザーがメッセージを送信
2. LINEがこのサーバーの `/webhook` にイベントを送信
3. サーバーが署名を検証し、メッセージ本文を Dify の `/chat-messages` API に送信
4. Dify から返ってきた回答を LINE の Reply API でそのまま返信

会話の文脈（`conversation_id`）はLINEユーザーIDごとにサーバーのメモリ上で保持します。サーバーが再起動すると会話履歴はリセットされ、次のメッセージから新しい会話として扱われます（Renderの無料プランはアイドル時にスリープ・再起動するため、利用頻度によっては履行が途切れる場合があります）。

## 環境変数

| 変数名 | 説明 |
|--------|------|
| `DIFY_API_KEY` | Dify アプリの APIキー |
| `DIFY_API_BASE_URL` | Dify API のベースURL（Dify Cloudなら変更不要。セルフホストなら自分の環境のURLに変更） |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot のチャンネルアクセストークン |
| `LINE_CHANNEL_SECRET` | LINE Bot のチャンネルシークレット |

## セットアップ手順

### 1. Dify でチャットボットを作成

1. [Dify](https://cloud.dify.ai)（セルフホストの場合は自分の環境）にログイン
2. 「スタジオ」から「最初から作成」→ アプリタイプ「チャットボット」を選択して作成
3. 必要に応じてプロンプト・モデル・知識ベースなどを設定し、公開する
4. アプリ画面左メニューの「APIアクセス」→「APIキー」から新しいキーを発行してコピー（`DIFY_API_KEY`）
5. セルフホストの場合は、API画面に表示されているベースURLも控える（`DIFY_API_BASE_URL`）

### 2. LINE Messaging API の設定

1. [LINE Developers](https://developers.line.biz) にアクセスしてログイン
2. 「プロバイダー」→「作成」で新しいプロバイダーを作成（既にある場合は不要）
3. 「Messaging API」チャンネルを新規作成
4. チャンネル設定の「Messaging API」タブ →「チャンネルアクセストークン（長期）」を発行してコピー（`LINE_CHANNEL_ACCESS_TOKEN`）
5. 「チャンネル基本設定」タブ →「チャンネルシークレット」をコピー（`LINE_CHANNEL_SECRET`）
6. 「Messaging API」タブで「応答メッセージ」をオフ、「Webhookの利用」をオンにする
7. 作成したボットを LINE アプリで友だち追加しておく

### 3. Render へデプロイ

1. [Render](https://render.com) にアクセスしてアカウント作成・このリポジトリを接続
2. 「New → Web Service」を選択し、このリポジトリを選択
3. 設定項目を以下のように入力：
   - **Root Directory**: `Dify`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`
4. 「Environment」タブで以下の環境変数を登録：
   - `DIFY_API_KEY`
   - `DIFY_API_BASE_URL`（Dify Cloudなら `https://api.dify.ai/v1`）
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
5. デプロイ完了後、発行されたURL（例：`https://dify-line-bot-xxxx.onrender.com`）をコピー

### 4. LINE の Webhook URL を設定

1. LINE Developers のチャンネル設定 →「Messaging API」タブ
2. 「Webhook URL」に Render の URL + `/webhook` を入力（例：`https://dify-line-bot-xxxx.onrender.com/webhook`）
3. 「検証」ボタンで接続確認（`{"status":"ok"}` 系の応答が返れば成功）

### 5. 動作確認

LINEアプリでボットにメッセージを送ると、Difyの回答が返信されます。

## ローカルでの実行

```bash
cd "Dify"
pip install -r requirements.txt
cp .env.example .env  # 値を編集して入力
uvicorn src.server:app --reload
```

ローカルでLINEからのWebhookを受け取るには、ngrok等でトンネルを張り、そのURLをLINEのWebhook URLに設定してください。
