from flask import Flask, render_template, redirect, url_for, session
import stripe

app = Flask(__name__)
app.secret_key = "your_secret_key"
stripe.api_key="your_secret_key"
products = [
    {"id": 1, "name": "Shoes", "price": 3000, "image": "shoe.jpg", "category": "Footwear"},
    {"id": 2, "name": "Bag", "price": 7500, "image": "Bag.jpg", "category": "Accessories"},
    {"id": 3, "name": "Watch", "price": 1500, "image": "watch.jpg", "category": "Accessories"},
    {"id": 4, "name": "Dress", "price": 799, "image": "Dress.jpg", "category": "Clothing"},
    {"id": 5, "name": "T-Shirt", "price": 339, "image": "t-shirt.jpg", "category": "Clothing"}
]

@app.route('/')
def home():
    return render_template("index.html", products=products)

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(id)
    session.modified = True
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    items = [p for p in products if p['id'] in cart_items]
    return render_template("cart.html", items=items)

@app.route('/checkout')
def checkout():
    cart_items = session.get('cart', [])
    items = [p for p in products if p['id'] in cart_items]

    total = sum(item['price'] for item in items)

    return render_template("checkout.html", items=items, total=total)

@app.route('/create-checkout-session')
def create_checkout_session():
    cart_items = session.get('cart', [])
    items = [p for p in products if p['id'] in cart_items]

    line_items = []

    for item in items:
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': item['price'] * 100,  # in paise
            },
            'quantity': 1,
        })

    session_stripe = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:5000/success',
        cancel_url='http://127.0.0.1:5000/cancel',
    )

    return redirect(session_stripe.url)

@app.route('/success')
def success():
    session.pop('cart', None)  # clear cart
    return render_template("success.html")

@app.route('/cancel')
def cancel():
    return "<h1>Payment Cancelled ❌</h1>"



if __name__ == "__main__":
    app.run(debug=True)