# 薬リマインダー

家族への薬の飲み忘れ防止通知をLINEに送信するツールです。

毎日朝・夜の2回、GitHub Actions が自動で実行し、飲んだことを確認するボタン付きメッセージをLINEに届けます。確認ボタンを押すと、家族全員に「飲みました」と通知が届きます。

## ファイル構成

```
medicine-reminder/
├── config/
│   └── medicines.yaml    # 薬の種類・タイミング設定
├── src/
│   ├── main.py           # 通知送信スクリプト
│   └── server.py         # LINE Webhook サーバー
└── requirements.txt
```

## 設定方法

`config/medicines.yaml` を編集して薬の情報を管理します。

```yaml
medicines:
  - name: "薬の名前"
    timing:
      - morning   # 朝に通知
      - evening   # 夜に通知
    note: "食後に服用"  # 備考（省略可）
```

`timing` には `morning`（朝8時）と `evening`（夜21時）を指定できます。

## 環境変数

| 変数名 | 説明 |
|--------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot のチャンネルアクセストークン |
| `LINE_CHANNEL_SECRET` | LINE Bot のチャンネルシークレット |
| `LINE_USER_ID` | 通知先のLINEユーザーID |
| `LINE_FAMILY_IDS` | 確認通知の送信先ID（複数の場合はカンマ区切り） |

GitHub Actions で実行する場合は、リポジトリの Secrets に上記を登録してください。

### GitHub Secrets に登録する方法

リポジトリの **Settings → Secrets and variables → Actions → New repository secret** で以下の 4 つを登録：

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `LINE_USER_ID`
- `LINE_FAMILY_IDS`

## セットアップ手順

### 1. LINE Messaging API の設定

1. [LINE Developers](https://developers.line.biz) にアクセスしてログイン
2. 「プロバイダー」→「作成」で新しいプロバイダーを作成
3. 「Messaging API」チャンネルを新規作成
4. チャンネル設定の「Messaging API」タブ →「チャンネルアクセストークン（長期）」を発行してコピー
5. 「チャンネル基本設定」タブ →「チャンネルシークレット」をコピー
6. 作成したボットを LINE アプリで友だち追加
7. ボットにメッセージを送ると、自分の LINE ユーザー ID が返信されるので控えておく

### 2. Render へのデプロイ（確認ボタン用）

確認ボタンを押したときに家族へ通知を届けるため、Webhook サーバーを Render にデプロイします。

1. [Render](https://render.com) にアクセスしてアカウント作成
2. 「New → Web Service」でこのリポジトリを接続
3. 以下の環境変数を Render の「Environment」タブに登録：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `LINE_FAMILY_IDS`
4. デプロイ完了後、発行された URL（例：`https://medicine-reminder-xxxx.onrender.com`）をコピー

### 3. LINE の Webhook URL を設定

1. LINE Developers のチャンネル設定 →「Messaging API」タブ
2. 「Webhook URL」に Render の URL + `/webhook` を入力（例：`https://medicine-reminder-xxxx.onrender.com/webhook`）
3. 「検証」ボタンで接続確認

### 4. GitHub Secrets に登録

上記「GitHub Secrets に登録する方法」の手順で 4 つの Secrets を登録。

### 5. 動作確認（手動実行）

GitHub の「Actions」→「Medicine Reminder」→「Run workflow」で今すぐ実行して LINE に届くか確認できます。

## ローカルでの実行

```bash
cd medicine-reminder
pip install -r requirements.txt

# 通知を手動送信
python src/main.py

# 時間帯を指定して実行
TIME_OF_DAY=morning python src/main.py
TIME_OF_DAY=evening python src/main.py
```

## 自動実行スケジュール

GitHub Actions により以下のスケジュールで自動実行されます。

| 時間帯 | 実行時刻（JST） |
|--------|----------------|
| 朝 | 毎日 8:00 |
| 夜 | 毎日 21:00 |
