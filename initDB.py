from sqlalchemy.exc import IntegrityError

from main import app
from models import *
import csv
import uuid

db.create_all(app=app)


def getCSVFile():

    f = None

    try:
        f = open('products.csv', 'r')
    except Exception as e:

        try:
            f = open('../products.csv', 'r')
        except Exception as e:
            print(e)

    return f

def populateDatabase(csvFile):

    for line in csv.DictReader(csvFile):

        name = line['Product Name']
        category = line['Category']
        price = line['Selling Price']
        image = line['Image']
        about = line['About Product']
        shippingWeight = line["Shipping Weight"]
        brandName = line["Brand Name"]

        product = Product(id=uuid.uuid4().int & 0xfffff, name=name, category=category, price=price, image=image, about=about, brandName=brandName, shippingWeight=shippingWeight)
        db.session.add(product)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("database already initialized")



populateDatabase(getCSVFile())
print('database initialized!')