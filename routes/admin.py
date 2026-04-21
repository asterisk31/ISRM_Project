from flask import Blueprint, request, redirect
from db.db import get_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/delete_user')
def delete_user():
    user_id = request.args.get('id')

    conn = get_db()
    cursor = conn.cursor()

    # No role check → vulnerability
    query = f"DELETE FROM users WHERE id={user_id}"
    cursor.execute(query)
    conn.commit()

    return redirect('/dashboard')