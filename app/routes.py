from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, date, timedelta
from .models import db, MedicineSchedule, DoseLog

main = Blueprint("main", __name__)

@main.get("/")
def index():
    return render_template("index.html")

# FullCalendar向け：表示範囲のイベントを返す
@main.get("/api/events")
def api_events():
    # ISO文字列で来る start/end を日付に
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    start = datetime.fromisoformat(start_str).date() if start_str else date.today()
    end = datetime.fromisoformat(end_str).date() if end_str else start

    events = []
    schedules = MedicineSchedule.query.all()

    for sch in schedules:
        d = max(start, sch.start_date)
        last = min(end, sch.end_date)
        while d <= last:
            # 服用ログ有無で taken を決定
            log = DoseLog.query.filter_by(schedule_id=sch.id, date=d).first()
            taken = log.taken if log else False

            title = f"{sch.name}（{sch.pills}錠） {sch.time}" + (" ✅" if taken else "")
            events.append({
                "id": f"{sch.id}:{d.isoformat()}",
                "title": title,
                "start": f"{d.isoformat()}T{sch.time}:00",
                "allDay": False,
                "extendedProps": {
                    "schedule_id": sch.id,
                    "date": d.isoformat(),
                    "taken": taken,
                }
            })
            d += timedelta(days=1)

    return jsonify(events)

# 処方の登録
@main.post("/api/schedule")
def api_schedule():
    data = request.get_json()
    sch = MedicineSchedule(
        name=data["name"].strip(),
        pills=int(data["pills"]),
        time=data["time"],  # "HH:MM"
        start_date=date.fromisoformat(data["start_date"]),
        end_date=date.fromisoformat(data["end_date"]),
    )
    db.session.add(sch)
    db.session.commit()
    return jsonify({"ok": True, "id": sch.id})

# 服用チェックのトグル（保存される！）
@main.post("/api/toggle_taken")
def api_toggle_taken():
    data = request.get_json()
    schedule_id = int(data["schedule_id"])
    d = date.fromisoformat(data["date"])

    log = DoseLog.query.filter_by(schedule_id=schedule_id, date=d).first()
    if log is None:
        log = DoseLog(schedule_id=schedule_id, date=d, taken=True)  # 初タップは True で作成
        db.session.add(log)
    else:
        log.taken = not log.taken

    db.session.commit()
    return jsonify({"ok": True, "taken": log.taken})
