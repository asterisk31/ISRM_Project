from flask import Blueprint, request, render_template, redirect, session
from db.db import get_db
from utils.logger import log_event

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # SQL Injection vulnerability
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)

        user = cursor.fetchone()

        if user:
            #log user input directly(intentional vuln)
            log_event(f"[LOGIN SUCCESS] User: {username}")

            # Session creation (intentionally weak)
            session['user'] = user['username']
            session['role'] = user['role']
            
            # Add extra exposure (for demonstration)
            session['login_time'] = str(request.headers.get('User-Agent'))
            
            return redirect('/dashboard')
        else:
            log_event(f"[LOGIN FAILED] for user: {username}")
            
            return render_template('login.html')
    
    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()

        # No validation
        query = f"""
        INSERT INTO users (username, password, role)
        VALUES ('{request.form['username']}', '{request.form['password']}', 'user')
        """
        cursor.execute(query)
        conn.commit()

        return redirect('/login')

    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    # Remove session data (basic logout)
    session.pop('user', None)
    session.pop('role', None)

    return redirect('/login')

#no password hashing