from models.database import db

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.String(4), nullable=False)  # Use String(4)
    score = db.Column(db.Integer, nullable=False)
