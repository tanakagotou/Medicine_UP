import os
from flask import Flask

def create_app():
    # __file__ = app/__init__.py のパス
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static")
    )

    from . import routes
    return app
