# 週間献立 LINE 通知

毎週日曜日の朝 8:00 に、Claude AI が生成した 1 週間分の夕食献立を LINE に自動送信するツール。  
食材費の週予算は **6,500円** を基準に献立を提案します。

## 仕組み

1. GitHub Actions が毎週日曜 8:00 (JST) に自動起動
2. Claude API が予算内の今週の献立を生成
3. LINE Messaging API でメッセージを送信

## 環境変数

機密情報はすべて環境変数で管理します。コードへの直書きは禁止です。

| 変数名 | 内容 | 取得先 |
|--------|------|--------|
| `ANTHROPIC_API_KEY` | Anthropic API キー | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャンネルアクセストークン（長期） | LINE Developers → Messaging API タブ |
| `LINE_USER_ID` | 自分の LINE ユーザー ID | LINE Developers → Your user ID |

### ローカルで動かす場合

`.env.example` をコピーして `.env` を作成し、値を記入します。

```bash
cp meal-planner/.env.example meal-planner/.env
# .env をエディタで開いて各値を入力
```

> `.env` は `.gitignore` に登録済みです。絶対に Git にコミットしないでください。

### GitHub Actions で動かす場合（本番）

リポジトリの **Settings → Secrets and variables → Actions → New repository secret** で以下の 3 つを登録：

- `ANTHROPIC_API_KEY`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`

## セットアップ手順

### 1. Anthropic API キーを取得

1. [console.anthropic.com](https://console.anthropic.com) でアカウント作成
2. 「API Keys」→「Create Key」でキーを発行してコピー

### 2. LINE Messaging API の設定

1. [LINE Developers](https://developers.line.biz) にアクセスしてログイン
2. 「プロバイダー」→「作成」で新しいプロバイダーを作成
3. 「Messaging API」チャンネルを新規作成
4. チャンネル設定の「Messaging API」タブ →「チャンネルアクセストークン（長期）」を発行してコピー
5. 作成したボットを LINE アプリで友だち追加
6. LINE Developers の「Your user ID」欄に表示されているユーザー ID をコピー

### 3. GitHub Secrets に登録

上記「GitHub Actions で動かす場合」の手順で 3 つの Secrets を登録。

### 4. 動作確認（手動実行）

GitHub の「Actions」→「Weekly Meal Plan」→「Run workflow」で今すぐ実行して LINE に届くか確認できます。

## ファイル構成

```
meal-planner/
├── src/
│   └── main.py          # メインスクリプト
├── .env.example         # 環境変数のテンプレート（値は空）
├── requirements.txt     # Python パッケージ
└── README.md
.github/
└── workflows/
    └── weekly-meal-plan.yml  # GitHub Actions 設定（毎週日曜 8:00 JST）
.gitignore               # .env を Git 管理対象外に設定
```
