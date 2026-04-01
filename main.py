from datetime import datetime, timezone
from pathlib import Path
import logging
import os
import sqlite3
from threading import Lock
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover - fallback for local dev if package is missing
    psycopg2 = None
    RealDictCursor = None


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.config["DATABASE_URL"] = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'tasks.db'}")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
app.logger.setLevel(logging.INFO)

DB_LOCK = Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _normalize_database_url() -> str:
    database_url = app.config["DATABASE_URL"]
    if database_url.startswith("postgres://"):
        return "postgresql://" + database_url[len("postgres://") :]
    return database_url


def _database_backend() -> str:
    database_url = _normalize_database_url()
    return "postgresql" if database_url.startswith("postgresql://") else "sqlite"


def _open_database_connection() -> tuple[str, Any]:
    backend = _database_backend()
    database_url = _normalize_database_url()

    if backend == "postgresql":
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary is not installed")
        connection = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return backend, connection

    sqlite_path = database_url.replace("sqlite:///", "", 1)
    connection = sqlite3.connect(sqlite_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return backend, connection


def _initialize_database() -> None:
    schema_sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done BOOLEAN NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """

    with DB_LOCK:
        backend, connection = _open_database_connection()
        try:
            cursor = connection.cursor()
            if backend == "postgresql":
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TEXT NOT NULL
                    )
                    """
                )
            else:
                cursor.execute(schema_sql)
            connection.commit()
        finally:
            connection.close()


def _fetch_tasks() -> list[dict[str, Any]]:
    backend, connection = _open_database_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, title, done, created_at FROM tasks ORDER BY id DESC")
        rows = cursor.fetchall()
        tasks: list[dict[str, Any]] = []
        for row in rows:
            if backend == "postgresql":
                task = {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "done": bool(row["done"]),
                    "created_at": str(row["created_at"]),
                }
            else:
                task = {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "done": bool(row["done"]),
                    "created_at": str(row["created_at"]),
                }
            tasks.append(task)
        return tasks
    finally:
        connection.close()


def task_counts() -> tuple[int, int]:
    tasks = _fetch_tasks()
    total = len(tasks)
    completed = sum(1 for task in tasks if task["done"])
    return total, completed


def _database_flags() -> dict[str, object]:
    return {
        "database_configured": bool(os.environ.get("DATABASE_URL")),
        "secret_key_loaded": bool(os.environ.get("FLASK_SECRET_KEY")),
        "database_backend": _database_backend(),
    }


@app.get("/")
def home() -> str:
    session["visits"] = int(session.get("visits", 0)) + 1
    tasks = _fetch_tasks()
    total, completed = task_counts()
    return render_template(
        "index.html",
        current_time=utc_now(),
        visits=session["visits"],
        tasks=tasks,
        total_tasks=total,
        completed_tasks=completed,
        pending_tasks=total - completed,
        **_database_flags(),
    )


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("home"))

    with DB_LOCK:
        backend, connection = _open_database_connection()
        try:
            cursor = connection.cursor()
            if backend == "postgresql":
                cursor.execute(
                    "INSERT INTO tasks (title, done, created_at) VALUES (%s, %s, %s)",
                    (title, False, utc_now()),
                )
            else:
                cursor.execute(
                    "INSERT INTO tasks (title, done, created_at) VALUES (?, ?, ?)",
                    (title, 0, utc_now()),
                )
            connection.commit()
        finally:
            connection.close()

    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id: int):
    with DB_LOCK:
        backend, connection = _open_database_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT done FROM tasks WHERE id = %s" if backend == "postgresql" else "SELECT done FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is not None:
                current_done = bool(row["done"] if backend == "postgresql" else row[0])
                new_done = not current_done
                cursor.execute(
                    "UPDATE tasks SET done = %s WHERE id = %s" if backend == "postgresql" else "UPDATE tasks SET done = ? WHERE id = ?",
                    (new_done, task_id) if backend == "postgresql" else (1 if new_done else 0, task_id),
                )
                connection.commit()
        finally:
            connection.close()

    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id: int):
    with DB_LOCK:
        backend, connection = _open_database_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM tasks WHERE id = %s" if backend == "postgresql" else "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )
            connection.commit()
        finally:
            connection.close()

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
        **_database_flags(),
    }
    return jsonify(payload), 200


@app.get("/config")
def config_status() -> tuple[dict[str, object], int]:
    return jsonify(_database_flags()), 200


@app.get("/debug/raise")
def debug_raise() -> tuple[dict[str, str], int]:
    app.logger.error("Intentional debug error triggered for Railway log demonstration")
    raise RuntimeError("Intentional Railway logging demo error")


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


if __name__ == "__main__":
    # Local development server
    _initialize_database()
    app.run(host="127.0.0.1", port=8080, debug=True)


_initialize_database()
