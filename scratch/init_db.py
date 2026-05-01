import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        conn.autocommit = True
        cur = conn.cursor()

        sql_files = [
            "database/schema.sql",
            "database/constraints.sql",
            "database/procedures.sql",
            "database/triggers.sql",
            "database/queries.sql",
            "database/seed_data.sql"
        ]

        for sql_file in sql_files:
            print(f"Executing {sql_file}...")
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql = f.read()
                if sql.strip():
                    cur.execute(sql)
            print(f"Finished {sql_file}")

        cur.close()
        conn.close()
        print("Database initialization successful!")

    except Exception as e:
        print(f"Database initialization failed: {e}")

if __name__ == "__main__":
    init_db()
