# アプリ名：
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 予定を入れるリスト（簡易的にメモリに保存）
events = [
    {"title": "朝の薬", "start": "2025-08-25"},
    {"title": "夜の薬", "start": "2025-08-26"},
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form["title"]
        date = request.form["date"]
        events.append({"title": title, "start": date})
        return redirect(url_for("index"))  # ページを更新

    return render_template("index.html", events=events)


if __name__ == "__main__":
    app.run(debug=True)
