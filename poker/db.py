import json
import os
import psycopg2

import logging
logger = logging.getLogger("db")

game_table_ddl = """
  CREATE TABLE IF NOT EXISTS game (
    game_id VARCHAR(100) PRIMARY KEY,
    state JSONB
  );
"""

db_url = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(db_url)

def load_game(conn, game_id):
    query = f"SELECT state FROM game WHERE game_id = '{game_id}'"
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    if len(rows) == 0:
        return None

    return rows[0][0]

def save_game(conn, game_id, state):
    state = json.dumps(state)
    stmt = f"INSERT INTO game (game_id, state) VALUES ('{game_id}', %s) ON CONFLICT (game_id) DO UPDATE SET state = %s"

    with conn.cursor() as cur:
        print(cur.execute(stmt, (state, state)))

def show_tables(conn):
    logger.info("SHOW TABLES ...")
    with conn.cursor() as cur:
        cur.execute("""SELECT table_catalog, table_schema, table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        for table in cur.fetchall():
            print(table)
            logger.info(table)

def bootstrap():
    conn = get_conn()
    with conn.cursor() as cur:
        print(cur.execute(game_table_ddl))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    bootstrap()
