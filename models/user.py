from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db 

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120))
    dob = db.Column(db.String(10))  # Alternatively, use db.Date for actual date objects
    is_active = db.Column(db.Boolean, default=True)  # New column: active by default

    scores = db.relationship('Score', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
