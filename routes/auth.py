from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db.db import get_db
from utils.auth_utils import (
    establish_session,
    generate_session_token,
    is_login_blocked,
    record_failed_login,
    reset_failed_logins,
    validate_password,
    validate_username,
)
from utils.logger import log_event

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)

        try:
            username = validate_username(username)
            validate_password(password)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("login.html"), 400

        blocked, retry_after = is_login_blocked(remote_addr, username)
        if blocked:
            flash(f"Too many failed logins. Try again in {retry_after} seconds.", "danger")
            log_event("LOGIN RATE LIMITED", username, f"ip={remote_addr}")
            return render_template("login.html"), 429

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, password, role FROM users WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            reset_failed_logins(remote_addr, username)
            session_token = generate_session_token()
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET session_token = %s WHERE id = %s",
                (session_token, user["id"]),
            )
            conn.commit()
            cursor.close()
            conn.close()
            establish_session(user, session_token)
            log_event("LOGIN SUCCESS", username, f"ip={remote_addr}")
            return redirect(url_for("dashboard.dashboard"))

        record_failed_login(remote_addr, username)
        log_event("LOGIN FAILED", username, f"ip={remote_addr}")
        flash("Invalid username or password.", "danger")
        return render_template("login.html"), 401

    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            username = validate_username(request.form.get("username", ""))
            password = validate_password(request.form.get("password", ""), signup=True)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("signup.html"), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            flash("That username is already registered.", "danger")
            return render_template("signup.html"), 409

        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password_hash, "user"),
        )
        conn.commit()
        cursor.close()
        conn.close()

        log_event("ACCOUNT CREATED", username)
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    username = session.get("user")
    user_id = session.get("user_id")
    if user_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET session_token = NULL WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    session.clear()
    if username:
        log_event("LOGOUT", username)
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
