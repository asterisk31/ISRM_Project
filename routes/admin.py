from flask import Blueprint, flash, redirect, request, session, url_for

from db.db import get_db
from utils.auth_utils import admin_required, parse_positive_int
from utils.logger import log_event

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/delete_user", methods=["POST"])
@admin_required
def delete_user():
    try:
        user_id = parse_positive_int(request.form.get("id"), "User ID")
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("dashboard.dashboard"))

    if user_id == session.get("user_id"):
        flash("You cannot delete the currently signed-in administrator.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()

    if deleted == 0:
        flash("User not found.", "warning")
    else:
        log_event("USER DELETED", session.get("user"), f"user_id={user_id}")
        flash("User deleted successfully.", "success")

    return redirect(url_for("dashboard.dashboard"))
