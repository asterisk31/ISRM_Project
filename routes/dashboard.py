from flask import Blueprint, redirect, render_template, session, url_for

from db.db import get_db
from utils.auth_utils import login_required

dash_bp = Blueprint("dashboard", __name__)


@dash_bp.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, role FROM users WHERE id = %s",
        (session.get("user_id"),),
    )
    current_user = cursor.fetchone()

    if not current_user:
        cursor.close()
        conn.close()
        session.clear()
        return redirect(url_for("auth.login"))

    role = current_user["role"]
    session["role"] = role
    session["user"] = current_user["username"]

    cursor.execute("SELECT id, name, marks FROM students ORDER BY id")
    student_data = cursor.fetchall()

    admin_data = None
    if role == "admin":
        cursor.execute("SELECT id, username, role FROM users ORDER BY username")
        admin_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        data=student_data,
        admin_data=admin_data,
        role=role,
    )
