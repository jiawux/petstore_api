from flask import Flask, request, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

app = Flask(__name__)

#fake pet data
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

#create pet model
class Pet(Resource):

    # endpoint to add a new pet
    @app.route("/pet", methods=["POST"])
    def add_pet():
        parser = RequestParser()
        parser.add_argument("name", type=str, required=True)
        parser.add_argument("id", type=int, required = True)
        parser.add_argument("photoUrls", required=True)
        parser.add_argument("status", type=str, required=True)
        args = parser.parse_args()

        #if id isn't unique
        for pet in pets:
            if (pet["id"] == args["id"]):
                return "invalid input", 405

        pet = {
            "name": args["name"],
            "id": args["id"],
            "category": {
              "id": args["id"],
              "name": args["name"]
            },
            "name": args["name"],
            "photoUrls": [
              args["photoUrls"]
            ],
            "tags": [
              {
                "id": args["id"],
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

        return "Pet not found", 404

    # endpoint to show all pets
    @app.route("/pet", methods=["GET"])
    def get_user():
        return jsonify(pets)

    # endpoint to update user
    @app.route("/pet/<pet_id>", methods=["PUT"])
    def update_pet(pet_id):

        #give error if id is invalid
        try:
            int(pet_id)
        except ValueError:
            return "invalid id supplied", 400

        for pet in pets:
            if (pet_id == str(pet["id"])):
                parser = RequestParser()
                parser.add_argument("name", type=str, required=True)
                parser.add_argument("photoUrls", required=True)
                parser.add_argument("status", type=str, required=True)
                args = parser.parse_args()

                pet["name"]= args["name"]
                pet["photoUrls"]= args["photoUrls"]
                pet["status"]= args["status"]
                pet["category"]["name"] = args["name"]
                pet["tags"][0]["name"] = args["name"]

                return jsonify(pet), 200

        #id doesn't match
        return "pet not found", 404

    @app.route("/")
    def hello():
        return "Hello World"

myPet = Pet()

if __name__ == '__main__':
    app.run(debug=True)
