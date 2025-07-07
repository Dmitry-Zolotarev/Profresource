import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = 'db.sqlite3'
DB_PATH = os.path.join(BASE_DIR, DB_NAME)
SCHEMA_FILE = os.path.join(BASE_DIR, 'test_data.sql')

def create_db_if_not_exists():
    if os.path.exists(DB_PATH):
        print("Добавление начальных данных...")
        with open(SCHEMA_FILE, encoding='utf-8') as f:
            sql_script = f.read()

        conn = sqlite3.connect(DB_PATH)
        conn.executescript(sql_script)
        conn.commit()
        print("Начальные данные добавлены.")
        conn.close()
    else:
        print("Базы данных не существует!")

if __name__ == '__main__':
    create_db_if_not_exists()
