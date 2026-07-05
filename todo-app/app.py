"""Todo リストアプリ (Flask + Google スプレッドシート)。

機能:
    - やることの登録・編集 (タイトル・内容・期日・優先度)
    - 登録したやることの一覧表示 (未完了かつ優先度の高い順)
    - チェックボックスによる完了・未完了の切り替え
    - Googleカレンダーとの連携 (OAuth 2.0)
"""

import os

from flask import Flask, flash, redirect, render_template, request, session, url_for

import calendar_service
import sheets

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


@app.route("/")
def index():
    """やること一覧ページ。"""
    todos = sheets.list_todos()
    return render_template(
        "index.html", todos=todos, calendar_connected=calendar_service.is_connected()
    )


@app.route("/new", methods=["GET", "POST"])
def new():
    """やることの新規登録ページ。"""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        due_date = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", sheets.DEFAULT_PRIORITY).strip()

        if not title:
            flash("タイトルは必須です。")
            return render_template("form.html", todo=request.form, action="new")
        if not sheets.validate_due_date(due_date):
            flash("期日は YYYY-MM-DD の形式で入力してください。")
            return render_template("form.html", todo=request.form, action="new")
        if not sheets.validate_priority(priority):
            flash("優先度は高・中・低のいずれかを選択してください。")
            return render_template("form.html", todo=request.form, action="new")

        sheets.add_todo(title, content, due_date, priority)
        flash("やることを登録しました。")
        return redirect(url_for("index"))

    return render_template("form.html", todo={}, action="new")


@app.route("/edit/<todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    """やることの編集ページ。"""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        due_date = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", sheets.DEFAULT_PRIORITY).strip()

        if not title:
            flash("タイトルは必須です。")
            return render_template("form.html", todo=request.form, action="edit")
        if not sheets.validate_due_date(due_date):
            flash("期日は YYYY-MM-DD の形式で入力してください。")
            return render_template("form.html", todo=request.form, action="edit")
        if not sheets.validate_priority(priority):
            flash("優先度は高・中・低のいずれかを選択してください。")
            return render_template("form.html", todo=request.form, action="edit")

        if not sheets.update_todo(todo_id, title, content, due_date, priority):
            flash("対象のやることが見つかりませんでした。")
            return redirect(url_for("index"))

        flash("やることを更新しました。")
        return redirect(url_for("index"))

    todo = sheets.get_todo(todo_id)
    if todo is None:
        flash("対象のやることが見つかりませんでした。")
        return redirect(url_for("index"))
    return render_template("form.html", todo=todo, action="edit")


@app.route("/stats")
def stats():
    """統計・分析ページ。"""
    return render_template("stats.html", stats=sheets.get_stats())


@app.route("/calendar/connect")
def calendar_connect():
    """Googleカレンダーの認可画面へリダイレクトする。"""
    redirect_uri = url_for("calendar_callback", _external=True)
    try:
        auth_url, state = calendar_service.get_authorization_url(redirect_uri)
    except FileNotFoundError:
        flash("OAuthクライアントの設定ファイルが見つかりません。管理者に設定を確認してください。")
        return redirect(url_for("index"))
    session["oauth_state"] = state
    return redirect(auth_url)


@app.route("/oauth2callback")
def calendar_callback():
    """Googleカレンダーの認可コードをトークンに交換する。"""
    redirect_uri = url_for("calendar_callback", _external=True)
    try:
        calendar_service.exchange_code(redirect_uri, session.get("oauth_state"), request.url)
        flash("Googleカレンダーと連携しました。")
    except Exception as e:
        print(f"[calendar] 認可コードの交換に失敗しました: {e}", flush=True)
        flash("Googleカレンダーとの連携に失敗しました。")
    return redirect(url_for("index"))


@app.route("/calendar/disconnect", methods=["POST"])
def calendar_disconnect():
    """Googleカレンダーとの連携を解除する。"""
    calendar_service.disconnect()
    flash("Googleカレンダーとの連携を解除しました。")
    return redirect(url_for("index"))


@app.route("/toggle/<todo_id>", methods=["POST"])
def toggle(todo_id):
    """やることの完了・未完了を切り替える。"""
    sheets.toggle_todo(todo_id)
    return redirect(url_for("index"))


@app.route("/delete/<todo_id>", methods=["POST"])
def delete(todo_id):
    """やることの削除。"""
    sheets.delete_todo(todo_id)
    flash("やることを削除しました。")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # ローカル開発では http://127.0.0.1 でOAuthコールバックを受けるため許可する。
    # 本番(Render等)はHTTPSで動作するためこの設定は影響しない。
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    app.run(debug=True, port=5000)
