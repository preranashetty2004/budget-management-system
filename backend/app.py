from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Ensure the database directory exists
database_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(database_dir, exist_ok=True)

# Set the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(database_dir, "budget.db")}'
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

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

if __name__ == '__main__':
    app.run(debug=True)