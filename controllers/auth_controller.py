from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import logout_user  # Import logout_user from flask_login
from models.database import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, full_name=full_name, qualification=qualification, dob=dob)
        new_user.set_password(password)  # Store hashed password
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # Verify password
            session['user_id'] = user.id
            session['username'] = user.username
            if user.username == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.user_dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
    return render_template('login.html')
