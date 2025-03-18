# Quiz Master - Flask App

## Overview
Quiz Master is a Flask-based web application that allows users to participate in quizzes. The app includes authentication, quiz management, and an admin panel for managing quizzes and users.

## Features
- User authentication (registration & login)
- Secure password hashing
- Quiz creation and management
- User dashboard
- Admin panel for quiz and user management
- SQLite database integration

## Technologies Used
- **Flask** (Backend framework)
- **Flask-SQLAlchemy** (ORM for database management)
- **Flask-Login** (User authentication)
- **Werkzeug Security** (Password hashing)
- **Python-dotenv** (Environment variable management)
- **Jinja2** (Templating engine)
- **SQLite** (Database)

## Installation
### 1. Clone the repository
```sh
git clone https://github.com/yourusername/quiz-master.git
cd quiz-master
```

### 2. Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the project root and add the following:
```
SECRET_KEY=your_super_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///quiz_master.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

### 5. Initialize Database
Run the following command to create necessary database tables:
```sh
python -c 'from app import db; db.create_all()'
```

### 6. Run the Application
```sh
python app.py
```
The app will be available at `http://127.0.0.1:5000/`

## Project Structure
```
quiz-master/
│-- app.py
│-- .env
│-- requirements.txt
│-- models/
│   ├── database.py
│   ├── user.py
│   ├── quiz.py
│   ├── question.py
│   ├── score.py
│-- controllers/
│   ├── auth_controller.py
│   ├── quiz_controller.py
│   ├── admin_controller.py
│   ├── user_controller.py
│-- templates/
│   ├── login.html
│   ├── register.html
│-- static/
│-- README.md
```

## Contribution
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.

