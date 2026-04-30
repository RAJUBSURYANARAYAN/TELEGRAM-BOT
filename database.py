import sqlite3
import os

DB_PATH = 'bot.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS claim_codes (
            code TEXT PRIMARY KEY,
            folder_uuid TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_code(code, folder_uuid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Basic collision handling
    try:
        c.execute('INSERT INTO claim_codes (code, folder_uuid) VALUES (?, ?)', (code, folder_uuid))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def get_and_delete_code(code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT folder_uuid FROM claim_codes WHERE code = ?', (code,))
    row = c.fetchone()
    if row:
        c.execute('DELETE FROM claim_codes WHERE code = ?', (code,))
        conn.commit()
        conn.close()
        return row[0]
    conn.close()
    return None
