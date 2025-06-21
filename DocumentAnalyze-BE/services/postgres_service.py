import os
import psycopg2
from dotenv import load_dotenv

# Load .env file variables
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def store_document(filename, extracted_text, doc_type=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (filename, extracted_text, doc_type) VALUES (%s, %s, %s)",
        (filename, extracted_text, doc_type)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Document stored in DB: {filename}")

