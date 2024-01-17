# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    email = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    id_number = db.Column(db.Integer, unique=True, nullable=False)
    role = db.Column(db.String(10), unique=False, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)

class Student(db.Model):
    adm_no = db.Column(db.String(8), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(28), unique=True, nullable=False)
    first_name = db.Column(db.String(15), unique=False, nullable=False)
    last_name = db.Column(db.String(15), unique=False, nullable=False)
    sir_name = db.Column(db.String(15), unique=False, nullable=False)
    id_number = db.Column(db.Integer, unique=True, nullable=False)
    campus = db.Column(db.String(15), unique=False, nullable=False)
    course = db.Column(db.String(15), unique=False, nullable=False)
    trimester = db.Column(db.String(15), unique=False, nullable=False)
    group = db.Column(db.String(15), unique=False, nullable=False)
    

class Units(db.Model):
    unit_code = db.Column(db.String(8), primary_key=True, unique=True, nullable=False)
    unit_name = db.Column(db.String(15), unique=False, nullable=False)
    course = db.Column(db.String(15), unique=False, nullable=False)
    trimester = db.Column(db.String(15), unique=False, nullable=False)
    campus = db.Column(db.String(15), unique=False, nullable=False)
    venue = db.Column(db.String(15), unique=False, nullable=False)
    group = db.Column(db.String(15), unique=False, nullable=False)
    class_date = db.Column(db.String(80), unique=False, nullable=False)
    start_time = db.Column(db.String(15), unique=False, nullable=False)
    end_time = db.Column(db.String(15), unique=False, nullable=False)
    lecture = db.Column(db.String(15), unique=False, nullable=False)

class Attendance(db.Model):
    attendance_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    adm_no = db.Column(db.String(8), unique=False, nullable=False)
    email = db.Column(db.String(28), unique=False, nullable=False)
    first_name = db.Column(db.String(15), unique=False, nullable=False)
    last_name = db.Column(db.String(15), unique=False, nullable=False)
    sir_name = db.Column(db.String(15), unique=False, nullable=False)
    course = db.Column(db.String(15), unique=False, nullable=False)
    unit_code = db.Column(db.String(8), unique=False, nullable=False)
    unit_name = db.Column(db.String(15), unique=False, nullable=False)
    venue = db.Column(db.String(15), unique=False, nullable=False)
    trimester = db.Column(db.String(15), unique=False, nullable=False)
    group = db.Column(db.String(15), unique=False, nullable=False)
    date = db.Column(db.Date, nullable=False)
    class_date = db.Column(db.String(15), unique=False, nullable=False)
    lecture = db.Column(db.String(15), unique=False, nullable=False)
    submitted_by = db.Column(db.String(15), unique=False, nullable=False)
    status = db.Column(db.String(9), unique=False, nullable=False)


