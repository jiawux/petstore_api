from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

#----------------------------------------------------------------------------
#define the schema
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    photoUrls = db.Column(db.Text)
    status = db.Column(db.String(30))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __init__(self, id, name, photoUrls, status, category):
        self.id = id
        if name =="":
            name = "pet" + str(id)
        self.name = name
        self.photoUrls = photoUrls
        if status == "":
            status = "available"
        self.status = status
        self.category_id = category.id

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_of_animal = db.Column(db.String(64))
    pets = db.relationship('Pet', backref='category', lazy=True)

    def __init__(self, type_of_animal):
        self.type_of_animal = type_of_animal

#define structure of response of endpoints
class PetSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name', 'photoUrls', 'status')

pet_schema = PetSchema()
pets_schema = PetSchema(many=True)

Category("dog")
Category("cat")
Category("bunny")
Category("")

#----------------------------------------------------------------------------

# endpoint to add a new pet
@app.route("/pet/v2", methods=["POST"])
def add_pet():
    #try:
    parser = RequestParser()
    parser.add_argument("id", type=int, required = True)
    parser.add_argument("name", type=str, required=False)
    parser.add_argument("photoUrls", type=str, required=False)
    parser.add_argument("status", type=str,
        choices=["available", "pending", "sold"], required=True,
        help="Invalid. Status is either available, pending, or sold.")
    parser.add_argument("category", type=str,
        choices=["cat", "dog", "bunny"], required = False)
    args = parser.parse_args()

    category = Category.query.filter_by(type_of_animal="")
    print(category)

    if args["category"] is not None:
        category = Category.query.filter_by(type_of_animal=args["category"])
        print(category)

    new_pet = Pet(args["id"], args["name"], args["photoUrls"], args["status"],
        category)

    db.session.add(new_pet)
    db.session.commit()

    pet = pet_schema.dump(new_pet).data

    return jsonify(pet), 201
    #except IntegrityError as e:
         #return "invalid input", 405


# endpoint to get user detail by id
@app.route("/pet/v2/<pet_id>", methods=["GET"])
def get(pet_id):

    pet = pet_schema.dump(Pet.query.get(pet_id)).data

    if len(pet.keys()) > 0:
        return jsonify(pet), 200

    return "Pet not found", 404


# endpoint to show all pets
@app.route("/pet/v2/<pet_id>", methods=["DELETE"])
def delete_pets(pet_id):

    pet = Pet.query.get(pet_id)
    db.session.delete(pet)
    db.session.commit()

    return "Deleted pet with id#" + str(pet_id), 200

# endpoint to show all pets
@app.route("/pet/v2", methods=["GET"])
def get_pets():
    pets = pets_schema.dump(Pet.query.all()).data
    return jsonify(pets)

# endpoint to update user
@app.route("/pet/v2/<pet_id>", methods=["PUT"])
def update_pet(pet_id):

    #give error if id is invalid
    try:
        int(pet_id)
    except ValueError:
        return "invalid id supplied", 400

    pet = Pet.query.get(pet_id)
    pet_data = pet_schema.dump(pet).data

    if len(pet_data.keys()) > 0:
        parser = RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("photoUrls", type=str)
        parser.add_argument("status", type=str)
        args = parser.parse_args()

        if args["name"] is not None:
            pet.name = args["name"]

        if args["photoUrls"] is not None:
            pet.photoUrls = args["photoUrls"]

        if args["status"] is not None:
            pet.status = args["status"]

        updated_pet = pet_schema.dump(pet).data
        db.session.commit()

        return jsonify(updated_pet), 200

    #id doesn't match
    return "pet not found", 404
"""
# endpoint to update user
@app.route("/pet/v2/<category_type>", methods=["GET"])
def update_pet(category_type):
"""

if __name__ == '__main__':
    app.run(debug=True)
