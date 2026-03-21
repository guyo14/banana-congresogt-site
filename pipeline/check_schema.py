from crawler.db import get_connection
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'sessions';")
print(cur.fetchall())
