from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_of_animal = db.Column(db.String(64))

    def __init__(self, id, type_of_animal):
        self.type_of_animal = type_of_animal

    def __repr__(self):
        return "<Category {}>".format(self.type_of_animal)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    photoUrls = db.Column(db.Text)
    status = db.Column(db.String(30))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(Category)

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

    def __repr__(self):
        return "<Pet {}>".format(self.id)
