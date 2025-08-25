from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

# 処方スケジュール（薬名・錠数・服用時刻・期間）
class MedicineSchedule(db.Model):
    __tablename__ = "medicine_schedule"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)   # 薬名
    pills = db.Column(db.Integer, nullable=False)      # 錠数
    time = db.Column(db.String(5), nullable=False)     # "HH:MM"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    dose_logs = db.relationship("DoseLog", backref="schedule", lazy=True)

    def __repr__(self):
        return f"<Schedule {self.name} {self.pills}錠 {self.time} {self.start_date}~{self.end_date}>"

# 服用ログ（各日付について服用済みかどうか）
class DoseLog(db.Model):
    __tablename__ = "dose_log"
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("medicine_schedule.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)                 # その日の分
    taken = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("schedule_id", "date", name="uq_schedule_date"),
    )

    def __repr__(self):
        return f"<DoseLog sid={self.schedule_id} {self.date} taken={self.taken}>"
