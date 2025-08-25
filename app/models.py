from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

db = SQLAlchemy()

class MedicineSchedule(db.Model):
    __tablename__ = "medicine_schedule"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)      # 薬名
    pills = db.Column(db.Integer, nullable=False)         # 何錠
    time = db.Column(db.String(5), nullable=False)        # 服用時刻 "HH:MM"
    start_date = db.Column(db.Date, nullable=False)       # 服用開始日
    end_date = db.Column(db.Date, nullable=False)         # 服用終了日

    def __repr__(self):
        return f"<Schedule {self.name} {self.pills}錠 at {self.time} ({self.start_date}~{self.end_date})>"

class DoseLog(db.Model):
    __tablename__ = "dose_log"
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("medicine_schedule.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)             # 服用対象日
    taken = db.Column(db.Boolean, default=False, nullable=False)

    schedule = db.relationship("MedicineSchedule", backref="dose_logs", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("schedule_id", "date", name="uq_schedule_date"),
    )
