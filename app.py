from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for Flask-Login

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id


# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Dummy user data (replace with a database in production)
users_db = {'admin': {'password': 'admin123'}}


# Homepage
@app.route('/')
def index():
    return render_template('index.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists and the password is correct
        if username in users_db and users_db[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('admin'))
        else:
            return "Invalid username or password", 401

    return render_template('login.html')


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Admin Panel (Protected Route)
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
            conn.commit()

        return redirect(url_for('admin'))

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id DESC LIMIT 10")  # Fetch recent 10 products
        products = cursor.fetchall()

    return render_template('admin.html', products=products)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    name = request.form['name']
    price = float(request.form['price'])
    stock = int(request.form['stock'])

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        conn.commit()

    return redirect(url_for('admin'))


# Product Catalog
@app.route('/products')
def products():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', '')

    query = "SELECT * FROM products WHERE name LIKE ?"
    params = [f'%{search_query}%']

    if sort_by == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'stock_asc':
        query += " ORDER BY stock ASC"

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        products = cursor.fetchall()

    return render_template('products.html', products=products)


# Edit Product
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?",
                           (name, price, stock, product_id))
            conn.commit()

        return redirect(url_for('admin'))

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

    return render_template('edit_product.html', product=product)


# Delete Product - Fixed to handle DELETE requests properly
@app.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = sqlite3.connect('database.db')  # Update your database connection
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Debug mode enabled for development
