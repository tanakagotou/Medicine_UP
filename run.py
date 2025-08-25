from app import create_app

# Flaskアプリ（アプリ工場パターン）
app = create_app()

if __name__ == "__main__":
    # 開発用サーバー起動
    app.run(debug=True)
