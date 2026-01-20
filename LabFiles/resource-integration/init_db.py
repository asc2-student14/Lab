
import sqlite3

DB_FILE = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS items")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            quantity INTEGER,
            price REAL,
            category TEXT,
            description TEXT,
            last_updated TEXT
        )
    ''')
    # Insert realistic sample data for lab testing
    sample_items = [
        # Electronics category
        ("MacBook Pro", 50, 1299.99, "Electronics", "High-performance laptop for developers", "2024-01-15"),
        ("iPhone 15", 75, 799.99, "Electronics", "Latest smartphone with advanced features", "2024-01-20"),
        ("iPad Air", 40, 599.99, "Electronics", "Tablet for productivity and creativity", "2024-01-25"),
        ("AirPods Pro", 100, 249.99, "Electronics", "Wireless earbuds with noise cancellation", "2024-01-30"),

        # Furniture category
        ("Ergonomic Office Chair", 25, 299.99, "Furniture", "Comfortable chair for long work sessions", "2024-02-10"),
        ("Standing Desk", 15, 449.99, "Furniture", "Adjustable height desk for better health", "2024-02-15"),
        ("Bookshelf", 30, 179.99, "Furniture", "5-shelf wooden bookshelf for storage", "2024-02-20"),
        ("Coffee Table", 20, 199.99, "Furniture", "Modern glass coffee table", "2024-02-25"),

        # Books category
        ("Python Programming", 150, 39.99, "Books", "Complete guide to Python development", "2024-03-01"),
        ("Clean Code", 120, 34.99, "Books", "Best practices for writing maintainable code", "2024-03-05"),
        ("System Design", 80, 49.99, "Books", "Designing scalable distributed systems", "2024-03-10"),
        ("Machine Learning", 90, 59.99, "Books", "Introduction to ML algorithms and techniques", "2024-03-15"),

        # Clothing category
        ("Tech T-Shirt", 200, 24.99, "Clothing", "Comfortable cotton t-shirt with tech logos", "2024-04-01"),
        ("Hoodie", 100, 49.99, "Clothing", "Warm hoodie for coding sessions", "2024-04-05"),
        ("Jeans", 150, 79.99, "Clothing", "Classic denim jeans", "2024-04-10"),

        # Tools category
        ("Wireless Mouse", 60, 79.99, "Tools", "Precision wireless mouse for productivity", "2024-05-01"),
        ("Mechanical Keyboard", 45, 149.99, "Tools", "Tactile keyboard for programmers", "2024-05-05"),
        ("Monitor Stand", 35, 89.99, "Tools", "Adjustable stand for better ergonomics", "2024-05-10"),
        ("USB-C Hub", 80, 59.99, "Tools", "Multi-port hub for connectivity", "2024-05-15"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO items (name, quantity, price, category, description, last_updated) VALUES (?, ?, ?, ?, ?, ?)", sample_items)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_FILE} with {len(sample_items)} records.")

if __name__ == "__main__":
    init_db()
