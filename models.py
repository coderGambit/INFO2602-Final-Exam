from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20000), nullable=False)
    category = db.Column(db.String(2000))
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(1000))
    about = db.Column(db.String(10000))
    cart = db.relationship("Cart", uselist=False)
    #added extras
    brandName = db.Column(db.String(500))
    shippingWeight = db.Column(db.String(50))


    def toDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "image": self.image,
            "about": self.about,
            "cart": self.cart
        }

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def toDict(self):
        return {
            "id":self.id,
            "quantity": self.quantity,
            "product_id": self.product_id
        }