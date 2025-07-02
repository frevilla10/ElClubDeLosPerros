from flask import Flask, render_template, request, redirect, session, url_for
import json
import mercadopago

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load products from JSON file
def load_products():
    with open('data/products.json', 'r') as f:
        return json.load(f)

# Configure Mercado Pago
sdk = mercadopago.SDK("YOUR_ACCESS_TOKEN")

@app.route('/')
def index():
    category = request.args.get('category')
    products = load_products()
    return render_template('index.html', products=products, selected_category=category)

@app.route('/product/<int:product_id>')
def product(product_id):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    products = load_products()
    cart_ids = session.get('cart', [])
    cart_items = [p for p in products if p['id'] in cart_ids]
    total = sum(p['price'] for p in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/checkout')
def checkout():
    products = load_products()
    cart_ids = session.get('cart', [])
    items = []
    for p in products:
        if p['id'] in cart_ids:
            items.append({
                "title": p['name'],
                "quantity": 1,
                "unit_price": float(p['price'])
            })
    preference_data = {"items": items}
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    return render_template('checkout.html', preference_id=preference["id"])

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
