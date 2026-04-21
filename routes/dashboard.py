from flask import Blueprint, session, render_template, request, redirect
from db.db import get_db

dash_bp = Blueprint('dashboard', __name__)

@dash_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')  # enforce login

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(f"SELECT role FROM users WHERE username='{session.get('user')}'")
    role = cursor.fetchone()['role']

    cursor.execute("SELECT id, name, marks FROM students")
    student_data = cursor.fetchall()

    admin_data = None

    if role == 'admin':
        cursor.execute("SELECT * FROM users")
        admin_data = cursor.fetchall()

    return render_template(
        'dashboard.html',
        data=student_data,
        admin_data=admin_data,
        role=role
    )

#Role can be modified via URL → privilege escalation