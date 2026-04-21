from flask import Blueprint, request
import os

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = "uploads/"

@upload_bp.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    # No validation
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    return "Uploaded"

#vuln -> arbitrary file upload, which can possibly lead to RCE
