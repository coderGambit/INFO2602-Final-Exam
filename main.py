from flask_cors import CORS
from flask import Flask, request, render_template, redirect, flash, url_for, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, Product, Cart  # add application models
import uuid
import sys

''' Begin boilerplate code '''


def create_app():
    app = Flask(__name__, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = "MYSECRET"
    CORS(app)
    db.init_app(app)
    return app


app = create_app()

app.app_context().push()

''' End Boilerplate Code '''


# filters products based on search term provided
def product_search(search):
    # uncomment after models are implemented
     return Product.query.filter(
         Product.name.like( '%'+search+'%' )
         | Product.about.like( '%'+search+'%' )
         | Product.category.like( '%'+search+'%' ))


# calculates the total of all cart items based on quantity and price
def cart_total():
    total = 0
    cart = Cart.query.all()
    fullCartDetails = []

    for item in cart:
        product = Product.query.get(item.product_id)
        itemDetails = getItemDetails(item, product)

        total += product.price * item.quantity
        fullCartDetails.append(itemDetails)

    return round(total, 2), fullCartDetails


######################### Template Routes ##############################

@app.route('/')
def index():
    cartTotal, cart = cart_total()
    products = Product.query.all()
    return render_template('app.html', cart=cart, cartTotal=cartTotal, products=products)


########################### API Routes #############################

@app.route('/app')
def client_app():
    return app.send_static_file('app.html')


def getItemDetailsForCart(cartItem):
    itemDetails = getItemDetails(cartItem)
    return itemDetails


def getItemDetails(cartItem, product=None):
    itemDetails = {}

    if not product:
        product = Product.query.get(cartItem.product_id)

    itemDetails["name"] = product.name
    itemDetails["price"] = product.price
    itemDetails["quantity"] = cartItem.quantity
    itemDetails["id"] = product.id
    return itemDetails


@app.route('/search/<query>', methods=['GET'])
def search(query):
    products = product_search(query).all()

    if products is None:
        return "no results"

    productList = []
    for product in products:

        productDict = product.toDict()

        if productDict["cart"] is None:
            productDict["cart"] = {}

        else:
            productDict["cart"] = productDict["cart"].toDict()

        productList.append(productDict)

    return jsonify(productList)


@app.route('/addToCart/<productID>', methods=['PUT'])
def addToCart(productID):
    cartItem = Cart.query.filter_by(product_id=productID).first()
    response = None

    try:
        # item already exists
        if cartItem:
            cartItem.quantity += 1
            db.session.commit()
            # 0 indicates that the item was not inserted and should update existing item
            # cart_total[0] is the cart total
            response = {"added": 0}

        # add new item
        else:
            cartItem = Cart(id=uuid.uuid4().int & 0xfffff, quantity=1, product_id=productID)
            db.session.add(cartItem)
            db.session.commit()
            # 1 indicates that the iteam was inserted and the frontend should add a new cart item
            response = {"added": 1}

    except:
        return str(sys.exc_info()[0])

    response["cartTotal"] = cart_total()[0]
    response["itemDetails"] = getItemDetailsForCart(cartItem)
    return jsonify(response)


@app.route('/updateQuantity', methods=['POST'])
def updateQuantity():

    productID = next(request.form.keys()).split("-")[1]
    newQuantity = int(next(request.form.values()))
    cartItem = Cart.query.filter_by(product_id=productID).first()
    response = ""

    if cartItem.quantity != newQuantity:

        if newQuantity == 0:
            db.session.delete(cartItem)
        else:
            cartItem.quantity = newQuantity

        db.session.commit()
        response = "updated"

    else:
        response = "not updated"

    return response, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
