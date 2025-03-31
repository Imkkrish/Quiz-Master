from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.quiz import Quiz
from models.question import Question
from models.database import db

question_bp = Blueprint('question', __name__)

@question_bp.route('/questions/add/<string:quiz_code>', methods=['GET', 'POST'])
def add_question(quiz_code):

    if 'username' not in session or session.get('username') != 'ghanshyam@admin.org':
        return redirect(url_for('auth.login'))
    
    quiz = Quiz.query.get_or_404(quiz_code)
    
    if request.method == 'POST':
        question_statement = request.form.get('question_1')
        option_a = request.form.get('option_1_a')
        option_b = request.form.get('option_1_b')
        option_c = request.form.get('option_1_c')
        option_d = request.form.get('option_1_d')
        # Depending on your form setup you might receive the correct answer as a text field or from a radio button.
        correct_answer = request.form.get('correct_answer_1')
        
        # Prepare the options string (comma separated).
        options_list = [opt for opt in [option_a, option_b, option_c, option_d] if opt]
        options_str = ",".join(options_list)
        
        # Create the new Question instance.
        new_question = Question(
            quiz_id=quiz_code,
            question_statement=question_statement,
            options=options_str,
            correct_answer=correct_answer
        )
        db.session.add(new_question)
        db.session.commit()
        
        flash("Question added successfully.", "success")
        return redirect(url_for('question.list_questions', quiz_code=quiz_code))
    
    # For GET requests, render the question creation template.
    return render_template('question/add.html', quiz=quiz)


@question_bp.route('/questions/list/<string:quiz_code>', methods=['GET'])
def list_questions(quiz_code):
    # Ensure admin access.
    if 'username' not in session or session.get('username') != 'ghanshyam@admin.org':
        return redirect(url_for('auth.login'))
    
    quiz = Quiz.query.get_or_404(quiz_code)
    questions = Question.query.filter_by(quiz_id=quiz_code).all()
    return render_template('question/list.html', quiz=quiz, questions=questions)


@question_bp.route('/questions/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    # Ensure admin access.
    if 'username' not in session or session.get('username') != 'ghanshyam@admin.org':
        return redirect(url_for('auth.login'))
    
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_answer = request.form.get('correct_answer')
        
        options_list = [opt for opt in [option_a, option_b, option_c, option_d] if opt]
        question.options = ",".join(options_list)
        question.correct_answer = correct_answer
        
        db.session.commit()
        flash("Question updated successfully.", "success")
        return redirect(url_for('question.list_questions', quiz_code=question.quiz_id))
    
    # Convert the options string into a list (for pre-filling the edit form).
    options = question.options.split(",") if question.options else ["", "", "", ""]
    return render_template('question/edit.html', question=question, options=options)


@question_bp.route('/questions/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    # Ensure admin access.
    if 'username' not in session or session.get('username') != 'ghanshyam@admin.org':
        return redirect(url_for('auth.login'))
    
    question = Question.query.get_or_404(question_id)
    quiz_code = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully.", "success")
    return redirect(url_for('question.list_questions', quiz_code=quiz_code))
