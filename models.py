from app import db

#define inital model  
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    photoUrls = db.Column(db.String(200), index=True, unique=True)
    status = db.Column(db.String(15))
    #category = db.Column({"id": id, "name": name})
    #tags = db.Column([{"id": id, "name": name}])

    def __init__(self, name, photoUrls, status):
        self.name = name
        self.photoUrls = photoUrls
        self.status = status


    def __repr__(self):
        return '<Pet {}>'.format(self.name)
