from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  # Secure password handling
import os

app = Flask(__name__)

# Ensure the database directory exists
database_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(database_dir, exist_ok=True)

# Set the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(database_dir, "budget.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for Flask-Login

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect unauthorized users to login

# User model (Only one definition)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)  # Store hashed passwords

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400

    new_user = User(username=data['username'])
    new_user.set_password(data['password'])  # Hash password
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# User Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):  # Check password securely
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# User Logout
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

# Protect routes
@app.route('/api/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Hello, {current_user.username}!"}), 200

# Define models
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    limit = db.Column(db.Float, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/api/income', methods=['POST'])
def add_income():
    data = request.get_json()
    new_income = Income(user_id=data['user_id'], amount=data['amount'], source=data['source'], date=data['date'])
    db.session.add(new_income)
    db.session.commit()
    return jsonify({"message": "Income added successfully"}), 201

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    new_expense = Expense(user_id=data['user_id'], amount=data['amount'], category=data['category'], date=data['date'])
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({"message": "Expense added successfully"}), 201

@app.route('/api/budgets', methods=['POST'])
@login_required
def add_budget():
    print(current_user.is_authenticated)  # Debugging
    if not current_user.is_authenticated:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.get_json()
    new_budget = Budget(user_id=current_user.id, category=data['category'], limit=data['limit'])
    db.session.add(new_budget)
    db.session.commit()
    return jsonify({"message": "Budget added successfully"}), 201


@app.route('/api/budgets', methods=['GET'])
@login_required
def get_budgets():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return jsonify([{"category": b.category, "limit": b.limit} for b in budgets]), 200

@app.route('/api/reports', methods=['GET'])
@login_required
def get_reports():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    categories = {}
    for expense in expenses:
        if expense.category in categories:
            categories[expense.category] += expense.amount
        else:
            categories[expense.category] = expense.amount
    return jsonify(categories), 200

if __name__ == '__main__':
    app.run(debug=True)
