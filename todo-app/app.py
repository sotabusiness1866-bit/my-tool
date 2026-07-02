"""Todo リストアプリ (Flask + Google スプレッドシート)。

機能:
    - やることの登録・編集 (タイトル・内容・期日・優先度)
    - 登録したやることの一覧表示 (未完了かつ優先度の高い順)
    - チェックボックスによる完了・未完了の切り替え
"""

from flask import Flask, flash, redirect, render_template, request, url_for

import sheets

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


@app.route("/")
def index():
    """やること一覧ページ。"""
    todos = sheets.list_todos()
    return render_template("index.html", todos=todos)


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
    app.run(debug=True, port=5000)
