from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pet.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)

#----------------------------------------------------------------------------
#define the Model

association_table = db.Table('association', db.metadata,
    db.Column('category_id', db.Integer, db.ForeignKey('category.category_id')),
    db.Column('pet_id', db.Integer, db.ForeignKey('pet.pet_id'))
)

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(64), unique=True)
    pets = db.relationship('Pet', secondary=association_table, back_populates='categories')

    def __init__(self, category_name):
        self.category_name = category_name

    def __repr__(self):
        return "Category {}".format(self.category_name)

class Pet(db.Model):
    __tablename__ = 'pet'
    pet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_name = db.Column(db.String(64), nullable=False)
    photoUrls = db.Column(db.Text)
    status = db.Column(db.String(30))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    categories = db.relationship('Category', secondary=association_table, back_populates='pets')

    def __init__(self, pet_name, photoUrls, status):
         self.pet_name = pet_name
         self.photoUrls = photoUrls
         self.status = status

    def __repr__(self):
        return "Pet {}".format(self.pet_name)

#define structure of response of endpoints
class PetSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('pet_id', 'pet_name', 'photoUrls', 'status')

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

@app.route('/category', methods=['POST'])
def add_category():
    parser = RequestParser()
    parser.add_argument('category_name', type=str, required=True)
    args = parser.parse_args()

    new_category = Category( args['category_name'])

    db.session.add(new_category)
    db.session.commit()

    global category_names
    category_names.append(args['category_name'])

    return jsonify(category_schema.dump(new_category).data), 200

# endpoint to show all categories
@app.route('/category', methods=['GET'])
def get_categories():
    categories = categories_schema.dump(Category.query.all()).data
    return jsonify(categories)

# endpoint to show category
@app.route('/category/<category_name>', methods=['GET'])
def get_category_by_name(category_name):
    category = Category.query.filter_by(category_name=category_name).first()

    return jsonify(category_schema.dump(category).data)

# endpoint to show all pets with specific category
@app.route('/category.pets/<category_name>', methods=['GET'])
def get_all_pets_by_category(category_name):
    category = Category.query.filter_by(category_name=category_name).first()
    pets = category.pets

    return jsonify(pets_schema.dump(pets).data)

@app.route('/category/<category_name>', methods=['DELETE'])
def delete_category(category_name):

    delete_category = Category.query.filter_by(category_name=category_name).first()
    db.session.delete(delete_category)
    db.session.commit()

    global category_names
    category_names.remove(category_name)

    return 'Deleted category ' + str(category_name), 200

# endpoint to update user
@app.route('/category/<category_name>', methods=['PUT'])
def update_category(category_name):

    category = Category.query.filter_by(category_name=category_name).first()

    parser = RequestParser()
    parser.add_argument('category_name', type=str, required=False)
    args = parser.parse_args()

    if args['category_name'] is not None:
        category.category_name = args['category_name']

    updated_category = category_schema.dump(category).data
    db.session.commit()

    return jsonify(updated_category)

#---------------------------------------------------------------------------
# endpoint to add a new pet
@app.route('/pet', methods=['POST'])
def add_pet():
    try:
         parser = RequestParser()
         parser.add_argument('pet_name', type=str, required=False)
         parser.add_argument('photoUrls', type=str, required=False)
         parser.add_argument('status', type=str,
            choices=['available', 'pending', 'sold'], required=True,
             help='Invalid. Status is either available, pending, or sold.')
         parser.add_argument('category', type=str, choices=category_names,
             required=True)
         args = parser.parse_args()

         pet_category = Category.query.filter_by(category_name=args['category']).first()
         new_pet = Pet(args['pet_name'], args['photoUrls'], args['status'])
         pet_category.pets.append(new_pet)

         db.session.add(new_pet)
         db.session.commit()

         return jsonify(pet_schema.dump(new_pet).data), 200

    except IntegrityError as e:
          return 'invalid input', 405


# endpoint to get user detail by id
@app.route('/pet/<int:pet_id>', methods=['GET'])
def get_pet_by_id(pet_id):

    pet = Pet.query.get(pet_id)
    pet_category = pet.categories
    pet_data = pet_schema.dump(pet).data
    pet_category_data = categories_schema.dump(pet_category).data
    data = [pet_data, pet_category_data]

    if len(pet_data.keys()) > 0:
        return jsonify(data), 200

    return 'Pet not found', 404

# endpoint to show all pets
@app.route('/pet', methods=['GET'])
def get_pets():
    pets = pets_schema.dump(Pet.query.all()).data
    return jsonify(pets)


@app.route('/pet/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):

    pet = Pet.query.get(pet_id)
    db.session.delete(pet)
    db.session.commit()

    return 'Deleted pet with id#' + str(pet_id), 200


# endpoint to update user
@app.route('/pet/<int:pet_id>', methods=['PUT'])
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
        parser.add_argument('pet_name', type=str, required=False)
        parser.add_argument('photoUrls', type=str, required=False)
        parser.add_argument('status', type=str,
            choices=['available', 'pending', 'sold'], required=False,
            help='Invalid. Status is either available, pending, or sold.')
        parser.add_argument('type of category change', type=str, required=False,
            choices=['delete', 'add'])
        parser.add_argument('category', type=str, choices=category_names,
            required=False)
        args = parser.parse_args()

        if args['pet_name'] is not None:
            pet.pet_name = args['pet_name']

        if (args['type of category change'] is not None):
            if (args['category'] is not None):

                category = Category.query.filter_by(category_name=args['category']).first()

                if (args['type of category change'] == 'add'):
                    category.pets.append(pet)
                else:
                    category.pets.remove(pet)

        if args['photoUrls'] is not None:
            pet.photoUrls = args['photoUrls']

        if args['status'] is not None:
            pet.status = args['status']

        db.session.commit()

        return get_pet_by_id(pet_id)

    #id doesn't match
    return 'pet not found', 404


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
