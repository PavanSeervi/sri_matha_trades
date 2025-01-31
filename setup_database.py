import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)
''')

# Insert sample data
cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Product 1', 100.0, 10)")
cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Product 2', 200.0, 5)")

# Commit and close
conn.commit()
conn.close()