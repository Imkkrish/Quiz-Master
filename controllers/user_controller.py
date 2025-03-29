from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from sqlalchemy import func
from models.quiz import Quiz
from models.score import Score
from models.database import db
from models.question import Question
from models.user_response import UserResponse  # Ensure this model exists
from models.user import User  # Import User to check active status
from models.subject import Subject
from models.chapter import Chapter
from datetime import date, datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/user_dashboard', endpoint='user_dashboard')
def user_dashboard():
    if 'username' not in session or 'user_id' not in session:
        flash("You must be logged in to view this page", "warning")
        return redirect(url_for('auth.login'))
    
    today = date.today()
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        flash("User not found", "warning")
        return redirect(url_for('auth.login'))
    
    # If the user is blocked, render the blocked account page.
    if not user.is_active:
        return render_template('blocked.html', user=user)
    
    # Performance metrics.
    total_score = db.session.query(func.sum(UserResponse.score)).filter(UserResponse.user_id == user_id).scalar() or 0
    attempted_count = UserResponse.query.filter_by(user_id=user_id).count()
    total_quizzes = Quiz.query.count()
    
    # Retrieve ongoing live quizzes (scheduled for today).
    live_quizzes = Quiz.query.filter(Quiz.date_of_quiz == today).all()
    # Retrieve upcoming quizzes (scheduled for future dates).
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz > today).order_by(Quiz.date_of_quiz.asc()).all()
    
    # Get all quiz codes the user has already attempted.
    attempted_responses = UserResponse.query.filter_by(user_id=user_id).all()
    attempted_quizzes = {response.quiz_code for response in attempted_responses}
    
    return render_template('dashboard/user_dashboard.html', 
                           total_score=total_score,
                           attempted_count=attempted_count,
                           total_quizzes=total_quizzes,
                           live_quizzes=live_quizzes,
                           upcoming_quizzes=upcoming_quizzes,
                           attempted_quizzes=attempted_quizzes,
                           today=today)

@user_bp.route('/user_quizzes')
def list_quiz_subjects():
    if 'username' not in session:
        flash("Please log in to attempt a quiz", "warning")
        return redirect(url_for('auth.login'))
    # Retrieve subjects that have at least one quiz.
    subjects = Subject.query.join(Subject.chapters).join(Chapter.quizzes).distinct().all()
    return render_template('users/quiz_subjects.html', subjects=subjects)

# 2. For a given subject, list chapters that have quizzes.
@user_bp.route('/user_quizzes/<subject_id>')
def list_quiz_chapters(subject_id):
    if 'username' not in session:
        flash("Please log in to attempt a quiz", "warning")
        return redirect(url_for('auth.login'))
    
    subject = Subject.query.get_or_404(subject_id)
    # Retrieve chapters in the subject that have at least one quiz.
    chapters = Chapter.query.filter(Chapter.subject_id == subject_id)\
                .join(Chapter.quizzes).distinct().all()
    
    # Note: We don't disable a chapter here.
    return render_template('users/quiz_chapters.html', subject=subject, chapters=chapters)

@user_bp.route('/user_quizzes/<subject_id>/<int:chapter_id>/quizzes')
def list_quizzes_for_chapter(subject_id, chapter_id):
    if 'username' not in session:
        flash("Please log in to attempt a quiz", "warning")
        return redirect(url_for('auth.login'))
    
    today = date.today()
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    if not quizzes:
        flash("No quizzes available in this chapter.", "warning")
        return redirect(url_for('user.list_quiz_chapters', subject_id=subject_id))
    
    user_id = session.get('user_id')
    attempted_responses = UserResponse.query.filter_by(user_id=user_id).all()
    attempted_quizzes = {response.quiz_code for response in attempted_responses}
    
    return render_template('users/list_quizzes.html', 
                       subject_id=subject_id, 
                       chapter_id=chapter_id, 
                       quizzes=quizzes, 
                       attempted_quizzes=attempted_quizzes,
                       today=today)

# 4. For a selected quiz, display the quiz questions.
@user_bp.route('/user_quizzes/<subject_id>/<int:chapter_id>/<quiz_code>')
def attempt_quiz(subject_id, chapter_id, quiz_code):
    if 'username' not in session:
        flash("Please log in to attempt a quiz", "warning")
        return redirect(url_for('auth.login'))
    
    today = date.today()
    quiz = Quiz.query.filter_by(code=quiz_code).first()
    if not quiz:
        flash("Quiz not found", "danger")
        return redirect(url_for('user.list_quizzes_for_chapter', subject_id=subject_id, chapter_id=chapter_id))
    
    # Restrict quiz attempts based on scheduled date.
    if quiz.date_of_quiz != today:
        if quiz.date_of_quiz > today:
            flash(f"This quiz is upcoming and will be live on {quiz.date_of_quiz.strftime('%Y-%m-%d')}.", "warning")
        else:
            flash("The quiz time has passed.", "warning")
        return redirect(url_for('user.list_quizzes_for_chapter', subject_id=subject_id, chapter_id=chapter_id))
    
    user_id = session.get('user_id')
    existing_response = UserResponse.query.filter_by(user_id=user_id, quiz_code=quiz.code).first()
    if existing_response:
        flash("You have already attempted this quiz.", "warning")
        return redirect(url_for('user.list_quizzes_for_chapter', subject_id=subject_id, chapter_id=chapter_id))
    
    questions = Question.query.filter_by(quiz_id=quiz.code).all()
    return render_template('users/attempt_quiz.html', quiz=quiz, questions=questions)
@user_bp.route('/submit_quiz/<quiz_code>', methods=['POST'])
def submit_quiz(quiz_code):
    if 'username' not in session or 'user_id' not in session:
        flash("You must be logged in to submit a quiz", "warning")
        return redirect(url_for('auth.login'))
    
    quiz = Quiz.query.filter_by(code=quiz_code).first()
    if not quiz:
        flash("Quiz not found", "danger")
        return redirect(url_for('user.user_dashboard'))
    
    user = User.query.get(session.get('user_id'))
    
    existing_response = UserResponse.query.filter_by(user_id=user.id, quiz_code=quiz.code).first()
    if existing_response:
        flash("You have already submitted this quiz!", "warning")
        return redirect(url_for('user.user_dashboard'))
    
    questions = Question.query.filter_by(quiz_id=quiz.code).all()
    correct_count = 0
    for question in questions:
        user_answer = request.form.get(f"q{question.id}")
        if user_answer and user_answer.strip() == question.correct_answer.strip():
            correct_count += 1
    
    total_questions = len(questions)
    score = correct_count
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    new_response = UserResponse(
        user_id=user.id,
        username=user.username,
        quiz_code=quiz.code,
        quiz_name=quiz.name,
        chapter_id=quiz.chapter_id,
        subject_id=quiz.chapter.subject.id,
        score=score,
        total_questions=total_questions,
        percentage=percentage
    )
    db.session.add(new_response)
    db.session.commit()
    
    flash(f"Quiz submitted! Your score is {score} out of {total_questions} ({percentage:.2f}%).", "success")
    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/view_scores')
def view_scores():
    if 'username' not in session or 'user_id' not in session:
        flash("Please log in to view scores", "warning")
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    subject_results = db.session.query(
        UserResponse.subject_id,
        func.sum(UserResponse.score).label('total_score'),
        func.sum(UserResponse.total_questions).label('total_questions')
    ).filter(UserResponse.user_id == user_id)\
     .group_by(UserResponse.subject_id).all()
    
    chapter_results = db.session.query(
        Chapter.name.label('chapter_name'),
        Subject.name.label('subject_name'),
        func.sum(UserResponse.score).label('total_score'),
        func.sum(UserResponse.total_questions).label('total_questions')
    ).join(Chapter, Chapter.id == UserResponse.chapter_id)\
     .join(Subject, Subject.id == Chapter.subject_id)\
     .filter(UserResponse.user_id == user_id)\
     .group_by(Chapter.name, Subject.name).all()
    
    quiz_results = db.session.query(
        UserResponse.quiz_code,
        func.sum(UserResponse.score).label('total_score'),
        func.sum(UserResponse.total_questions).label('total_questions')
    ).filter(UserResponse.user_id == user_id)\
     .group_by(UserResponse.quiz_code).all()
    
    return render_template('users/view_scores.html',
                           subject_results=subject_results,
                           chapter_results=chapter_results,
                           quiz_results=quiz_results)
