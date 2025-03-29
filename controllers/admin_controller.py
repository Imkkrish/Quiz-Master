from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models.user import User
from datetime import datetime
from models.subject import Subject  # Ensure you have this model
from models.chapter import Chapter  # Already defined in your models
from models.quiz import Quiz
from models.question import Question
from models.score import Score
from models.database import db
from sqlalchemy import func
from models.user_response import UserResponse
import random

admin_bp = Blueprint('admin', __name__)

def generate_quiz_code():
    """Generate a unique random 4-digit code for the quiz."""
    while True:
        code = str(random.randint(1000, 9999))
        if not Quiz.query.filter_by(code=code).first():
            return code

# --- Admin Dashboard and Summary Charts ---
@admin_bp.route('/dashboard')
def dashboard():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    # Example summary data; replace with real chart data as needed.
    total_users = User.query.filter(User.username != 'admin').count()
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
    total_quizzes = Quiz.query.count()
    return render_template('dashboard/admin_dashboard.html', 
                           total_users=total_users, 
                           total_subjects=total_subjects,
                           total_chapters=total_chapters,
                           total_quizzes=total_quizzes)

# --- Subject Management ---
@admin_bp.route('/subjects')
def list_subjects():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    subjects = Subject.query.all()
    return render_template('subjects/list.html', subjects=subjects)

@admin_bp.route('/subjects/<subject_id>/chapters')
def subject_chapters(subject_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    # Get the subject (or return a 404 if not found)
    subject = Subject.query.get_or_404(subject_id)
    # Get all chapters associated with this subject
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    return render_template('chapters/list.html', subject=subject, chapters=chapters)

@admin_bp.route('/subjects/add', methods=['GET', 'POST'])
def add_subject():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        name = request.form.get('name')
        description = request.form.get('description')
        # Create a new subject using the custom subject ID
        new_subject = Subject(id=subject_id, name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully', 'success')
        return redirect(url_for('admin.list_subjects'))
    return render_template('subjects/add.html')

@admin_bp.route('/subjects/edit/<subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        subject.name = request.form.get('name')
        subject.description = request.form.get('description')
        db.session.commit()
        flash('Subject updated successfully', 'success')
        return redirect(url_for('admin.list_subjects'))
    return render_template('subjects/edit.html', subject=subject)

@admin_bp.route('/subjects/delete/<subject_id>')
def delete_subject(subject_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully', 'success')
    return redirect(url_for('admin.list_subjects'))

# --- Chapter Management ---
@admin_bp.route('/chapters')
def list_chapters():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    chapters = Chapter.query.all()
    return render_template('chapters/list.html', chapters=chapters)

@admin_bp.route('/chapters/add', methods=['GET', 'POST'])
def add_chapter():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form.get('name')
        subject_id = request.form.get('subject_id')
        new_chapter = Chapter(name=name, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully', 'success')
        return redirect(url_for('admin.list_chapters'))
    # Assuming you need a list of subjects to choose from:
    subjects = Subject.query.all()
    return render_template('chapters/add.html', subjects=subjects)

@admin_bp.route('/get_chapters/<subject_id>')
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    chapters_data = [{"id": chap.id, "name": chap.name} for chap in chapters]
    return jsonify(chapters_data)

@admin_bp.route('/chapters/edit/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.subject_id = request.form.get('subject_id')
        db.session.commit()
        flash('Chapter updated successfully', 'success')
        return redirect(url_for('admin.list_chapters'))
    subjects = Subject.query.all()
    return render_template('chapters/edit.html', chapter=chapter, subjects=subjects)

@admin_bp.route('/chapters/delete/<int:chapter_id>')
def delete_chapter(chapter_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('admin.list_chapters'))

# --- Quiz Management under a Chapter ---
@admin_bp.route('/quizzes/add', methods=['GET', 'POST'])
def add_quiz():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all subjects for the dropdown
    subjects = Subject.query.all()
    
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')
        quiz_name = request.form.get('quiz_name')
        date_of_quiz_str = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')
        
        # Convert date string to a Python date object
        if date_of_quiz_str:
            try:
                date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('admin.add_quiz'))
        else:
            date_of_quiz = None
        
        # Generate a unique quiz code
        quiz_code = generate_quiz_code()
        new_quiz = Quiz(
            code=quiz_code,
            name=quiz_name,
            chapter_id=chapter_id,  # Associate quiz with a chapter
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )
        db.session.add(new_quiz)
        db.session.commit()
        
        flash(f'Quiz "{quiz_name}" added successfully. Quiz Code: {quiz_code}', 'success')
        
        # Redirect to the question creation page for this quiz
        return redirect(url_for('question.add_question', quiz_code=quiz_code))
    
    # Render the quiz creation template with the list of subjects.
    return render_template('quizzes/add.html', subjects=subjects)

@admin_bp.route('/quizzes')
def list_quizzes():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    quizzes = Quiz.query.all()
    return render_template('quizzes/list.html', quizzes=quizzes)

@admin_bp.route('/quizzes/edit/<string:quiz_code>', methods=['GET', 'POST'])
def edit_quiz(quiz_code):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    quiz = Quiz.query.get_or_404(quiz_code)
    
    # Do not update question details in this route.
    if request.method == 'POST':
        quiz.name = request.form.get('quiz_name')
        quiz.remarks = request.form.get('remarks')
        
        # Convert the date if provided
        date_str = request.form.get('date_of_quiz')
        if date_str:
            from datetime import datetime
            try:
                quiz.date_of_quiz = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('admin.edit_quiz', quiz_code=quiz_code))
        else:
            quiz.date_of_quiz = None

        quiz.time_duration = request.form.get('time_duration')
        db.session.commit()
        flash("Quiz updated successfully.", "success")
        return redirect(url_for('admin.list_quizzes'))
    
    return render_template('quizzes/edit.html', quiz=quiz)

@admin_bp.route('/quizzes/delete/<string:quiz_code>')
def delete_quiz(quiz_code):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    quiz = Quiz.query.get_or_404(quiz_code)
    for question in quiz.questions:
        db.session.delete(question)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully.", "success")
    return redirect(url_for('admin.list_quizzes'))

@admin_bp.route('/manage_users')
def manage_users():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    # Retrieve all users from the database.
    users = User.query.all()
    return render_template('users/manage_users.html', users=users)
@admin_bp.route('/users/block/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    # Prevent blocking the admin account
    if user.username == 'admin':
        flash("Cannot block the admin.", "danger")
        return redirect(url_for('admin.manage_users'))
    user.is_active = False
    db.session.commit()
    flash("User blocked successfully.", "success")
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/activate/<int:user_id>', methods=['POST'])
def activate_user(user_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash("User activated successfully.", "success")
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # Update fields that you want the admin to be able to edit.
        user.full_name = request.form.get('full_name')
        user.qualification = request.form.get('qualification')
        user.dob = request.form.get('dob')
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for('admin.manage_users'))
    return render_template('users/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin.manage_users'))

# --- Search Functionality ---
@admin_bp.route('/search', methods=['GET'])
def search():
    if 'username' not in session or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))
    query = request.args.get('q', '')
    # Example search: search in users, subjects, and quizzes
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    return render_template('search_results.html', query=query, users=users, subjects=subjects, quizzes=quizzes)
@admin_bp.route('/scorecard')
def scorecard():
    if 'username' not in session or session.get('username') != 'admin':
        flash("Not authorized", "warning")
        return redirect(url_for('auth.login'))
    
    # Aggregate scores per subject
    subject_stats = db.session.query(
        UserResponse.subject_id,
        func.sum(UserResponse.score).label('total_score'),
        func.sum(UserResponse.total_questions).label('total_questions')
    ).group_by(UserResponse.subject_id).all()
    
    # Aggregate scores per chapter
    chapter_stats = db.session.query(
        UserResponse.chapter_id,
        func.sum(UserResponse.score).label('total_score'),
        func.sum(UserResponse.total_questions).label('total_questions')
    ).group_by(UserResponse.chapter_id).all()

    # Aggregate scores per quiz
    quiz_results = db.session.query(
        UserResponse.quiz_code,
        func.sum(UserResponse.score).label('total_score'),
        func.sum(UserResponse.total_questions).label('total_questions')
    ).group_by(UserResponse.quiz_code).all()

    # Fetch user-wise statistics
    user_stats = db.session.query(
        User.username,
        func.sum(UserResponse.score).label('total_score'),
        func.sum(UserResponse.total_questions).label('total_questions'),
        func.count(UserResponse.quiz_code).label('quizzes_attempted')
    ).join(UserResponse, User.id == UserResponse.user_id).group_by(User.username).all()

    # Find total users
    total_users = len(user_stats)

    # Calculate average accuracy
    total_correct = sum(user.total_score for user in user_stats if user.total_score is not None)
    total_questions = sum(user.total_questions for user in user_stats if user.total_questions is not None)
    average_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

    # Find top performer
    top_performer = max(user_stats, key=lambda u: u.total_score, default=None)

    return render_template('scorecard.html',
                           subject_stats=subject_stats,
                           chapter_stats=chapter_stats,
                           quiz_results=quiz_results,
                           user_stats=user_stats,
                           total_users=total_users,
                           average_accuracy=round(average_accuracy, 2),
                           top_performer=top_performer)
