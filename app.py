#Imports
#StandardLibraryImports

import logging, ssl, sys, os, secrets, subprocess
from datetime import datetime, timedelta
import pandas as pd
import csv
from io import StringIO


# Third-party Imports
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from flask_socketio import SocketIO


from flask_login import LoginManager, current_user, login_user
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect
from markupsafe import escape

subprocess.run('call setenv.bat', shell=True)

# Local Imports
from forms import LoginForm, RegistrationForm,UploadForm,AttendanceForm, ChangePasswordForm, SearchForm,StudentRegistrationForm
from models import db, User, Student, Units, Attendance


# Set up logging with RotatingFileHandler for log rotation
log_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=10)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))

logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)



app = Flask(__name__)


# Load the context
socketio = SocketIO(app)
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
certfile_path = 'cert.pem'
keyfile_path = 'key.pem'
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['CERTFILE_PATH'] = 'cert.pem'
app.config['KEYFILE_PATH'] = 'key.pem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
context.load_cert_chain(certfile=certfile_path, keyfile=keyfile_path)

db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
app.permanent_session_lifetime = timedelta(minutes=30)

ADMIN = 'admin'
TEACHER = 'teacher'
STUDENT = 'student'


# User authentication functions
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def login_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):  # Make sure 'password' is the hashed version
        session['user_id'] = user.email
        logging.info(f'User {user.email} logged in')
        return user.role
    logging.warning(f'Failed login attempt for email: {email}')
    return None

    
def logout_user():
    user_id = session.get('user_id')
    if user_id:
        logging.info(f'User {user_id} logged out')
    session.pop('user_id', None)


def is_logged_in():
    print('user_id' in session)
    return 'user_id' in session


def get_user_role():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return user.role
    return None


# Views
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():

    attendance_history = get_attendance_data()
    
    return render_template('index.html',attendance_history=attendance_history,current_user=current_user)




def get_attendance_data():
    # Retrieve all students and their attendance history
    students = Student.query.all()
    attendance_history = []

    for student in students:
        # Populate the student data
        student_data = {
            'id': student.email,
            'adm_no': student.adm_no,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'course': student.course,
            'trimester': student.trimester,
            'group': student.group,
            'class': f"{student.course} - {student.trimester} - {student.group}",  # Placeholder for class information
            # Add any other student information you want to display
        }

        # Retrieve attendance history for each student
        student_attendance = Attendance.query.filter_by(adm_no=student.adm_no).all()
        attendance_data = []

        for entry in student_attendance:
            entry_data = {
                'id':entry.attendance_id,
                'adm_no': entry.adm_no,
                'first_name': entry.first_name,
                'last_name': entry.last_name,
                'email':entry.email,
                'date': entry.date,
                'status': entry.status,
                'course':entry.course,
                'unit_name':entry.unit_name,
                'group':entry.group,
                'lecture':entry.lecture,
                'venue':entry.venue,
                'class_date':entry.class_date,
                'submitted_by':entry.submitted_by,
                'status':entry.status

                # Add any other attendance information you want to display
            }
            
            attendance_data.append(entry_data)

        student_data['attendance_history'] = attendance_data
        attendance_history.append(student_data)

    return attendance_history
    





@app.route('/admin_attendance_overview', methods=['GET', 'POST'])
def admin_attendance_overview():
    # Assuming you have a form for searching, replace YourSearchForm with the actual name of your search form class
    form = SearchForm()
    attendance_history = get_attendance_data()

    # Handle form submission for searching
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search_term.data.lower()

        filtered_attendance_history = [student for student in attendance_history
                                       if (search_term in student['first_name'].lower() or
                                           search_term in student['last_name'].lower() or
                                           search_term == student['adm_no'].lower()) ]

        return render_template('admin_attendance_overview.html', form=form, attendance_history=filtered_attendance_history)

    return render_template('admin_attendance_overview.html', form=form, attendance_history=attendance_history)



    
@app.route('/teacher_dashboard')
def teacher_dashboard():

    if is_logged_in() and get_user_role() == TEACHER:
        return render_template('teacher_dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/testing',methods=['GET', 'POST'])
def testing():
    return render_template('test.html')



@app.route('/student_dashboard')
def student_dashboard():
    print(f'Session Content: {session}')
    if is_logged_in() and get_user_role() == STUDENT:
        email = User.email
        course = Student.course
        trimester = Student.trimester
        group = Student.group
        campus = Student.campus
        units = Units.query.all()
        email = session.get('user_id')
        student = Student.query.filter_by(email=email).first()
        print(student)

        for i in units:
            if Units.course == Student.course and Units.trimester == Student.trimester and Units.group == Student.group and Units.campus == Student.campus:
                student_units.append(i.course,i.trimester,i.group,i.campus,i.date)

        return render_template('student_dashboard.html',student=student)
    else:
        return redirect(url_for('login'))





@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create an instance of the form

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        role = login_user(email, password)
        logging.info(f'Login attempt for email: {email} - Role: {role}')

        if role:
            if role == STUDENT:
                return redirect(url_for('student_dashboard'))
            elif role == TEACHER:
                return redirect(url_for('teacher_dashboard'))
            elif role == ADMIN:
                return redirect(url_for('admin_dashboard'))

        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html', form=form)  # Pass the form to the template




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Create an instance of your registration form
    

    if form.validate_on_submit():  # Check if form was submitted and is valid
        id_number = form.id_number.data
        email = form.email.data
        position = form.position.data
        password = form.password.data
        password2 = form.password2.data


        if password != password2:
            flash("Passwords don't match", 'danger')
        else:
            hashed_password = generate_password_hash(password, method='scrypt')

        if position == 'student':
            role = STUDENT
        elif position == 'teacher':
            role = TEACHER
        else:
            role = None

        if role:
            # Check if the email already exists
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                flash('Email already exists. Please use a different email.', 'danger')
                return redirect(url_for('register'))


            new_user = User(id_number=id_number, email=email, role=role, password=hashed_password)
            existing_student = Student.query.filter_by(email=new_user.email).first()
            if existing_student : #and new_user.id_number == existing_student.id_number
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')

            else:
                if new_user.role == STUDENT:
                    flash("you are not a registered or you provided wrong information, please register here",'danger')
                    #give a registration form to register as student. to the students table.
                    #send notification to admin asking them to register the student
                    #create csv for all students who want to be registered
                    #admin can download it
                    return redirect(url_for('student_registration'))
                else:
                    flash("you are not a registered lecture, please contact your admin",'danger')
                    return redirect(url_for('register'))

            return redirect(url_for('login'))
        else:
            flash('Invalid user role. Please try again.', 'danger')

    return render_template('register.html', form=form)  # Pass the form to the template context





# ...

# Import the necessary modules at the beginning of your file

@app.route('/student_registration', methods=['GET', 'POST'])
def student_registration():
    form = StudentRegistrationForm()

    if form.validate_on_submit():
        # Collect form data
        first_name = form.first_name.data
        last_name = form.last_name.data
        sir_name = form.sir_name.data
        adm_no = form.Adm_no.data
        national_id_number = form.national_id_number.data
        email = form.email.data
        campus = form.campus.data
        course = form.course.data
        trimester = form.trimester.data
        group = form.group.data

        # Create a DataFrame to store the registration data
        registration_data = pd.DataFrame({
            'First Name': [first_name],
            'Last Name': [last_name],
            'Sir Name': [sir_name],
            'Adm_no': [adm_no],
            'Nat_ID': [national_id_number],
            'Email': [email],
            'Campus': [campus],
            'Course': [course],
            'Trimester': [trimester],
            'Group': [group],
        })

        # Append the new registration data to an existing Excel file or create a new one if it doesn't exist
        excel_file_path = os.path.join(os.path.dirname(__file__), 'C:/Users/user/Desktop/gpt/registration_data.xlsx')

        try:
            existing_data = pd.read_excel(excel_file_path)
            updated_data = pd.concat([existing_data, registration_data], ignore_index=True)
        except FileNotFoundError:
            updated_data = registration_data

        # Write the updated data to the Excel file
        updated_data.to_excel(excel_file_path, index=False)

        # Emit a socket event to notify the admin or other relevant users
        socketio.emit('new_student_registered', {'first_name': first_name, 'last_name': last_name, 'email': email}, namespace='/admin')
        
        flash('Form submitted successfully! Your details are being verified; you will be contacted once completed', 'success')

        # Redirect to the admin_dashboard or any other appropriate route
        return redirect(url_for('login'))

    return render_template('student_registration.html', form=form)



# Add a route for the admin to download the registration data
@app.route('/download_registration_data')
def download_registration_data():
    if is_logged_in() and get_user_role() == ADMIN:
        excel_file_path = os.path.join(os.path.dirname(__file__), 'C:/Users/user/Desktop/gpt/registration_data.xlsx')
        
        try:
            return send_file(excel_file_path, as_attachment=True)
        except FileNotFoundError:
            flash('No registration data available for download.', 'danger')
            return redirect(url_for('admin_dashboard'))
    else:
        flash("please login with nessesary permissions", 'danger')
        return redirect(url_for("login"))
    








@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))



# Add the following Class and Student management views

@app.route('/class_list', methods=['GET', 'POST'])
def class_list():
    if is_logged_in():
        lecture = "ken"
        classes = Units.query.filter_by(lecture=lecture).all()
        attend = Attendance.query.all()
        reg_students = Student.query.all()

        return render_template('class_list.html', classes=classes, attend=attend, reg_students=reg_students)
    return redirect(url_for('login'))

@app.route('/attendance_history')
def attendance_history():
    user_id = session.get('user_id')

    if not user_id:
        flash('User not logged in', 'danger')
        return redirect(url_for('login'))

    student = Student.query.filter_by(email=user_id).first()

    if not student:
        flash('Student information not found', 'danger')
        return redirect(url_for('login'))

    attendance_history = Attendance.query.filter_by(adm_no=student.adm_no).all()
    trimester_classes = Units.query.filter_by(course=student.course, trimester=student.trimester).all()

    total_classes = len(trimester_classes)
    attended_classes = sum(1 for entry in attendance_history if entry.status == "present")

    attendance_percentage = int((attended_classes / total_classes) * 100) if total_classes > 0 else 0

    return render_template('attendance_history.html',
                           student=student,
                           attendance_history=attendance_history,
                           attendance_percentage=attendance_percentage,
                           trimester_classes=trimester_classes)


#==================================================================================================================================
#==================================================================================================================================

################################################### ATTENDANCE RECORDING ##########################################################

#==================================================================================================================================
#==================================================================================================================================

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    form = AttendanceForm()  # Create an instance of your form
    return process_attendance(form)



def process_attendance(form):
    if request.method == 'POST' and form.validate_on_submit() and is_logged_in():
        requested_adm_no = form.adm_no.data
        requested_unit_code = form.unit_code.data
        status = form.status.data

        student = Student.query.get(requested_adm_no)
        unit = Units.query.get(requested_unit_code)
        submitted_by = session.get('user_id')

        if student:
            adm_no = requested_adm_no
            email = student.email
            first_name = student.first_name
            last_name = student.last_name
            sir_name = student.sir_name
            course = student.course
            unit_code = requested_unit_code
            unit_name = unit.unit_name
            venue = unit.venue
            trimester = student.trimester
            group = student.group
            date = datetime.utcnow().date()
            class_date = unit.class_date
            lecture = unit.lecture
            status = status

            existing_attendance = Attendance.query.filter_by(
                class_date=class_date,
                date=date,
                unit_code=unit_code
            ).first()

            if existing_attendance:
                flash("Attendance has already been submitted for this class.", "warning")
            else:
                new_attendance = Attendance(
                    adm_no=adm_no,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    sir_name=sir_name,
                    course=course,
                    unit_code=unit_code,
                    unit_name=unit_name,
                    venue=venue,
                    trimester=trimester,
                    group=group,
                    date=date,
                    class_date=class_date,
                    lecture=lecture,
                    submitted_by=submitted_by,
                    status=status
                )
                db.session.add(new_attendance)
                db.session.commit()
                flash("Attendance submitted successfully.", "success")
        else:
            flash("Invalid adm_no", "danger")

    return render_template('attendance.html', form=form)

#=====================================================================================================================================
#=====================================================================================================================================

########################################################## UPLOAD ####################################################################

#=====================================================================================================================================
#=====================================================================================================================================
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if is_logged_in() and get_user_role() == ADMIN:
        form = UploadForm()

        if request.method == 'POST' and form.validate_on_submit():
            file = form.file.data
            data_type = request.args.get('data_type')
            handle_file_upload(file, data_type)

        return render_template('upload.html', form=form)

    else:
        flash('You do not have permission to access this page. Please contact your admin or login as admin', 'danger')
        return redirect(url_for('login'))




def handle_file_upload(file, data_type):
    if file and file.filename.endswith(('.csv', '.xlsx')):
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            if data_type == 'students':
                adm_no = row['adm_no']
                email = row['email']
                first_name = row['first_name']
                last_name = row['last_name']
                sir_name = row['sir_name']
                id_number = row['id_number']
                campus = row['campus']
                course = row['course']
                trimester = row['trimester']
                group = row['group']

                existing_student = Student.query.filter_by(adm_no=adm_no).first()
                if existing_student:
                    existing_student.email = email
                    existing_student.first_name = first_name
                    existing_student.last_name = last_name
                    existing_student.sir_name = sir_name
                    existing_student.id_number = id_number
                    existing_student.campus = campus
                    existing_student.course = course
                    existing_student.trimester = trimester
                    existing_student.group = group
                else:
                    new_student = Student(
                        adm_no=adm_no,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        sir_name=sir_name,
                        id_number=id_number,
                        campus=campus,
                        course=course,
                        trimester=trimester,
                        group=group
                    )
                    db.session.add(new_student)

            elif data_type == 'units':
                unit_code = row['unit_code']
                unit_name = row['unit_name']
                course = row['course']
                trimester = row['trimester']
                campus = row['campus']
                venue = row['venue']
                group = row['group']
                class_date = row['class_date'].strftime('%Y-%m-%d')
                start_time = row['start_time']
                end_time = row['end_time']
                lecture = row['lecture']

                existing_unit = Units.query.filter_by(unit_code=unit_code).first()
                if existing_unit:
                    existing_unit.unit_name = unit_name
                    existing_unit.course = course
                    existing_unit.trimester = trimester
                    existing_unit.campus = campus
                    existing_unit.venue = venue
                    existing_unit.group = group
                    existing_unit.class_date = class_date
                    existing_unit.start_time = start_time
                    existing_unit.end_time = end_time
                    existing_unit.lecture = lecture
                    flash(existing_unit.unit_code + " updated successfully!!")
                else:
                    new_unit = Units(
                        unit_code=unit_code,
                        unit_name=unit_name,
                        course=course,
                        trimester=trimester,
                        campus=campus,
                        venue=venue,
                        group=group,
                        class_date=class_date,
                        start_time=start_time,
                        end_time=end_time,
                        lecture=lecture
                    )
                    db.session.add(new_unit)

        db.session.commit()
        flash('Upload successful', 'success')



#======================================================================================================================================
#======================================================================================================================================

############################################################ UPDATE PROFILE ###########################################################

#======================================================================================================================================
#======================================================================================================================================
	

# Add this route to your app.py file
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if is_logged_in():
        form = ChangePasswordForm()  # Create a form for updating user profile information

        if form.validate_on_submit():
            # Get the current user
            user_id = session['user_id']
            user = User.query.get(user_id)


            # Update user password
            old_password = form.old_password.data
            new_password = form.new_password.data
            confirm_password = form.confirm_password.data

            if check_password_hash(user.password, old_password):
                # Update the password
                user.password = generate_password_hash(new_password, method='sha256')
                db.session.commit()

                flash('Password updated successfully!', 'success')
                return redirect(url_for('student_dashboard'))  # Replace with the actual endpoint
            else:
                flash('Invalid old password. Please try again.', 'danger')

    # Inside your route where you render the template
    return render_template('change_password.html', form=form, current_user=current_user)

@app.route('/view_profile')
def view_profile():
    if is_logged_in():
        user_id = session.get('user_id')
        user = User.query.get(user_id)

        if user:
            if user.role == 'student':
                student = Student.query.filter_by(email=user.email).first()
                if student:
                    return render_template('view_student_profile.html', student=student)
                else:
                    flash('Student information not found.', 'danger')
            else:
                # For other roles (e.g., teacher, admin), you can display basic user information
                return render_template('view_profile.html', user=user)
        else:
            flash('User not found.', 'danger')

    return redirect(url_for('login'))





###################################                  #######################################               #####################



@app.route('/button')
def button():
    return render_template('button.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    upload_form = UploadForm()
    attendance_form = AttendanceForm()
    search_form = SearchForm()
    student_registration_form = StudentRegistrationForm()
    change_password_form = ChangePasswordForm()

    if (
        login_form.validate_on_submit() or
        registration_form.validate_on_submit() or
        upload_form.validate_on_submit() or
        attendance_form.validate_on_submit() or
        search_form.validate_on_submit() or
        student_registration_form.validate_on_submit() or
        change_password_form.validate_on_submit()
    ):
        # Handle form submissions here if needed
        pass

    return render_template('form.html', 
                           login_form=login_form,
                           registration_form=registration_form,
                           upload_form=upload_form,
                           attendance_form=attendance_form,
                           search_form=search_form,
                           student_registration_form=student_registration_form,
                           change_password_form=change_password_form)
    

@app.route('/table')
def table():
    attendance_history = get_attendance_data()
    return render_template('table.html',attendance_history=attendance_history)

@app.route('/typography')
def typography():
    return render_template('typography.html')

@app.route('/element')
def element():
    return render_template('element.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/errorpage')
def errorpage():
    return render_template('404.html')

@app.route('/widget')
def widget():
    return render_template('widget.html')



###################################                  #######################################               #####################         



if __name__ == '__main__':
    # Change this line to use socketio.run instead of app.run
    # socketio.run(app, ssl_context=context, host='0.0.0.0', port=443, debug=True)

    app.run(host='127.0.0.1', port=5000,debug=True)
    # app.run(ssl_context=context, host='127.0.0.1', port=443, debug=True)

