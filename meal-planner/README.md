# 週間献立 LINE 通知

毎週日曜日の朝 8:00 に、Claude AI が生成した 1 週間分の夕食献立を LINE に自動送信するツール。

## 仕組み

1. GitHub Actions が毎週日曜 8:00 (JST) に自動起動
2. Claude API が今週の献立を生成
3. LINE Messaging API でメッセージを送信

## セットアップ手順

### 1. Anthropic API キーを取得

1. [console.anthropic.com](https://console.anthropic.com) にアクセスしてアカウント作成
2. 「API Keys」から新しいキーを発行してコピー

### 2. LINE Messaging API の設定

1. [LINE Developers](https://developers.line.biz) にアクセスしてログイン
2. 「プロバイダー」→「作成」で新しいプロバイダーを作る
3. 「Messaging API」チャンネルを新規作成
4. チャンネル設定の「Messaging API」タブ →「チャンネルアクセストークン（長期）」を発行してコピー
5. 作成したボットを LINE アプリで友だち追加する
6. LINE Developers の「Your user ID」欄に表示されている自分のユーザー ID をコピー

### 3. GitHub Secrets に登録

リポジトリの Settings → Secrets and variables → Actions → 「New repository secret」で以下の 3 つを登録：

| 名前 | 内容 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic のAPIキー |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャンネルアクセストークン |
| `LINE_USER_ID` | 自分の LINE ユーザー ID |

### 4. 動作確認（手動実行）

GitHub のリポジトリページ →「Actions」→「Weekly Meal Plan」→「Run workflow」で今すぐ実行して LINE に届くか確認できます。

## ファイル構成

```
meal-planner/
├── src/
│   └── main.py          # メインスクリプト
├── requirements.txt     # Python パッケージ
└── README.md
.github/
└── workflows/
    └── weekly-meal-plan.yml  # GitHub Actions 設定
```
