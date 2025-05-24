import sqlite3

try:
    # Attempts to create a connection to an in-memory SQLite database.
    conn = sqlite3.connect(':memory:')
    print("SQLite is running on your system.")
    conn.close()
except sqlite3.Error as e:
    print(f"Error: {e}")
    print("SQLite is not working correctly on your system.")