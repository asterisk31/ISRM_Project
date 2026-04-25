import os

from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename

from utils.auth_utils import allowed_upload
from utils.logger import log_event

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"


@upload_bp.route("/upload", methods=["POST"])
def upload():
    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({"error": "A file is required."}), 400

    if not allowed_upload(file.filename):
        return jsonify({"error": "Unsupported file type."}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    log_event("FILE UPLOADED", session.get("user"), filename)
    return jsonify({"status": "Uploaded", "filename": filename})
