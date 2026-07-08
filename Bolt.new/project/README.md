# AI Chat（Bolt.new × Dify）

Bolt.new で生成した React + Vite 製のチャット画面に、[Dify](https://dify.ai/) のAPIを連携させたAIチャットアプリです。

## 機能

- **チャットUI** — ユーザー/AIの吹き出し表示、タイピングインジケーター
- **Dify API連携** — 送信したメッセージをDifyのアプリに渡し、AIの回答を表示
- **会話履歴の保持** — Difyの `conversation_id` を引き継ぎ、文脈を保った会話ができる
- **エラーハンドリング** — 通信に失敗した場合はチャット画面にエラーメッセージを表示
- **APIキーの保護** — Difyの認証情報はサーバーレス関数（`api/chat.ts`）でのみ使用し、ブラウザには一切渡らない構成

## 構成

| ファイル/ディレクトリ | 役割 |
|---|---|
| `src/App.tsx` | チャット画面のUIと送信処理 |
| `api/chat.ts` | Difyへのリクエストを中継するサーバーレス関数（Vercel） |

フロントエンドは `/api/chat` を叩き、`api/chat.ts` がサーバー側で `DIFY_API_KEY` を使ってDify本体（`chat-messages` エンドポイント）を呼び出します。APIキーはこの中継役より外（ブラウザ）には出ません。

## セットアップ

### 1. ライブラリのインストール

```bash
cd project
npm install
```

### 2. Dify APIキーの準備

1. [Dify](https://dify.ai/) でチャットボット用のアプリを作成
2. アプリの「APIアクセス」ページで **Base URL** と **API Secret Key** を確認
3. `.env.example` を `.env` にコピーし、値を書き換える

```bash
cp .env.example .env
```

```
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=（発行されたAPI Secret Key）
```

> `.env` は `.gitignore` 対象なので、実際のAPIキーがGitに載ることはありません。

### 3. 起動

```bash
npm run dev
```

表示されたURL（例: `http://localhost:5173`）をブラウザで開くとチャット画面が表示されます。

> ローカルの `npm run dev`（Vite単体）では `api/chat.ts` は動きません。フロントエンドの見た目だけを確認する分には問題ありませんが、実際にDifyと通信するところまで手元で確認したい場合は [Vercel CLI](https://vercel.com/docs/cli) の `vercel dev` を使ってください。

## デプロイ（Vercel）

1. このリポジトリをVercelにインポート（Root Directoryは `Bolt.new/project` を指定）
2. Vercelのプロジェクト設定 → Environment Variables に `DIFY_API_URL` / `DIFY_API_KEY` を追加
3. デプロイ

`api/` ディレクトリはVercelが自動でサーバーレス関数として認識します。追加の設定ファイルは不要です。
