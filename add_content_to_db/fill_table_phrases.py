import os
import psycopg2
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")

    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor()

    file_path = "./texts./phrases.txt"

    with open(file_path, "r", encoding="utf8") as file:
        for line in file:
            line = line.strip()
            if line:
                cursor.execute("INSERT INTO phrase (text) VALUES (%s)", (line,))

    conn.commit()
    cursor.close()
    conn.close()
