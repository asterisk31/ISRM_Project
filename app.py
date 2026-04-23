from flask import Flask
from routes.auth import auth_bp
from routes.dashboard import dash_bp
from routes.api import api_bp
from routes.upload import upload_bp
from routes.admin import admin_bp
from routes.demo import demo_bp

app = Flask(__name__)
app.secret_key = "devkey"  # intentional

app.register_blueprint(auth_bp)
app.register_blueprint(dash_bp)
app.register_blueprint(api_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(demo_bp)

if __name__ == "__main__":
    # Bind to all interfaces and disable debug mode in CI/CD environments
    import os
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode, use_reloader=False)