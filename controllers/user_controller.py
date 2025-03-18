from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from sqlalchemy import func
from models.quiz import Quiz
from models.score import Score
from models.database import db
from models.question import Question
from models.user_response import UserResponse  # Ensure this model is defined and imported

user_bp = Blueprint('user', __name__)
@user_bp.route('/user_dashboard', endpoint='user_dashboard')
def user_dashboard():
    if 'username' not in session:
        flash("You must be logged in to view this page", "warning")
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    # Calculate actual statistics
    total_score = db.session.query(func.sum(Score.score)).filter(Score.user_id == user_id).scalar() or 0
    attempted_count = Score.query.filter(Score.user_id == user_id).count()
    total_quizzes = Quiz.query.count()
    
    # Debug info
    print(f"Debug - User ID: {user_id}")
    print(f"Debug - Total Score: {total_score}")
    print(f"Debug - Attempted Count: {attempted_count}")
    print(f"Debug - Total Quizzes: {total_quizzes}")
    
    return render_template('user_dashboard.html', 
                           total_score=total_score,
                           attempted_count=attempted_count,
                           total_quizzes=total_quizzes)

@user_bp.route('/attempt_quiz/<string:quiz_code>', methods=['GET', 'POST'])
def attempt_quiz(quiz_code):
    quiz = Quiz.query.filter_by(code=quiz_code).first_or_404()

    questions = sorted(quiz.questions, key=lambda q: q.id)
    total_questions = len(questions)
    current_index = request.args.get('q', default=0, type=int)

    if current_index >= total_questions:
        score_value = 0
        user_id = session.get('user_id')

        for question in questions:
            response = UserResponse.query.filter_by(
                user_id=user_id, quiz_id=quiz.code, question_id=question.id
            ).first()
            if response and response.answer.strip().upper() == question.correct_answer.strip().upper():
                score_value += 1

        existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz.code).first()
        if not existing_score:
            new_score = Score(user_id=user_id, quiz_id=quiz.code, score=score_value)
            db.session.add(new_score)
            db.session.commit()
            flash(f'Quiz completed! Your score: {score_value}', 'success')
        else:
            flash("You have already submitted this quiz.", "info")

        return redirect(url_for('user.user_quizzes'))

    current_question = questions[current_index]
    existing_response = UserResponse.query.filter_by(
        user_id=session.get('user_id'), quiz_id=quiz.code, question_id=current_question.id
    ).first()

    if request.method == 'POST':
        user_answer = request.form.get('answer')

        if not user_answer:
            flash("Please select an answer before proceeding.", "warning")
            return redirect(url_for('user.attempt_quiz', quiz_code=quiz.code, q=current_index))

        if not existing_response:
            new_response = UserResponse(
                user_id=session.get('user_id'), quiz_id=quiz.code, question_id=current_question.id, answer=user_answer
            )
            db.session.add(new_response)
            db.session.commit()
        else:
            flash("You have already answered this question. Moving to the next one.", "info")

        return redirect(url_for('user.attempt_quiz', quiz_code=quiz.code, q=current_index + 1))

    if existing_response:
        flash("You have already answered this question. Moving to the next one.", "info")
        return redirect(url_for('user.attempt_quiz', quiz_code=quiz.code, q=current_index + 1))

    options = [opt.strip() for opt in current_question.options.split(',')]

    return render_template('attempt_quiz.html', quiz=quiz, question=current_question, 
                           q_index=current_index, total=total_questions, options=options)

@user_bp.route('/view_scores')
def view_scores():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    scores = Score.query.filter_by(user_id=user_id).all()

    return render_template('view_scores.html', scores=scores)

@user_bp.route('/user_quizzes')
def user_quizzes():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    quizzes = Quiz.query.order_by(func.random()).all()

    attempted = {score.quiz_id: score.score for score in Score.query.filter_by(user_id=user_id).all()}

    return render_template('user_quizzes.html', quizzes=quizzes, attempted=attempted)
