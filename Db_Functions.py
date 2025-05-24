# db_functions.py
import sqlite3
import os
from pathlib import Path

def get_db_path():
    # Use a path relative to the user's home directory
    db_path = Path.home() / "Expense_Tracker_BY_YAHYA_MATER" / "expenses.db"
    db_path.parent.mkdir(exist_ok=True)  # Ensure the directory exists
    return str(db_path)

def setup_database():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the records table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whom TEXT NOT NULL,
            date TEXT NOT NULL,
            why TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')

    # Create the categories table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            default_amount REAL
        )
    ''')

    # Prepopulate categories if empty
    cursor.execute('SELECT COUNT(*) FROM categories')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO categories (name, default_amount) VALUES (?, ?)', [
            ('Food', 10.00),
            ('Transport', 5.00),
            ('Entertainment', 20.00)
        ])

    conn.commit()
    conn.close()
    print(f"Database set up successfully. in {db_path}")

def add_record(whom, date, why, amount):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO records (whom, date, why, amount) VALUES (?, ?, ?, ?)', (whom, date, why, amount))
    conn.commit()
    conn.close()

def search_records(whom=None, start_date=None, end_date=None, min_amount=None, max_amount=None, group_by_whom=True, like_whom=True):
    print("search_records parameters:", whom, " ", start_date, " ", end_date , " ", min_amount , " ", max_amount)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
        SELECT
            id,
            whom,
            why
    '''
    if group_by_whom:
        query += """,
            MAX(date) AS last_date,
            SUM(amount) AS total_amount
        """
    else:
        query += ", date AS last_date, amount"
    
    query += " FROM records WHERE 1=1"
    
    params = []
    if whom:
        if like_whom:
            query += ' AND whom LIKE ?'
            params.append(f'{whom}%')
        else:
            query += ' AND whom = ?'
            params.append(whom)
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    if min_amount:
        query += ' AND amount >= ?'
        params.append(min_amount)
    if max_amount:
        query += ' AND amount <= ?'
        params.append(max_amount)

    if group_by_whom:
        query += ' GROUP BY whom'

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    print("search_records results:", results)
    return results

def delete_record(id=None):
    if id is None:
        return
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", [id])
    conn.commit()
    conn.close()


def parse_search_query(query):
    name = None
    start_date = None
    end_date = None
    min_amount = None
    max_amount = None

    tokens = query.split()
    for token in tokens:
        if token.startswith('/'):
            if token[1] == '>':
                start_date = token[2:]
            elif token[1] == '<':
                end_date = token[2:]
        elif token.startswith('$'):
            if token[1] == '>':
                min_amount = float(token[2:])
            elif token[1] == '<':
                max_amount = float(token[2:])
            else:
                min_amount = max_amount = float(token[1:])
        else:
            name = token

    print("parse_search_query results:", name, " ", start_date, " ", end_date , " ", min_amount , " ", max_amount)
    return name, start_date, end_date, min_amount, max_amount

def fetch_summary():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            id,
            whom,
            why,
            MAX(date) AS last_date, 
            SUM(amount) AS total_amount 
        FROM records 
        GROUP BY whom
    ''')
    results = cursor.fetchall()
    conn.close()
    print("Summary fetched successfully. results:", results)
    return results

