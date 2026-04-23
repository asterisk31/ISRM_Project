import mysql.connector
from config import DB_CONFIG
import os

try:
    from config import DB_CONFIG
except ModuleNotFoundError:
    # Use environment variables or defaults for CI/CD
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "isrm_test"),
        "raise_on_warnings": False,
    }

def get_db():
    return mysql.connector.connect(**DB_CONFIG)