from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import IntegrityError
import os, sqlite3

app = Flask(__name__)
#basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cr.sqlite')
db_path = os.path.join(os.path.dirname(__file__), 'category.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
#db_category_string = basedir + "category.db"
conn = sqlite3.connect(db_path)
print(conn)
db = SQLAlchemy(app)
print(db)
ma = Marshmallow(app)

#---------------------------------------------------------------------------

class Category(db.Model):
    id = db.Column("category_id", db.Integer, primary_key=True)
    type_of_animal = db.Column(db.String(64))

def __init__(id, type_of_animal):
    self.type_of_animal = type_of_animal
    self.id = id

db.create_all()
#define structure of response of endpoints
class CategorySchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'type_of_animal')

print("category_id")
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
dog = 1,"dog"
new_category = Category(dog)
db.session.add(new_category)
db.session.commit()
print("hello")

#new_category = Category.query.filter_by(type_of_animal="cat")
#category = category_schema.dump(new_category).data
#print(category)
