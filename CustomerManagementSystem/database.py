import sqlite3

conn = sqlite3.connect('customer.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        email TEXT,
        google_map_url TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS repairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        photo_path TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
''')

conn.commit()
conn.close()