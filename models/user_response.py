from datetime import datetime
from models.database import db

class UserResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)  # Add this column
    quiz_code = db.Column(db.String(4), nullable=False)
    quiz_name = db.Column(db.String(120), nullable=False)
    chapter_id = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    submitted_on = db.Column(db.DateTime, default=datetime.utcnow)
