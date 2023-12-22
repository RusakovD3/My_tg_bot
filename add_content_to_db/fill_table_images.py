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

    directory = "./imgs/"

    for filename in os.listdir(directory):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".png"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "rb") as file:
                file_data = file.read()
                cursor.execute(
                    "INSERT INTO Images (image) VALUES (%s)",
                    (psycopg2.Binary(file_data),),
                )

    conn.commit()
    cursor.close()
    conn.close()
