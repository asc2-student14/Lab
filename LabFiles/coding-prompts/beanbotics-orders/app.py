from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'beanbotics-secret-key'

DB_FILE = "orders.db"

def get_menu_items():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM menu_items")
    items = cursor.fetchall()
    conn.close()
    return [{'id': item[0], 'name': item[1], 'description': item[2]} for item in items]

def create_order_record(customer_name, item_id, size, total_price):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (customer_name, item_id, size, total_price, order_time)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_name, item_id, size, total_price, datetime.datetime.now().isoformat()))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def apply_tax(price):
    tax_amount = price * 0.05
    return price - tax_amount

def calculate_price_by_size(size):
    size_prices = {
        'small': 4.50,
        'medium': 5.50,
        'large': 6.50
    }
    base_price = size_prices.get(size, 5.50)
    return apply_tax(base_price)

def get_order(order_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.id, o.customer_name, o.size, o.total_price, o.order_time,
               m.name, m.description
        FROM orders o
        JOIN menu_items m ON o.item_id = m.id
        WHERE o.id = ?
    """, (order_id,))
    order = cursor.fetchone()
    conn.close()
    if order:
        return {
            'id': order[0],
            'customer_name': order[1],
            'size': order[2],
            'total_price': order[3],
            'order_time': datetime.datetime.fromisoformat(order[4]),
            'item': {'name': order[5], 'description': order[6]}
        }
    return None

@app.route('/')
def home():
    return redirect(url_for('create_order'))

@app.route('/order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        item_id = request.form.get('item_id')
        size = request.form.get('size', 'medium')
        
        if not customer_name or not item_id:
            return "Missing required fields", 400
            
        total_price = calculate_price_by_size(size)
        order_id = create_order_record(customer_name, item_id, size, total_price)
        return redirect(url_for('order_success', order_id=order_id))
    
    items = get_menu_items()
    return render_template('order.html', items=items)

@app.route('/order/<int:order_id>/success')
def order_success(order_id):
    order = get_order(order_id)
    if not order:
        return "Order not found", 404
    return render_template('success.html', order=order)

@app.route('/debug')
def debug_menu():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.id, o.customer_name, o.size, o.total_price, o.order_time,
               m.name
        FROM orders o
        JOIN menu_items m ON o.item_id = m.id
        ORDER BY o.order_time DESC
    """)
    orders = cursor.fetchall()
    conn.close()
    
    order_list = []
    for order in orders:
        order_list.append({
            'id': order[0],
            'customer_name': order[1],
            'size': order[2],
            'total_price': order[3],
            'order_time': datetime.datetime.fromisoformat(order[4]),
            'item_name': order[5]
        })
    
    return render_template('debug.html', orders=order_list)

@app.route('/debug/clear', methods=['POST'])
def clear_orders():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders")
    conn.commit()
    conn.close()
    return redirect(url_for('debug_menu'))

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            size TEXT DEFAULT 'medium',
            total_price REAL NOT NULL,
            order_time TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    if cursor.fetchone()[0] == 0:
        items = [
            ("Espresso", "Rich, bold coffee shot"),
            ("Americano", "Espresso with hot water"),
            ("Latte", "Espresso with steamed milk"),
            ("Cappuccino", "Espresso with steamed milk foam"),
            ("Mocha", "Espresso with chocolate and steamed milk")
        ]
        
        cursor.executemany(
            "INSERT INTO menu_items (name, description) VALUES (?, ?)",
            items
        )
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)