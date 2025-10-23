#!/usr/bin/env python3
import json
import os
import sqlite3

game_table_ddl = """
  CREATE TABLE IF NOT EXISTS game (
    game_id TEXT PRIMARY KEY,
    state TEXT
  );
"""

db_url = os.environ.get("DATABASE_URL") or 'poker.db'

class Connection():
    def __init__(self):
        pass

    def __enter__(self):
        self.conn = sqlite3.connect(db_url, timeout=30.0)
        # Enable WAL mode for better concurrency
        self.conn.execute('PRAGMA journal_mode=WAL;')
        # Begin immediate transaction to lock the database
        self.conn.execute('BEGIN IMMEDIATE;')
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            # No exception occurred, commit the transaction
            self.conn.commit()
        else:
            # Exception occurred, rollback the transaction
            self.conn.rollback()
        self.conn.close()

    def load_game(self, game_id):
        query = "SELECT state FROM game WHERE game_id = ?;"
        cur = self.conn.cursor()
        cur.execute(query, (game_id,))
        rows = cur.fetchall()

        if len(rows) == 0:
            return None

        return json.loads(rows[0][0])

    def save_game(self, game_id, state):
        state = json.dumps(state)
        stmt = "INSERT INTO game (game_id, state) VALUES (?, ?) ON CONFLICT (game_id) DO UPDATE SET state = ?"

        cur = self.conn.cursor()
        cur.execute(stmt, (game_id, state, state))

    def commit(self):
        # Commit is now handled automatically in __exit__
        pass

def bootstrap(fn):
    conn = sqlite3.connect(fn)
    print(f'Connected to {fn}')
    cur = conn.cursor()
    cur.execute(game_table_ddl)
    print(game_table_ddl)
    conn.commit()
    conn.close()

if __name__=='__main__':
    bootstrap(db_url)
