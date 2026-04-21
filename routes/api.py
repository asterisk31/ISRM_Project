from flask import Blueprint, request, jsonify, session, redirect

from db.db import get_db

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/student')
def get_student():

    if 'user' not in session:
        return "Unauthorized", 401

    student_id = request.args.get('id')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # SQL Injection
    query = f"SELECT * FROM students WHERE id={student_id}"
    cursor.execute(query)

    result = cursor.fetchall()

    return jsonify(result)

@api_bp.route('/api/change_role', methods=['POST'])
def change_role():
    if 'user' not in session:
        return "Login required"

    username = request.form.get('username')
    new_role = request.form.get('role')

    conn = get_db()
    cursor = conn.cursor()

    # No authorization check → vulnerability
    query = f"UPDATE users SET role='{new_role}' WHERE username='{username}'"
    cursor.execute(query)
    conn.commit()

    if username == session.get('user'):
        session['role'] = new_role

    return "Role updated"

@api_bp.route('/api/update_marks', methods=['POST'])
def update_marks():
    if 'user' not in session:
        return "Unauthorized", 401

    student_id = request.form.get('id')
    marks = request.form.get('marks')

    conn = get_db()
    cursor = conn.cursor()

    # INTENTIONAL ISSUE:
    # No role check → any logged-in user can modify marks
    query = f"UPDATE students SET marks={marks} WHERE id={student_id}"
    cursor.execute(query)
    conn.commit()

    return "Marks updated"

@api_bp.route('/api/delete_student', methods=['POST'])
def delete_student():
    if 'user' not in session:
        return "Unauthorized", 401

    student_id = request.form.get('id')

    conn = get_db()
    cursor = conn.cursor()

    # INTENTIONAL ISSUE:
    # No role check + SQL injection
    query = f"DELETE FROM students WHERE id={student_id}"
    cursor.execute(query)
    conn.commit()

    return "Student deleted"

# injection +data exposure
