from flask import Flask, request, jsonify
from flask_restful.reqparse import RequestParser
import json

app = Flask(__name__)

#fake pet data------------------------------------------------
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

#------------------------------------------------------------

# endpoint to add a new pet
@app.route("/pet/v1", methods=["POST"])
def add_pet():
    parser = RequestParser()
    parser.add_argument("name", type=str, required=True)
    parser.add_argument("id", type=int, required = True)
    parser.add_argument("photoUrls", required=True)
    parser.add_argument("status", type=str,
        choices=["available", "pending", "sold"], required=True,
        help="Invalid. Status is either available, pending, or sold.")
    args = parser.parse_args()

    #if id isn't unique
    for pet in pets:
        if (pet["id"] == args["id"]):
            return "invalid input", 405

    new_pet = {
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

    pets.append(new_pet)
    return jsonify(new_pet), 201

# endpoint to get user detail by id
@app.route("/pet/v1/<pet_id>", methods=["GET"])
def get(pet_id):

    #give error if id is invalid
    try:
        int(pet_id)
    except ValueError:
        return "invalid id supplied", 400

    for pet in pets:
        if (pet_id == str(pet["id"])):
            return jsonify(pet), 200

    return "Pet not found", 404

# endpoint to show all pets
@app.route("/pet/v1", methods=["GET"])
def get_pets():
    return jsonify(pets)

# endpoint to update user
@app.route("/pet/v1/<pet_id>", methods=["PUT"])
def update_pet(pet_id):

    #give error if id is invalid
    try:
        int(pet_id)
    except ValueError:
        return "invalid id supplied", 400

    for pet in pets:
        if (pet_id == str(pet["id"])):
            parser = RequestParser()
            parser.add_argument("name", type=str)
            parser.add_argument("photoUrls", type=str)
            parser.add_argument("status", type=str)
            #parser.add_argument("category", type = json.loads)
            args = parser.parse_args()

            if args["name"] is not None:
                pet["name"]= args["name"]
                pet["category"]["name"] = args["name"]
                pet["tags"][0]["name"] = args["name"]

            if args["photoUrls"] is not None:
                pet["photoUrls"]= args["photoUrls"]

            if args["status"] is not None:
                pet["status"]= args["status"]

            #pet["category"].update(args["category"].my_dict)

            return jsonify(pet), 200

    #id doesn't match
    return "pet not found", 404

@app.route("/v1")
def hello():
    return "Welcome to the Pet Store."


if __name__ == '__main__':
    app.run(debug=True)
