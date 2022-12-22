import sqlite3

def update(query, parameters):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    conn.commit()
    last_row_id = cursor.lastrowid
    conn.close()
    return last_row_id

def query(query, parameters):
    conn = get_db_connection()
    result = conn.execute(query, parameters).fetchone()
    conn.close()
    return result

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn