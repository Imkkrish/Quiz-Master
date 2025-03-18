from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.user import User
from models.score import Score
from models.quiz import Quiz
from models.question import Question
from models.database import db
from sqlalchemy import func
import random

admin_bp = Blueprint('admin', __name__)

def generate_quiz_code():
    """Generate a unique random 4-digit code for the quiz."""
    while True:
        code = str(random.randint(1000, 9999))
        if not Quiz.query.filter_by(code=code).first():
            return code

@admin_bp.route('/manage_users')
def manage_users():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        quiz_name = request.form.get('quiz_name')
        question_text = request.form.get('question_1')
        option_a = request.form.get('option_1_a')
        option_b = request.form.get('option_1_b')
        option_c = request.form.get('option_1_c')
        option_d = request.form.get('option_1_d')
        correct_answer = request.form.get('correct_answer_1')
        
        # Generate a unique 4-digit code
        quiz_code = generate_quiz_code()
        
        # Create new quiz using the generated 4-digit code as primary key
        new_quiz = Quiz(code=quiz_code, name=quiz_name)
        db.session.add(new_quiz)
        db.session.commit()  # new_quiz.code is set
        
        # Build options string from non-empty inputs
        options_list = [opt for opt in [option_a, option_b, option_c, option_d] if opt]
        options_str = ",".join(options_list)
        
        # Create a new question with quiz_id = new_quiz.code
        new_question = Question(
            question_statement=question_text,
            options=options_str,
            correct_answer=correct_answer,
            quiz_id=new_quiz.code
        )
        db.session.add(new_question)
        db.session.commit()
        
        flash(f'Quiz added successfully. Quiz Code: {quiz_code}', 'success')
        return redirect(url_for('admin.manage_quizzes'))
    return render_template('add_quiz.html')

@admin_bp.route('/manage_quizzes')
def manage_quizzes():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    quizzes = Quiz.query.all()
    return render_template('manage_quizzes.html', quizzes=quizzes)

@admin_bp.route('/edit_quiz/<string:quiz_code>', methods=['GET', 'POST'])
def edit_quiz(quiz_code):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    
    quiz = Quiz.query.get_or_404(quiz_code)
    # For simplicity, assume one question per quiz.
    question = quiz.questions[0] if quiz.questions else None

    if request.method == 'POST':
        quiz_name = request.form.get('quiz_name')
        question_text = request.form.get('question_1')
        option_a = request.form.get('option_1_a')
        option_b = request.form.get('option_1_b')
        option_c = request.form.get('option_1_c')
        option_d = request.form.get('option_1_d')
        correct_answer = request.form.get('correct_answer_1')
        
        quiz.name = quiz_name
        if question:
            question.question_statement = question_text
            options_list = [opt for opt in [option_a, option_b, option_c, option_d] if opt]
            question.options = ",".join(options_list)
            question.correct_answer = correct_answer
        else:
            options_list = [opt for opt in [option_a, option_b, option_c, option_d] if opt]
            options_str = ",".join(options_list)
            question = Question(
                question_statement=question_text,
                options=options_str,
                correct_answer=correct_answer,
                quiz_id=quiz.code
            )
            db.session.add(question)
        db.session.commit()
        flash("Quiz updated successfully.", "success")
        return redirect(url_for('admin.manage_quizzes'))
    
    options_list = question.options.split(",") if question else ["", "", "", ""]
    return render_template('edit_quiz.html', quiz=quiz, question=question, options=options_list)

@admin_bp.route('/delete_quiz/<string:quiz_code>')
def delete_quiz(quiz_code):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    quiz = Quiz.query.get_or_404(quiz_code)
    # Delete associated questions
    for question in quiz.questions:
        db.session.delete(question)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully.", "success")
    return redirect(url_for('admin.manage_quizzes'))

@admin_bp.route('/view_scores_admin')
def view_scores_admin():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    # Aggregate total score per user.
    aggregated_scores = (
        db.session.query(
            Score.user_id,
            func.sum(Score.score).label("total_score")
        )
        .group_by(Score.user_id)
        .all()
    )
    results = []
    from models.user import User
    for user_id, total_score in aggregated_scores:
        user = User.query.get(user_id)
        results.append({
            "username": user.username,
            "full_name": user.full_name,
            "total_score": total_score
        })
    return render_template('view_scores_admin.html', aggregated_scores=results)
