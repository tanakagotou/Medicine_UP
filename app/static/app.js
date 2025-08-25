// app/static/app.js
document.addEventListener("DOMContentLoaded", () => {
  // ===== モーダル（<dialog>） =====
  const dialog = document.getElementById("formDialog");
  const openBtn = document.getElementById("open-form");
  const cancelBtn = document.getElementById("cancelForm");
  const form = document.getElementById("scheduleForm");

  if (openBtn) openBtn.addEventListener("click", () => dialog.showModal());
  if (cancelBtn) cancelBtn.addEventListener("click", () => dialog.close());

  // ===== FullCalendar =====
  const calendarEl = document.getElementById("calendar");

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "ja",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: ""
    },
    titleFormat: { year: "numeric", month: "long" },
    expandRows: true,
    contentHeight: "auto",

    // イベント取得
    eventSources: [{ url: "/api/events" }],

    // 服用済みなら "is-taken" クラス、未服用なら "is-not-taken" クラスを付与
    eventClassNames: (arg) => {
      return arg.event.extendedProps?.taken ? ["is-taken"] : ["is-not-taken"];
    },

    // タイトル末尾に ✅ を付け外し（サーバー側でも付けていますが、即時反映用）
    eventDidMount: (info) => {
      const taken = !!info.event.extendedProps?.taken;
      const title = info.event.title || "";
      const hasCheck = title.endsWith(" ✅");
      if (taken && !hasCheck) info.event.setProp("title", title + " ✅");
      if (!taken && hasCheck) info.event.setProp("title", title.replace(/\s✅$/, ""));
    },

    // 日付クリック → その日でフォーム初期化
    dateClick: (info) => {
      if (!form) return;
      form.reset();
      form.elements["start_date"].value = info.dateStr;
      form.elements["end_date"].value = info.dateStr;
      dialog.showModal();
    },

    // イベントクリック → 服用済みトグル
    eventClick: async (info) => {
      const ext = info.event.extendedProps;
      if (!ext || ext.schedule_id == null || !ext.date) return;

      const res = await fetch("/api/toggle_taken", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ schedule_id: ext.schedule_id, date: ext.date })
      }).then((r) => r.json()).catch(() => null);

      if (!res || !res.ok) return;

      // 即時に見た目を更新（再取得しなくても反映されるように）
      const nextTaken = !!res.taken;

      // extendedProps を更新
      info.event.setExtendedProp("taken", nextTaken);

      // クラス切り替え
      if (info.el) {
        info.el.classList.toggle("is-taken", nextTaken);
        info.el.classList.toggle("is-not-taken", !nextTaken);
      }

      // タイトルの ✅ を同期
      const baseTitle = (info.event.title || "").replace(/\s✅$/, "");
      info.event.setProp("title", nextTaken ? baseTitle + " ✅" : baseTitle);
    },
  });

  calendar.render();

  // ===== 追加フォーム送信：処方登録 =====
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        name: form.elements["name"].value.trim(),
        pills: form.elements["pills"].value,
        time: form.elements["time"].value,
        start_date: form.elements["start_date"].value,
        end_date: form.elements["end_date"].value,
      };
      if (!payload.name || !payload.time || !payload.start_date || !payload.end_date) {
        alert("未入力の項目があります。");
        return;
      }
      const res = await fetch("/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then((r) => r.json()).catch(() => null);

      if (res && res.ok) {
        dialog.close();
        // 新規追加は再取得で反映
        calendar.refetchEvents();
      } else {
        alert("保存に失敗しました。");
      }
    });
  }

  // ===== 服用時刻になったら通知（ページを開いている間） =====
  const alarm = document.getElementById("alarm");
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }

  const notifyIfDue = () => {
    const events = calendar.getEvents();
    if (!events.length) return;
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const d = String(now.getDate()).padStart(2, "0");
    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const target = `${y}-${m}-${d}T${hh}:${mm}`;

    for (const ev of events) {
      const s = ev.start;
      if (!s) continue;
      const stamp =
        `${s.getFullYear()}-${String(s.getMonth() + 1).padStart(2, "0")}` +
        `-${String(s.getDate()).padStart(2, "0")}T${String(s.getHours()).padStart(2, "0")}` +
        `:${String(s.getMinutes()).padStart(2, "0")}`;

      const taken = !!ev.extendedProps?.taken;
      if (stamp === target && !taken) {
        try { if (alarm) { alarm.currentTime = 0; alarm.play(); } } catch (_) {}
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("服用時間になりました", { body: ev.title });
        }
      }
    }
  };

  const startTicker = () => {
    const now = new Date();
    const msToNextMinute = (60 - now.getSeconds()) * 1000 - now.getMilliseconds();
    setTimeout(() => {
      notifyIfDue();
      setInterval(notifyIfDue, 60 * 1000);
    }, Math.max(0, msToNextMinute));
  };
  startTicker();
});
