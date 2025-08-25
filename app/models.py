from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 薬の名前
    time = db.Column(db.String(10), nullable=False)   # 時間（例: 08:00）

    def __repr__(self):
        return f"<Medicine {self.name} at {self.time}>"
