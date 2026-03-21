from crawler.db import get_connection

conn = get_connection()
cur = conn.cursor()

print("--- RECENT SESSIONS ---")
cur.execute("SELECT id, type, session_number, start_date FROM sessions ORDER BY id DESC LIMIT 2;")
for row in cur.fetchall():
    print(row)

print("\n--- RECENT VOTATIONS ---")
cur.execute("SELECT id, session_id, subject, start_date FROM votations ORDER BY id DESC LIMIT 2;")
for row in cur.fetchall():
    print(row)

print("\n--- RECENT VOTES ---")
cur.execute("SELECT votation_id, congressman_id, vote_type, attendance_status FROM votes ORDER BY votation_id DESC, congressman_id DESC LIMIT 5;")
for row in cur.fetchall():
    print(row)

try:
    with open("crawler/crawl_report.txt", "r") as f:
        print("\n--- CRAWL REPORT ---")
        print(f.read())
except:
    pass

cur.close()
conn.close()
