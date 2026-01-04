from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # session secret

API_URL = "https://fakestoreapi.com/products"

# ====== Helper ======
def get_cart_items():
    return session.get('cart', {})

def cart_count():
    return sum(get_cart_items().values())

def cart_total():
    total = 0
    items = get_cart_items()
    for product_id, qty in items.items():
        res = requests.get(f"{API_URL}/{product_id}")
        if res.status_code == 200:
            total += res.json()['price'] * qty
    return round(total, 2)

# ====== Routes ======
@app.route('/')
def index():
    search_query = request.args.get('q', '')
    sort = request.args.get('sort', '')
    
    response = requests.get(API_URL)
    products = response.json() if response.status_code == 200 else []

    if search_query:
        products = [p for p in products if search_query.lower() in p['title'].lower()]

    if sort == 'price_asc':
        products.sort(key=lambda x: x['price'])
    elif sort == 'price_desc':
        products.sort(key=lambda x: x['price'], reverse=True)
    
    return render_template('index.html', products=products, cart_count=cart_count(), search_query=search_query)

@app.route('/category/<name>')
def category(name):
    category_map = {
        "electronics": "electronics",
        "jewelery": "jewelery",
        "men": "men's clothing",
        "women": "women's clothing"
    }
    api_name = category_map.get(name, name)
    res = requests.get(f"{API_URL}/category/{api_name}")
    products = res.json() if res.status_code == 200 else []
    return render_template('index.html', products=products, cart_count=cart_count())

@app.route('/product/<int:product_id>')
def detail(product_id):
    res = requests.get(f"{API_URL}/{product_id}")
    if res.status_code == 200:
        product = res.json()
        return render_template('detail.html', product=product, cart_count=cart_count())
    return "Product not found", 404

# ====== Cart Routes ======
@app.route('/cart')
def cart():
    cart_items = get_cart_items()
    items = []
    for product_id, qty in cart_items.items():
        res = requests.get(f"{API_URL}/{product_id}")
        if res.status_code == 200:
            product = res.json()
            product['qty'] = qty
            product['subtotal'] = round(product['price'] * qty, 2)
            items.append(product)
    total = round(sum([i['subtotal'] for i in items]), 2)
    return render_template('cart.html', items=items, total=total, cart_count=cart_count())

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart_items = get_cart_items()
    cart_items[str(product_id)] = cart_items.get(str(product_id), 0) + 1
    session['cart'] = cart_items
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart_items = get_cart_items()
    cart_items.pop(str(product_id), None)
    session['cart'] = cart_items
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    cart_items = get_cart_items()
    items = []
    for product_id, qty in cart_items.items():
        res = requests.get(f"{API_URL}/{product_id}")
        if res.status_code == 200:
            product = res.json()
            product['qty'] = qty
            product['subtotal'] = round(product['price'] * qty, 2)
            items.append(product)
    total = round(sum([i['subtotal'] for i in items]), 2)
    return render_template('checkout.html', items=items, total=total, cart_count=cart_count())

if __name__ == '__main__':
    app.run(debug=True)
