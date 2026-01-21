from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'beanbotics-secret-key'

# Configuration constants
DB_FILE = "orders.db"
TAX_RATE = 0.05
DEFAULT_SIZE = 'medium'
SIZE_PRICES = {
    'small': 4.50,
    'medium': 5.50,
    'large': 6.50
}


def get_menu_items() -> list[dict[str, int | str]]:
    """Retrieve all menu items from the database.

    Fetches all available menu items from the menu_items table,
    including their IDs, names, and descriptions.

    Returns:
        list[dict[str, int | str]]: A list of dictionaries, where each 
            dictionary contains:
            - 'id' (int): The unique identifier of the menu item
            - 'name' (str): The display name of the menu item
            - 'description' (str): A brief description of the item

    Raises:
        sqlite3.Error: If there's an issue connecting to or querying the database.

    Example:
        >>> items = get_menu_items()
        >>> print(items[0])
        {'id': 1, 'name': 'Espresso', 'description': 'Strong Italian coffee'}
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM menu_items")
        items = cursor.fetchall()
    return [{'id': item[0], 'name': item[1], 'description': item[2]} for item in items]


def create_order_record(customer_name: str, item_id: int, size: str, total_price: float) -> int:
    """Create a new order record in the database.

    Args:
        customer_name: The name of the customer placing the order.
        item_id: The ID of the menu item being ordered.
        size: The size of the drink ('small', 'medium', or 'large').
        total_price: The calculated total price including tax.

    Returns:
        int: The ID of the newly created order.

    Raises:
        sqlite3.Error: If there's an issue with the database operation.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_name, item_id, size, total_price, order_time)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_name, item_id, size, total_price, datetime.datetime.now().isoformat()))
        order_id = cursor.lastrowid
        conn.commit()
    return order_id


def apply_tax(price: float) -> float:
    """Apply sales tax to a price.

    Args:
        price: The base price before tax.

    Returns:
        float: The price with tax added.

    Example:
        >>> apply_tax(10.00)
        10.50
    """
    tax_amount = price * TAX_RATE
    return price + tax_amount


def calculate_price_by_size(size: str) -> float:
    """Calculate the total price for a drink based on its size.

    Args:
        size: The size of the drink ('small', 'medium', or 'large').
            Defaults to medium price if size is not recognized.

    Returns:
        float: The total price including tax.

    Example:
        >>> calculate_price_by_size('large')
        6.825
    """
    base_price = SIZE_PRICES.get(size, SIZE_PRICES[DEFAULT_SIZE])
    return apply_tax(base_price)


def get_order(order_id: int) -> dict | None:
    """Retrieve an order by its ID.

    Args:
        order_id: The unique identifier of the order.

    Returns:
        dict | None: A dictionary containing order details if found, None otherwise.
            The dictionary contains:
            - 'id' (int): Order ID
            - 'customer_name' (str): Customer's name
            - 'size' (str): Drink size
            - 'total_price' (float): Total price paid
            - 'order_time' (datetime): When the order was placed
            - 'item' (dict): Menu item details with 'name' and 'description'

    Raises:
        sqlite3.Error: If there's an issue with the database operation.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.customer_name, o.size, o.total_price, o.order_time,
                   m.name, m.description
            FROM orders o
            JOIN menu_items m ON o.item_id = m.id
            WHERE o.id = ?
        """, (order_id,))
        order = cursor.fetchone()
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
    """Redirect to the order creation page."""
    return redirect(url_for('create_order'))


@app.route('/order', methods=['GET', 'POST'])
def create_order():
    """Handle order creation - display form on GET, process order on POST."""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        item_id = request.form.get('item_id')
        size = request.form.get('size', DEFAULT_SIZE)
        
        if not customer_name or not item_id:
            return "Missing required fields: customer_name and item_id are required", 400
            
        total_price = calculate_price_by_size(size)
        order_id = create_order_record(customer_name, item_id, size, total_price)
        return redirect(url_for('order_success', order_id=order_id))
    
    items = get_menu_items()
    return render_template('order.html', items=items)


@app.route('/order/<int:order_id>/success')
def order_success(order_id: int):
    """Display the order success page."""
    order = get_order(order_id)
    if not order:
        return "Order not found", 404
    return render_template('success.html', order=order)


@app.route('/debug')
def debug_menu():
    """Display all orders for debugging purposes."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.customer_name, o.size, o.total_price, o.order_time,
                   m.name
            FROM orders o
            JOIN menu_items m ON o.item_id = m.id
            ORDER BY o.order_time DESC
        """)
        orders = cursor.fetchall()
    
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
    """Clear all orders from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders")
        conn.commit()
    return redirect(url_for('debug_menu'))


def init_db() -> None:
    """Initialize the database with required tables and seed data.

    Creates the menu_items and orders tables if they don't exist,
    and populates menu_items with default coffee drinks if empty.
    """
    with sqlite3.connect(DB_FILE) as conn:
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


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
