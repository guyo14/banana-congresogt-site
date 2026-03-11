import os
import psycopg2
from psycopg2.extras import execute_values
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

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema", "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(schema_sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Database schema initialized.")

def init_aliases():
    alias_path = os.path.join(os.path.dirname(__file__), "schema", "alias.sql")
    if not os.path.exists(alias_path):
        return
    with open(alias_path, "r") as f:
        alias_sql = f.read()
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(alias_sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Aliases initialized.")

def insert_parties(parties):
    query = """
    INSERT INTO parties (id, name)
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name;
    """
    conn = get_connection()
    cur = conn.cursor()
    execute_values(cur, query, parties)
    conn.commit()
    cur.close()
    conn.close()

def insert_districts(districts):
    query = """
    INSERT INTO districts (id, name)
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name;
    """
    conn = get_connection()
    cur = conn.cursor()
    execute_values(cur, query, districts)
    conn.commit()
    cur.close()
    conn.close()

def insert_congressmen(congressmen):
    # congressmen is a list of tuples: (id, first_name, last_name, key, party_id, district_id, photo_url, birth_date, status)
    # The 'name' column in DB is kept but will no longer be explicitly inserted from the crawler, instead we use first_name and last_name
    query = """
    INSERT INTO congressmen (id, first_name, last_name, key, party_id, district_id, photo_url, birth_date, status)
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        key = EXCLUDED.key,
        party_id = EXCLUDED.party_id,
        district_id = EXCLUDED.district_id,
        photo_url = EXCLUDED.photo_url,
        birth_date = EXCLUDED.birth_date,
        status = EXCLUDED.status;
    """
    conn = get_connection()
    cur = conn.cursor()
    execute_values(cur, query, congressmen)
    conn.commit()
    cur.close()
    conn.close()

def get_congressmen_dict():
    query_congressmen = """
    SELECT id, key 
    FROM congressmen;
    """
    query_aliases = """
    SELECT congressman_id, alias 
    FROM congressmen_aliases;
    """
    
    conn = get_connection()
    cur = conn.cursor()
    
    congressmen_dict = {}
    
    # Load primary keys
    cur.execute(query_congressmen)
    for row in cur.fetchall():
        c_id, key = row
        congressmen_dict[key] = c_id
        
    # Load aliases (these will override or supplement existing keys nicely)
    try:
        cur.execute(query_aliases)
        for row in cur.fetchall():
            c_id, alias = row
            congressmen_dict[alias] = c_id
    except psycopg2.errors.UndefinedTable:
        # Table might not exist yet if init_aliases hasn't been called, rollback and log ignoring
        conn.rollback()

    cur.close()
    conn.close()
    return congressmen_dict

def insert_session(session):
    # session: (id, type, session_number, start_date)
    query = """
    INSERT INTO sessions (id, type, session_number, start_date)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        type = EXCLUDED.type,
        session_number = EXCLUDED.session_number,
        start_date = EXCLUDED.start_date;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, session)
    conn.commit()
    cur.close()
    conn.close()

def insert_votation(votation):
    # votation: (id, session_id, subject, start_date)
    query = """
    INSERT INTO votations (id, session_id, subject, start_date)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        session_id = EXCLUDED.session_id,
        subject = EXCLUDED.subject,
        start_date = EXCLUDED.start_date;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, votation)
    conn.commit()
    cur.close()
    conn.close()

def insert_votes(votes):
    # votes: list of (votation_id, congressman_id, vote_type, attendance_status)
    query = """
    INSERT INTO votes (votation_id, congressman_id, vote_type, attendance_status)
    VALUES %s
    ON CONFLICT (votation_id, congressman_id) DO UPDATE SET
        vote_type = EXCLUDED.vote_type,
        attendance_status = EXCLUDED.attendance_status;
    """
    conn = get_connection()
    cur = conn.cursor()
    execute_values(cur, query, votes)
    conn.commit()
    cur.close()
    conn.close()

def insert_attendance(records):
    # records: list of (session_id, congressman_id, status)
    query = """
    INSERT INTO attendance (session_id, congressman_id, status)
    VALUES %s
    ON CONFLICT (session_id, congressman_id) DO UPDATE SET
        status = EXCLUDED.status;
    """
    conn = get_connection()
    cur = conn.cursor()
    execute_values(cur, query, records)
    conn.commit()
    cur.close()
    conn.close()
