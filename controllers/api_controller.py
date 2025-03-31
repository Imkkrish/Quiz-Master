from flask import Blueprint, request, jsonify
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.database import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    subject_list = [{
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    } for subject in subjects]
    return jsonify(subject_list), 200

@api_bp.route('/subjects', methods=['POST'])
def create_subject():
    data = request.get_json()
    new_subject = Subject(
        id=data.get('id'),
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(new_subject)
    db.session.commit()
    return jsonify({'message': 'Subject created successfully'}), 201

@api_bp.route('/subjects/<subject_id>', methods=['GET'])
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }), 200

@api_bp.route('/subjects/<subject_id>', methods=['PUT'])
def update_subject(subject_id):
    data = request.get_json()
    subject = Subject.query.get_or_404(subject_id)
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    db.session.commit()
    return jsonify({'message': 'Subject updated successfully'}), 200

@api_bp.route('/subjects/<subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'message': 'Subject deleted successfully'}), 200

@api_bp.route('/chapters', methods=['GET'])
def get_chapters():
    chapters = Chapter.query.all()
    chapter_list = [{
        'id': chapter.id,
        'name': chapter.name,
        'subject_id': chapter.subject_id
    } for chapter in chapters]
    return jsonify(chapter_list), 200

@api_bp.route('/chapters', methods=['POST'])
def create_chapter():
    data = request.get_json()
    new_chapter = Chapter(
        name=data.get('name'),
        subject_id=data.get('subject_id')
    )
    db.session.add(new_chapter)
    db.session.commit()
    return jsonify({'message': 'Chapter created successfully'}), 201

@api_bp.route('/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    quiz_list = [{
        'code': quiz.code,
        'name': quiz.name,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.isoformat(),
        'time_duration': quiz.time_duration,
        'remarks': quiz.remarks
    } for quiz in quizzes]
    return jsonify(quiz_list), 200

@api_bp.route('/quizzes', methods=['POST'])
def create_quiz():
    data = request.get_json()
    new_quiz = Quiz(
        code=data.get('code'),
        name=data.get('name'),
        chapter_id=data.get('chapter_id'),
        date_of_quiz=data.get('date_of_quiz'),
        time_duration=data.get('time_duration'),
        remarks=data.get('remarks')
    )
    db.session.add(new_quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz created successfully'}), 201
