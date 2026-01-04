from flask import Flask, render_template, abort
import requests

app = Flask(__name__)

API_URL = "https://fakestoreapi.com/products"

@app.route('/')
def index():
    response = requests.get(API_URL)
    if response.status_code == 200:
        products = response.json()
        return render_template('index.html', products=products)
    return "Gagal memuat data", 500

@app.route('/category/<name>')
def category(name):
    # Mapping untuk menyesuaikan klik di HTML dengan database API
    category_map = {
        "electronics": "electronics",
        "jewelery": "jewelery",
        "men": "men's clothing",
        "women": "women's clothing"
    }
    
    # Ambil nama kategori asli untuk API
    api_name = category_map.get(name, name)
    response = requests.get(f"{API_URL}/category/{api_name}")
    
    if response.status_code == 200:
        products = response.json()
        
        # Logika Tambahan: Jika klik Men atau Women, tampilkan outfit (jaket/kaos)
        # Jika electronics/jewelery, tampilkan semua tanpa filter
        if name in ['men', 'women']:
            # Filter hanya item yang punya kata 'jacket', 'shirt', 't-shirt', 'short', 'slim', atau 'backpack'
            products = [p for p in products if any(x in p['title'].lower() for x in ['jacket', 'shirt', 't-shirt', 'short', 'slim', 'backpack'])]
            
        return render_template('index.html', products=products)
    
    return "Kategori tidak ditemukan", 404

@app.route('/product/<int:product_id>')
def detail(product_id):
    response = requests.get(f"{API_URL}/{product_id}")
    if response.status_code == 200:
        product = response.json()
        if not product:
            abort(404)
        return render_template('detail.html', product=product)
    return "Produk tidak ditemukan", 404

if __name__ == '__main__':
    app.run(debug=True)