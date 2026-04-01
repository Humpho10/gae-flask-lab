from datetime import datetime, timezone
from threading import Lock
import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

TASKS: list[dict[str, object]] = []
TASK_ID = 1
TASKS_LOCK = Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def task_counts() -> tuple[int, int]:
    total = len(TASKS)
    completed = sum(1 for task in TASKS if task["done"])
    return total, completed


@app.get("/")
def home() -> str:
    session["visits"] = int(session.get("visits", 0)) + 1
    total, completed = task_counts()
    return render_template(
        "index.html",
        current_time=utc_now(),
        visits=session["visits"],
        tasks=TASKS,
        total_tasks=total,
        completed_tasks=completed,
        pending_tasks=total - completed,
    )


@app.post("/tasks")
def add_task():
    global TASK_ID
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("home"))

    with TASKS_LOCK:
        TASKS.append(
            {
                "id": TASK_ID,
                "title": title,
                "done": False,
                "created_at": utc_now(),
            }
        )
        TASK_ID += 1

    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id: int):
    with TASKS_LOCK:
        for task in TASKS:
            if task["id"] == task_id:
                task["done"] = not bool(task["done"])
                break

    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id: int):
    with TASKS_LOCK:
        for index, task in enumerate(TASKS):
            if task["id"] == task_id:
                TASKS.pop(index)
                break

    return redirect(url_for("home"))


@app.get("/api/stats")
def api_stats() -> tuple[dict[str, object], int]:
    total, completed = task_counts()
    payload = {
        "server_time": utc_now(),
        "visits": int(session.get("visits", 0)),
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": total - completed,
    }
    return jsonify(payload), 200


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


if __name__ == "__main__":
    # Local development server
    app.run(host="127.0.0.1", port=8080, debug=True)
