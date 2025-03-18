from models.database import db

class Quiz(db.Model):
    code = db.Column(db.String(4), primary_key=True) 
    name = db.Column(db.String(120), nullable=False)
    

    questions = db.relationship('Question', backref='quiz', lazy=True)
