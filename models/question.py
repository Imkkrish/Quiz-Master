from models.database import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.String(255), nullable=False)
    options = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(10), nullable=False)
    quiz_id = db.Column(db.String(4), db.ForeignKey('quiz.code'), nullable=False)

    def get_options(self):
        return self.options.split(',')
