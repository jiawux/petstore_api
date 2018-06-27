from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

#pets json
pets = [
    {
          "id": 1,
          "category": {
            "id": 1,
            "name": "doggie"
          },
          "name": "doggie",
          "photoUrls": [
            "string1"
          ],
          "tags": [
            {
              "id": 1,
              "name": "doggie"
            }
          ],
          "status": "available"
     },
     {
          "id": 2,
          "category": {
            "id": 2,
            "name": "cat"
          },
          "name": "cat",
          "photoUrls": [
            "string2"
          ],
          "tags": [
            {
              "id": 2,
              "name": "category"
            }
          ],
          "status": "available"
          },
      {
          "id": 3,
          "category": {
            "id": 3,
            "name": "snake"
          },
          "name": "snake",
          "photoUrls": [
            "string3"
          ],
          "tags": [
            {
              "id": 3,
              "name": "snake"
            }
          ],
          "status": "available"
        }
]

petid = 3


#create pet
class Pet(Resource):

    # endpoint to add a new pet
    @app.route("/pet", methods=["POST"])
    def add_pet():
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("photoUrls")
        parser.add_argument("status")
        args = parser.parse_args()
        global petid
        petid += 1

        pet = {
            "name": args["name"],
            "id": petid,
            "category": {
              "id": petid,
              "name": args["name"]
            },
            "name": args["name"],
            "photoUrls": [
              args["photoUrls"]
            ],
            "tags": [
              {
                "id": petid,
                "name": args["name"]
              }
            ],
            "status": args["status"]
          }

        pets.append(pet)
        return jsonify(pet), 201

    # endpoint to get user detail by id
    @app.route("/pet/<pet_id>", methods=["GET"])
    def get(pet_id):
        for pet in pets:
            if (pet_id == str(pet["id"])):
                return jsonify(pet), 200

        return "Pet not found try id 1 through " + str(petid), 404

    # endpoint to show all pets
    @app.route("/pet", methods=["GET"])
    def get_user():
        return jsonify(pets)

    # endpoint to update user
    @app.route("/pet/<pet_id>", methods=["PUT"])
    def update_pet(pet_id):
        for pet in pets:
            if (pet_id == str(pet["id"])):
                parser = reqparse.RequestParser()
                parser.add_argument("name")
                parser.add_argument("photoUrls")
                parser.add_argument("status")
                args = parser.parse_args()

                pet["name"]= args["name"]
                pet["photoUrls"]= args["photoUrls"]
                pet["status"]= args["status"]

                return jsonify(pet), 200

        return "pet not found", 404

    @app.route("/")
    def hello():
        return "Hello World"

myPet = Pet()

if __name__ == '__main__':
    app.run(debug=True)
