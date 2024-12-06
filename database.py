import sqlite3
from contextlib import contextmanager


def create_table():
    conn = sqlite3.connect('gb_values_db.db')
    cursor = conn.cursor()

    table_schema="""
        timestamp_checked INTEGER,
        gb_count REAL,
        is_changed_from_last_check INTEGER
    """
    cursor.execute(f"CREATE TABLE IF NOT EXISTS gb_values_db ({table_schema});")

    conn.commit()
    conn.close()


create_table()


@contextmanager
def db_connection():
    conn = sqlite3.connect('gb_values_db.db')
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        conn.close()


def get_last_row():

    with db_connection() as cursor:
        query = f"SELECT * FROM gb_values_db ORDER BY timestamp_checked DESC LIMIT 1"
        cursor.execute(query)
        last_row = cursor.fetchone()
    return last_row


def get_is_changed_from_last_check(current_total_gb_count):
    last_row = get_last_row()
    if last_row is None:
        return True
    last_saved_total_gb_count = last_row[1]
    return current_total_gb_count != last_saved_total_gb_count


def insert_row(values):
    with db_connection() as cursor:
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO gb_values_db VALUES ({placeholders})"
        cursor.execute(query, values)