import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def export_all_tables_to_csv():
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all tables in public schema
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    backup_dir = "../data"
    os.makedirs(backup_dir, exist_ok=True)
    
    for table in tables:
        csv_file_path = os.path.join(backup_dir, f"{table}.csv")
        print(f"Exporting {table} to {csv_file_path}...")
        with open(csv_file_path, "w") as f:
            copy_sql = f"COPY {table} TO STDOUT WITH CSV HEADER"
            cur.copy_expert(copy_sql, f)
            print(f"Exported {table} successfully.")
            
    cur.close()
    conn.close()
    print("All tables exported!")

if __name__ == "__main__":
    export_all_tables_to_csv()
