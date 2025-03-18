from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # With the app context, import all models so they register with SQLAlchemy before creating tables.
    with app.app_context():
        from models.user import User
        from models.quiz import Quiz
        from models.question import Question
        from models.score import Score
        db.create_all()
