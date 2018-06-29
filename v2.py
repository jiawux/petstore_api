from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pets.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)

#----------------------------------------------------------------------------
#define the Model

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(64), unique=True)
    pets = db.relationship('Pet', backref='category')

    def __init__(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name

    def __repr__(self):
        return 'Category {}'.format(self.category_name)

class Pet(db.Model):
    __tablename__ = 'pets'
    pet_id = db.Column(db.Integer, primary_key=True)
    pet_name = db.Column(db.String(64), nullable=False)
    photoUrls = db.Column(db.Text)
    status = db.Column(db.String(30))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))

    def __init__(self, pet_id, pet_name, photoUrls, status, category):
         self.pet_id = pet_id
         if pet_name =='':
             pet_name = 'pet' + str(id)
         self.pet_name = pet_name
         self.photoUrls = photoUrls
         if status == '':
             status = 'available'
         self.status = status


#define structure of response of endpoints
class PetSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('pet_id', 'pet_name', 'category_name', 'photoUrls', 'status')

class CategorySchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('category_id', 'category_name')

pet_schema = PetSchema()
pets_schema = PetSchema(many=True)

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

category_names = []


#----------------------------------------------------------------------------

@app.route('/v2/category', methods=['POST'])
def add_category():
    parser = RequestParser()
    parser.add_argument('category_id', type=int, required=True)
    parser.add_argument('category_name', type=str, required=True)
    args = parser.parse_args()

    new_category = Category(args['category_id'], args['category_name'])

    db.session.add(new_category)
    db.session.commit()

    global category_names
    category_names.append(args['category_name'])

    return jsonify(category_schema.dump(new_category).data), 200

# endpoint to show all categories
@app.route('/v2/category', methods=['GET'])
def get_categories():
    categories = categories_schema.dump(Category.query.all()).data
    return jsonify(categories)

# endpoint to show category
@app.route('/v2/category/<category_name>', methods=['GET'])
def get_category_by_name(category_name):
    category = Category.query.filter_by(category_name=category_name).first()
    return jsonify(categories)

# endpoint to show all pets with specific category
@app.route('/v2/pet/<category_name>', methods=['GET'])
def get_all_pet_by_category(category_name):
    pets = Pet.query.filter_by(category_name=category_name).all()
    return jsonify(pets_schema.dump(pets).data)

# endpoint to add a new pet
@app.route('/v2/pet', methods=['POST'])
def add_pet():
    try:
        parser = RequestParser()
        parser.add_argument('pet_id', type=int, required=True)
        parser.add_argument('pet_name', type=str, required=False)
        parser.add_argument('photoUrls', type=str, required=False)
        parser.add_argument('status', type=str,
            choices=['available', 'pending', 'sold'], required=True,
            help='Invalid. Status is either available, pending, or sold.')
        parser.add_argument('category', type=str, choices=category_names,
            required=True)
        args = parser.parse_args()

        pet_category = Category.query.filter_by(category_name=args['category']).first()

        print(pet_category.pets)

        new_pet = Pet(args['pet_id'], args['pet_name'], args['photoUrls'], args['status'])

        pet_category.pets.append(new_pet)

        db.session.add(new_pet)
        db.session.commit()

        print(pet_category.pets)

        return jsonify(pet_schema.dump(new_pet).data), 201

    except IntegrityError as e:
         return 'invalid input', 405


# endpoint to get user detail by id
@app.route('/v2/pet/<pet_id>', methods=['GET'])
def get(pet_id):

    pet = pet_schema.dump(Pet.query.get(pet_id)).data

    if len(pet.keys()) > 0:
        return jsonify(pet), 200

    return 'Pet not found', 404

# endpoint to show all pets
@app.route('/v2/pet', methods=['GET'])
def get_pets():
    pets = pets_schema.dump(Pet.query.all()).data
    print(pets)
    return jsonify(pets)

@app.route('/v2/pet/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):

    pet = Pet.query.get(pet_id)
    db.session.delete(pet)
    db.session.commit()

    return 'Deleted pet with id#' + str(pet_id), 200


# endpoint to update user
@app.route('/v2/pet/<pet_id>', methods=['PUT'])
def update_pet(pet_id):

    #give error if id is invalid
    try:
        int(pet_id)
    except ValueError:
        return 'invalid id supplied', 400

    pet = Pet.query.get(pet_id)
    pet_data = pet_schema.dump(pet).data

    if len(pet_data.keys()) > 0:
        parser = RequestParser()
        parser.add_argument('pet_name', type=str)
        parser.add_argument('photoUrls', type=str)
        parser.add_argument('status', type=str,
            choices=['available', 'pending', 'sold'],
            help='Invalid. Status is either available, pending, or sold.')
        parser.add_argument('category', type=str, choices=category_names,
            required=False)
        args = parser.parse_args()

        if args['pet_name'] is not None:
            pet.pet_name = args['pet_name']

        if args['category'] is not None:
            pet.category_name = args['category']

        if args['photoUrls'] is not None:
            pet.photoUrls = args['photoUrls']

        if args['status'] is not None:
            pet.status = args['status']

        updated_pet = pet_schema.dump(pet).data
        db.session.commit()

        return jsonify(updated_pet), 200

    #id doesn't match
    return 'pet not found', 404


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
