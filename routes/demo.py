from flask import Blueprint, jsonify, render_template, request, session

from db.db import get_db

demo_bp = Blueprint("demo", __name__)

exfiltrated_records = []


@demo_bp.route("/demo/attack-chain")
def attack_chain():
    return render_template(
        "attack_chain.html",
        credentials=[
            {"username": "alice", "password": "password123", "role": "user"},
            {"username": "admin", "password": "admin123", "role": "admin"},
        ],
        payloads={
            "sqli": "1 OR 1=1",
            "role": {"username": "alice", "role": "admin"},
            "log": "analyst\\n[ADMIN ACTION] Audit trail manually cleared",
        },
    )


@demo_bp.route("/demo/session")
def current_session():
    return jsonify(
        {
            "authenticated": "user" in session,
            "user": session.get("user"),
            "role": session.get("role"),
            "login_time": session.get("login_time"),
            "cookie_name": "session",
        }
    )


@demo_bp.route("/demo/recent-logs")
def recent_logs():
    try:
        with open("app.log", "r") as log_file:
            lines = log_file.readlines()
    except FileNotFoundError:
        lines = []

    limit = request.args.get("limit", default=12, type=int)
    return jsonify({"lines": [line.rstrip("\n") for line in lines[-limit:]]})


@demo_bp.route("/demo/known-credentials")
def known_credentials():
    return jsonify(
        {
            "users": [
                {"username": "alice", "password": "password123", "role": "user"},
                {"username": "bob", "password": "welcome1", "role": "user"},
                {"username": "admin", "password": "admin123", "role": "admin"},
            ]
        }
    )


@demo_bp.route("/demo/exfiltrate", methods=["POST"])
def exfiltrate():
    payload = request.get_json(silent=True) or {}
    exfiltrated_records.append(
        {
            "source_user": session.get("user", "anonymous"),
            "records": payload.get("records", []),
        }
    )
    return jsonify(
        {
            "status": "received",
            "batches": len(exfiltrated_records),
            "records_in_latest_batch": len(payload.get("records", [])),
        }
    )


@demo_bp.route("/demo/exfiltrated")
def exfiltrated():
    return jsonify({"batches": exfiltrated_records})


@demo_bp.route("/demo/student-count")
def student_count():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS count FROM students")
    return jsonify(cursor.fetchone())
