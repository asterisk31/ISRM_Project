from flask import Blueprint, flash, jsonify, redirect, request, session, url_for

from db.db import get_db
from utils.auth_utils import (
    api_admin_required,
    api_login_required,
    parse_marks,
    parse_positive_int,
    validate_role,
    validate_username,
)
from utils.logger import log_event

api_bp = Blueprint("api", __name__)


def _success_response(message):
    wants_json = request.is_json or request.accept_mimetypes.best == "application/json"
    if wants_json:
        return jsonify({"status": message})
    flash(message, "success")
    return redirect(url_for("dashboard.dashboard"))


def _error_response(message, status_code):
    wants_json = request.is_json or request.accept_mimetypes.best == "application/json"
    if wants_json:
        return jsonify({"error": message}), status_code
    flash(message, "danger")
    return redirect(url_for("dashboard.dashboard"))


@api_bp.route("/api/student")
def get_student():
    auth_error = api_login_required()
    if auth_error:
        return auth_error

    student_id = request.args.get("id")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if student_id:
        try:
            parsed_student_id = parse_positive_int(student_id, "Student ID")
        except ValueError as exc:
            cursor.close()
            conn.close()
            return jsonify({"error": str(exc)}), 400

        cursor.execute(
            "SELECT id, name, marks, email FROM students WHERE id = %s",
            (parsed_student_id,),
        )
    else:
        cursor.execute("SELECT id, name, marks, email FROM students ORDER BY id")

    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@api_bp.route("/api/change_role", methods=["POST"])
def change_role():
    auth_error = api_admin_required()
    if auth_error:
        return auth_error

    try:
        username = validate_username(request.form.get("username", ""))
        new_role = validate_role(request.form.get("role", ""))
    except ValueError as exc:
        return _error_response(str(exc), 400)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = %s WHERE username = %s", (new_role, username))
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated == 0:
        return _error_response("User not found.", 404)

    if username == session.get("user"):
        session["role"] = new_role

    log_event("ROLE UPDATED", session.get("user"), f"target={username} role={new_role}")
    return _success_response("Role updated")


@api_bp.route("/api/update_marks", methods=["POST"])
def update_marks():
    auth_error = api_admin_required()
    if auth_error:
        return auth_error

    try:
        student_id = parse_positive_int(request.form.get("id"), "Student ID")
        marks = parse_marks(request.form.get("marks"))
    except ValueError as exc:
        return _error_response(str(exc), 400)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET marks = %s WHERE id = %s",
        (marks, student_id),
    )
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated == 0:
        return _error_response("Student not found.", 404)

    log_event("STUDENT MARKS UPDATED", session.get("user"), f"student_id={student_id} marks={marks}")
    return _success_response("Marks updated")


@api_bp.route("/api/delete_student", methods=["POST"])
def delete_student():
    auth_error = api_admin_required()
    if auth_error:
        return auth_error

    try:
        student_id = parse_positive_int(request.form.get("id"), "Student ID")
    except ValueError as exc:
        return _error_response(str(exc), 400)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()

    if deleted == 0:
        return _error_response("Student not found.", 404)

    log_event("STUDENT DELETED", session.get("user"), f"student_id={student_id}")
    return _success_response("Student deleted")
