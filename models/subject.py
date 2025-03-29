from models.database import db

class Subject(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # A subject can have multiple chapters.
    # Using a string reference to 'Chapter' avoids the need for an import here.
    chapters = db.relationship('Chapter', backref='subject', lazy=True)
