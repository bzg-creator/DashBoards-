import psycopg2
import time
import random
from datetime import datetime

DB_SETTINGS = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Des1",
    "user": "postgres",
    "password": "776759"
}

def get_connection():
    return psycopg2.connect(**DB_SETTINGS)

def get_random_existing_id(cur, table, column):
    cur.execute(f"SELECT {column} FROM {table} ORDER BY RANDOM() LIMIT 1;")
    result = cur.fetchone()
    return result[0] if result else None

def insert_random_data():
    conn = get_connection()
    cur = conn.cursor()

    # --- Category
    cur.execute("""
        INSERT INTO category (catid, catgroup, catname, catdesc)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (catid) DO NOTHING;
    """, (
        random.randint(1000, 9999),
        random.choice(['Music', 'Sport', 'Theatre', 'Cinema']),
        random.choice(['Concert', 'Match', 'Play', 'Movie']),
        random.choice(['Great event', 'Big show', 'New season'])
    ))

    # --- Events
    cur.execute("""
        INSERT INTO events (eventid, venueid, catid, eventname, starttime)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (eventid) DO NOTHING;
    """, (
        random.randint(10000, 99999),
        random.randint(1, 5),
        random.randint(1, 10),
        random.choice(['Rock Night', 'Football Final', 'Opera Show']),
        datetime.now()
    ))

    # --- Listing
    cur.execute("""
        INSERT INTO listing (listid, sellerid, eventid, numtickets, priceperticket, totalprice, listtime)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (listid) DO NOTHING;
    """, (
        random.randint(20000, 99999),
        random.randint(1, 10),
        get_random_existing_id(cur, "events", "eventid") or 10000,
        random.randint(1, 5),
        round(random.uniform(25, 150), 2),
        round(random.uniform(100, 500), 2),
        datetime.now()
    ))

    # --- Sale (uses existing eventid + listid)
    existing_eventid = get_random_existing_id(cur, "events", "eventid")
    existing_listid = get_random_existing_id(cur, "listing", "listid")

    if existing_eventid and existing_listid:
        cur.execute("""
            INSERT INTO sale (saleid, listid, sellerid, buyerid, eventid, qtysold, pricepaid, commission, saletime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (saleid) DO NOTHING;
        """, (
            random.randint(100000, 999999),
            existing_listid,
            random.randint(1, 10),
            random.randint(1, 10),
            existing_eventid,
            random.randint(1, 3),
            round(random.uniform(100, 300), 2),
            round(random.uniform(10, 30), 2),
            datetime.now()
        ))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("🎯 Load generator started — inserting random data every 5 seconds...")
    while True:
        try:
            insert_random_data()
            print("✅ Inserted random data into Des1")
        except Exception as e:
            print("⚠️ Error:", e)
        time.sleep(5)
