#!/usr/bin/env python3
"""
Test script to verify database schema alignment
"""
import sys
import os

# Add the crawler directory to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import psycopg2
    from dotenv import load_dotenv

    load_dotenv()

    print("=== Testing Database Connection ===")
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    print("✓ Connection successful")

    cur = conn.cursor()

    # Test table existence
    print("\n=== Checking Tables ===")
    tables = ['blocks', 'parties', 'districts', 'congressmen', 'sessions', 'voting', 'votes', 'attendance']
    for table in tables:
        cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');")
        exists = cur.fetchone()[0]
        if exists:
            print(f"✓ {table} exists")
        else:
            print(f"✗ {table} MISSING")

    # Check voting table structure
    print("\n=== Voting Table Structure ===")
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'voting'
        ORDER BY ordinal_position;
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check votes table structure
    print("\n=== Votes Table Structure ===")
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'votes'
        ORDER BY ordinal_position;
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check if initial data exists
    print("\n=== Data Check ===")
    cur.execute("SELECT COUNT(*) FROM blocks;")
    print(f"Blocks: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM parties;")
    print(f"Parties: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM districts;")
    print(f"Districts: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM congressmen;")
    print(f"Congressmen: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM sessions;")
    print(f"Sessions: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM voting;")
    print(f"Voting: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM votes;")
    print(f"Votes: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM attendance;")
    print(f"Attendance: {cur.fetchone()[0]}")

    cur.close()
    conn.close()

    print("\n✓ All tests passed!")

except ImportError as e:
    print(f"✗ Missing dependency: {e}")
    print("\nPlease install dependencies:")
    print("  pip3 install psycopg2-binary python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
