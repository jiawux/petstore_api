from flask import Flask, request, jsonify, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful.reqparse import RequestParser
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pets.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)

#----------------------------------------------------------------------------
#define the Model
"""
@event.listens_for(db.Table, "column_reflect")
def reflect_col(inspector, table, column_info):
    column_info['key'] = column_info['name'].replace(' ', '_')
"""
association_table = db.Table('association', db.metadata,
    db.Column('category_id', db.Integer, db.ForeignKey('category.category_id')),
    db.Column('pet_id', db.Integer, db.ForeignKey('pet.pet_id'))
)

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(150), nullable=False, unique=True)
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
        return "Pet {}".format(self.pet_id)
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


#----------------------------------------------------------------------------

@app.route('/category', methods=['GET','POST'])
def add_category():
    error=None
    if request.method == 'POST':

        category_name=request.form.get('category_name')

        try:
            if category_name!="":
                new_category = Category(category_name)

                db.session.add(new_category)
                db.session.commit()

                print(new_category)
                print(Category.query.filter_by(category_name=category_name).first())

                return redirect(url_for('home_page', pets = Pet.query.all(),
                    categories = Category.query.all()))
            else:
                error = "invalid category_name"
                return render_template('category.html', categories = Category.query.all(), error=error)
        except InvalidRequestError as e:
             return render_template('category.html', categories = Category.query.all(),
                error = "Invalid entries. Try again.")
        except IntegrityError as e:
             return render_template("pet.html", categories = Category.query.all(),
                error = "Entries must be unique. Try again.")

    return render_template('category.html', categories = Category.query.all())

@app.route('/category/delete/<category_name>', methods=['GET','DELETE'])
def delete_category(category_name):

    delete_category = Category.query.filter_by(category_name=category_name).first()
    db.session.delete(delete_category)
    db.session.commit()

    return '''<h3>
                 <a href = '{}'">Home Page</a>
              </h3>
              <h3>Deleted Category {}'''.format(url_for('home_page',
              pets = Pet.query.all(), categories = Category.query.all()), category_name)

# endpoint to update user
@app.route('/category/update/<category_name>', methods=['GET','POST'])
def update_category(category_name):

    if request.method == 'POST':

        category = Category.query.filter_by(category_name=category_name).first()
        category_name=request.form.get('category_name')

        try:
            if category_name!="":
                category.category_name = category_name

                updated_category = category_schema.dump(category).data
                db.session.commit()

                return redirect(url_for('home_page', pets = Pet.query.all(),
                    categories = Category.query.all()))
            else:
                return render_template('category.html', categories=Category.query.all(),
                    error = "Please fill out the input fields.")
        except IntegrityError as e:
             return render_template('category.html', categories = Category.query.all(),
                error = "Entries must be unique. Try again.")

    print(category_name)
    return render_template('category.html', categories = Category.query.all())

# endpoint to show all pets with specific category
@app.route('/category.pets/<category_name>', methods=['GET'])
def get_all_pets_by_category(category_name):
    error=None
    category = Category.query.filter_by(category_name=category_name).first()
    pets = category.pets

    if pets ==[]:
        error = "This category does not contain any pets."

    return render_template('pets_by_category.html', category_name=category_name,
        pets = pets, error=error )

#---------------------------------------------------------------------------
# endpoint to add a new pet
@app.route('/pet', methods=['GET','POST'])
def pet():
    if request.method == "POST":

        pet_name = request.form.get('pet_name')
        photoUrls = request.form.get('photoUrls')
        status = request.form.get('status')
        category = request.form.get('category')


        pet_category = Category.query.filter_by(category_name=category).first()
        pet_category_data = category_schema.dump(pet_category).data

        if pet_name=='':
            return render_template("pet.html", categories = Category.query.all(),
                error = "Please fill out the name field.")


        try:
            new_pet = Pet(pet_name, photoUrls, status)

            if (len(pet_category_data.keys()) > 0):
                print("we got hERE")
                pet_category.pets.append(new_pet)

            db.session.add(new_pet)
            db.session.commit()

            return redirect(url_for('home_page', pets = Pet.query.all(),
             categories = Category.query.all()))

        except IntegrityError as e:
             return render_template("pet.html", categories = Category.query.all(),
                error = "Entries must be unique. Try again.")

    return render_template("pet.html", categories = Category.query.all())

@app.route('/pet/delete/<int:pet_id>', methods=['GET','DELETE'])
def delete_pet(pet_id):

    pet = Pet.query.get(pet_id)
    db.session.delete(pet)
    db.session.commit()

    return '''<h3>
                 <a href = '{}'">Home Page</a>
              </h3>
              <h3>Deleted Pet {}'''.format(url_for('home_page',
              pets = Pet.query.all(), categories = Category.query.all()), pet_id)


# endpoint to update user
@app.route('/pet/update/<int:pet_id>', methods=['GET','POST'])
def update_pet(pet_id):


    if request.method == 'POST':
        pet = Pet.query.get(pet_id)

        pet_name = request.form.get('pet_name')
        photoUrls = request.form.get('photoUrls')
        status = request.form.get('status')
        delta = request.form.get('type of category change')
        category_id = request.form.get('category')

        if pet_name != "":
            pet.pet_name = pet_name

        if photoUrls != "":
            pet.photoUrls = photoUrls

        if status != pet.status:
            pet.status = status

        new_category = Category.query.get(category_id)

        if delta == 'add':
            new_category.pets.append(pet)
        elif delta == 'delete':
            if pet in new_category.pets:
                new_category.pets.remove(pet)

        db.session.commit()
        return redirect(url_for('home_page', pets = Pet.query.all(),
         categories = Category.query.all()))

    return render_template("update_pet.html", categories = Category.query.all())


@app.route('/')
def home_page():
#   return render_template('home_page.html', pets = Pet.query.all(),
#    categories = Category.query.all())
    return render_template('sequence_diagram.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
