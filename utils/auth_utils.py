import os
import re
import secrets
import time
from functools import wraps

from flask import flash, jsonify, redirect, session, url_for

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
ROLE_CHOICES = {"admin", "user"}
ALLOWED_UPLOAD_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}

MAX_FAILED_LOGINS = int(os.getenv("MAX_FAILED_LOGINS", "5"))
LOCKOUT_SECONDS = int(os.getenv("LOGIN_LOCKOUT_SECONDS", "600"))

_failed_login_tracker = {}


def validate_username(username):
    candidate = (username or "").strip()
    if not USERNAME_RE.fullmatch(candidate):
        raise ValueError("Username must be 3-30 characters and use letters, numbers, dot, underscore, or dash.")
    return candidate


def validate_password(password, *, signup=False):
    value = password or ""
    if signup:
        if len(value) < 8 or len(value) > 64:
            raise ValueError("Password must be between 8 and 64 characters.")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must include at least one letter and one number.")
    elif not value:
        raise ValueError("Password is required.")
    return value


def validate_role(role):
    value = (role or "").strip().lower()
    if value not in ROLE_CHOICES:
        raise ValueError("Role must be either admin or user.")
    return value


def parse_positive_int(value, field_name):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid integer.") from exc

    if parsed <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return parsed


def parse_marks(value):
    marks = parse_positive_int(value, "Marks")
    if marks > 100:
        raise ValueError("Marks must be between 1 and 100.")
    return marks


def allowed_upload(filename):
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_UPLOAD_EXTENSIONS


def _tracker_key(remote_addr, username):
    return f"{remote_addr or 'unknown'}::{username.lower()}"


def is_login_blocked(remote_addr, username):
    attempts = _failed_login_tracker.get(_tracker_key(remote_addr, username))
    if not attempts:
        return False, 0

    if attempts["count"] < MAX_FAILED_LOGINS:
        return False, 0

    elapsed = time.time() - attempts["last_attempt"]
    if elapsed >= LOCKOUT_SECONDS:
        _failed_login_tracker.pop(_tracker_key(remote_addr, username), None)
        return False, 0

    return True, int(LOCKOUT_SECONDS - elapsed)


def record_failed_login(remote_addr, username):
    key = _tracker_key(remote_addr, username)
    attempts = _failed_login_tracker.setdefault(key, {"count": 0, "last_attempt": 0})
    attempts["count"] += 1
    attempts["last_attempt"] = time.time()


def reset_failed_logins(remote_addr, username):
    _failed_login_tracker.pop(_tracker_key(remote_addr, username), None)


def generate_session_token():
    return secrets.token_urlsafe(32)


def establish_session(user, session_token):
    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    session["user"] = user["username"]
    session["role"] = user["role"]
    session["session_token"] = session_token


def is_active_session(conn):
    user_id = session.get("user_id")
    session_token = session.get("session_token")
    if not user_id or not session_token:
        return False

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, role, session_token FROM users WHERE id = %s",
        (user_id,),
    )
    user = cursor.fetchone()
    cursor.close()

    if not user or user.get("session_token") != session_token:
        return False

    session["user"] = user["username"]
    session["role"] = user["role"]
    return True


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        from db.db import get_db
        conn = get_db()
        valid = is_active_session(conn)
        conn.close()
        if not valid:
            session.clear()
            flash("Your session has expired. Please sign in again.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        from db.db import get_db
        conn = get_db()
        valid = is_active_session(conn)
        conn.close()
        if not valid:
            session.clear()
            flash("Your session has expired. Please sign in again.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            flash("Administrator access is required.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        return view(*args, **kwargs)

    return wrapped


def api_login_required():
    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401
    from db.db import get_db
    conn = get_db()
    valid = is_active_session(conn)
    conn.close()
    if not valid:
        session.clear()
        return jsonify({"error": "Session expired. Please log in again."}), 401
    return None


def api_admin_required():
    auth_error = api_login_required()
    if auth_error:
        return auth_error
    if session.get("role") != "admin":
        return jsonify({"error": "Administrator access is required."}), 403
    return None
