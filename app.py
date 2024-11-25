from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Allow CORS for all domains
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Employee model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create database
@app.before_first_request
def create_tables():
    db.create_all()

# API to create employee
@app.route('/api/employees', methods=['POST'])
def create_employee():
    data = request.json
    if not all(key in data for key in ('name', 'email', 'mobile', 'designation', 'gender', 'course')):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    # Validate email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400

    # Check for duplicate email
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already exists'}), 400

    new_employee = Employee(
        name=data['name'],
        email=data['email'],
        mobile=data['mobile'],
        designation=data['designation'],
        gender=data['gender'],
        course=data['course']
    )
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'success': True, 'employee': {'id': new_employee.id, 'name': new_employee.name}})

# API to get all employees
@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([{
        'id': emp.id,
        'name': emp.name,
        'email': emp.email,
        'mobile': emp.mobile,
        'designation': emp.designation,
        'gender': emp.gender,
        'course': emp.course,
        'created_at': emp.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for emp in employees])

if __name__ == '__main__':
    app.run(debug=True)