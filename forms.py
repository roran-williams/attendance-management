from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, RadioField,IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Optional, Length, NumberRange


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')



class Test(FlaskForm):
    name = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')



class RegistrationForm(FlaskForm):
    id_number = StringField('ID Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    position = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')


class AttendanceForm(FlaskForm):
    adm_no = StringField('Admission Number', validators=[InputRequired()])
    unit_code = StringField('Unit Code', validators=[InputRequired()])
    status = RadioField('Status', choices=[('present', 'Present'), ('absent', 'Absent')], validators=[InputRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search_term = StringField('Search for student')
    submit = SubmitField('Search')


class StudentRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired(), Length(min=2, max=12)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=2, max=12)])
    sir_name = StringField('Sir Name', validators=[InputRequired(), Length(min=2, max=12)])
    Adm_no = StringField('Admission Number', validators=[InputRequired(), Length(min=8, max=9)])
    national_id_number = IntegerField('National ID Number', validators=[InputRequired(), NumberRange(min=10000, max=9999999999, message="Please enter a id number")])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=27)])
    campus = StringField('Campus', validators=[InputRequired(), Length(min=2, max=9)])
    course = StringField('Course', validators=[InputRequired(), Length(min=2, max=9)])
    trimester = StringField('Trimester', validators=[InputRequired(), Length(min=2, max=3)])
    group = StringField('Group', validators=[InputRequired(), Length(min=1, max=1)])
    submit = SubmitField('Submit')
 


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')
