# controllers/quiz_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from models.user import User

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    total_users = User.query.filter(User.username != 'admin').count()
    total_quizzes = Quiz.query.count()
    return render_template('admin_dashboard.html', total_users=total_users, total_quizzes=total_quizzes)

@quiz_bp.route('/user_quizzes')
def user_quizzes():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user_id = session.get('user_id')
    # Retrieve all available quizzes in random order
    quizzes = Quiz.query.order_by(db.func.random()).all()
    # Retrieve the list of quiz codes that the current user has attempted
    attempted_quiz_codes = [score.quiz_id for score in Score.query.filter_by(user_id=user_id).all()]
    print("Attempted quiz codes for user", user_id, ":", attempted_quiz_codes)  # Debug print
    return render_template('user_quizzes.html', quizzes=quizzes, attempted=attempted_quiz_codes)
