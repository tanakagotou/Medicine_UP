from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, date, timedelta
from .models import db, MedicineSchedule, DoseLog

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

# FullCalendar が期間指定で叩くイベントAPI
@main.get("/api/events")
def api_events():
    # FullCalendarはISO文字列でstart/endを渡してくる
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    # 文字列→date
    start = datetime.fromisoformat(start_str).date() if start_str else date.today()
    end = datetime.fromisoformat(end_str).date() if end_str else start

    events = []

    schedules = MedicineSchedule.query.all()
    for sch in schedules:
        # 期間の交差部分のみ走査
        d = max(start, sch.start_date)
        last = min(end, sch.end_date)
        while d <= last:
            # その日のイベント（titleは「薬名（n錠）」）
            title = f"{sch.name}（{sch.pills}錠） {sch.time}"
            # 服用チェックの取得（なければ自動生成はしない＝クリック時に作る運用にして軽量化）
            dose = DoseLog.query.filter_by(schedule_id=sch.id, date=d).first()
            taken = dose.taken if dose else False
            events.append({
                "id": f"{sch.id}:{d.isoformat()}",
                "title": title + (" ✅" if taken else ""),
                "start": f"{d.isoformat()}T{sch.time}:00",  # 時刻つきで表示
                "allDay": False,
                "extendedProps": {
                    "schedule_id": sch.id,
                    "date": d.isoformat(),
                    "taken": taken,
                }
            })
            d += timedelta(days=1)

    return jsonify(events)

# スケジュール新規登録
@main.post("/api/schedule")
def api_schedule():
    data = request.get_json()
    name = data["name"].strip()
    pills = int(data["pills"])
    time = data["time"]              # "HH:MM"
    start_date = date.fromisoformat(data["start_date"])
    end_date = date.fromisoformat(data["end_date"])

    sch = MedicineSchedule(
        name=name, pills=pills, time=time,
        start_date=start_date, end_date=end_date
    )
    db.session.add(sch)
    db.session.commit()
    return jsonify({"ok": True, "id": sch.id})

# 服用済みトグル
@main.post("/api/toggle_taken")
def api_toggle_taken():
    data = request.get_json()
    schedule_id = int(data["schedule_id"])
    d = date.fromisoformat(data["date"])

    dose = DoseLog.query.filter_by(schedule_id=schedule_id, date=d).first()
    if dose is None:
        dose = DoseLog(schedule_id=schedule_id, date=d, taken=True)
        db.session.add(dose)
    else:
        dose.taken = not dose.taken

    db.session.commit()
    return jsonify({"ok": True, "taken": dose.taken})
