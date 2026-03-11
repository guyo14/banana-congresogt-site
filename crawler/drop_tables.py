from db import get_connection

def drop_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS attendance CASCADE;")
    cur.execute("DROP TABLE IF EXISTS votes CASCADE;")
    cur.execute("DROP TABLE IF EXISTS votations CASCADE;")
    cur.execute("DROP TABLE IF EXISTS sessions CASCADE;")
    cur.execute("DROP TABLE IF EXISTS congressmen_aliases CASCADE;")
    cur.execute("DROP TABLE IF EXISTS congressmen CASCADE;")
    cur.execute("DROP TABLE IF EXISTS districts CASCADE;")
    cur.execute("DROP TABLE IF EXISTS parties CASCADE;")
    cur.execute("DROP TYPE IF EXISTS session_type CASCADE;")
    cur.execute("DROP TYPE IF EXISTS attendance_status CASCADE;")
    cur.execute("DROP TYPE IF EXISTS vote_type CASCADE;")
    cur.execute("DROP TYPE IF EXISTS congressman_status CASCADE;")
    conn.commit()
    cur.close()
    conn.close()
    print("Tables dropped.")

if __name__ == "__main__":
    drop_tables()
