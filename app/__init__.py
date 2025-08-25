# app/__init__.py
import os
from flask import Flask
from .models import db

def create_app():
    app_dir = os.path.dirname(__file__)                 # .../app
    proj_root = os.path.dirname(app_dir)                # プロジェクト直下

    app = Flask(
        __name__,
        template_folder=os.path.join(proj_root, "templates"),  # ← ここをプロジェクト直下に
        static_folder=os.path.join(app_dir, "static"),         # 静的は app/static
    )

    # --- DB 設定（必要ならそのまま） ---
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app_dir, "medicine.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_AS_ASCII"] = False

    db.init_app(app)

    # ルーティング登録
    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
