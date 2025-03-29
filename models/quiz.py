from models.database import db
from datetime import date

class Quiz(db.Model):
    code = db.Column(db.String(4), primary_key=True)  # Unique 4-digit code
    name = db.Column(db.String(120), nullable=False)
    
    # Foreign key linking this quiz to a chapter.
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    
    # Additional fields as per requirements.
    date_of_quiz = db.Column(db.Date, default=date.today)
    time_duration = db.Column(db.String(5))  # Format hh:mm
    remarks = db.Column(db.Text)
    
    # Relationship: A quiz can have multiple questions.
    questions = db.relationship('Question', backref='quiz', lazy=True)
