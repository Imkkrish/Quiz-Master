# models/chapter.py
from models.database import db

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)
