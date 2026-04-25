from flask import Blueprint, render_template

from utils.auth_utils import admin_required

demo_bp = Blueprint("demo", __name__)


@demo_bp.route("/demo/attack-chain")
@admin_required
def attack_chain():
    return render_template(
        "attack_chain.html",
        controls=[
            "Parameterized SQL queries across authentication, admin, and API flows",
            "Password hashing with Werkzeug security helpers",
            "Role-based access control for admin-only mutations",
            "Validated usernames, roles, integer IDs, marks, and upload file types",
            "Sanitized application logging and restrictive security headers",
            "Hardened session cookies with expiry and HTTP-only flags",
        ],
    )
