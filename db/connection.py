import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "/tmp"),
        port=os.environ.get("DB_PORT", "5431"),
        database=os.environ.get("DB_NAME", "bank_db"),
        user=os.environ.get("DB_USER", ""),
        password=os.environ.get("DB_PASSWORD", ""),
    )