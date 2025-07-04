from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    race = db.Column(db.String(50), nullable=False, default='Unknown')
    skill = db.Column(db.String(100), nullable=False, default='None')
    status = db.Column(db.String(20), nullable=False, default='active')
    gender = db.Column(db.String(10), nullable=False, default='Laki-laki')
    rank = db.Column(db.String(1), nullable=False, default='F')

    photo = db.Column(db.LargeBinary, nullable=True) 
    photo_mimetype = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Hero {self.id}: {self.name}>'