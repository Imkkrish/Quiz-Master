import os  
from flask import Flask, render_template, flash, session, redirect, url_for
from models.database import db, init_db
from werkzeug.security import generate_password_hash
from controllers.auth_controller import auth_bp
from controllers.question_controller import question_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from controllers.api_controller import api_bp
from dotenv import load_dotenv  


load_dotenv()

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'  # Convert to bool


db.init_app(app)

with app.app_context():
    init_db(app) 

    from models.user import User
    
    admin = User.query.filter_by(username='ghanshyam@admin.org').first()
    if not admin:
        admin = User(username='ghanshyam@admin.org', full_name='Admin', qualification='Admin', dob='2000-01-01')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


app.register_blueprint(auth_bp)
app.register_blueprint(question_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(api_bp)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
