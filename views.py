# Import necessary modules and classes

# ... existing imports ...

# Create blueprints for different views
AdminViews = Blueprint('admin_views', __name__)
TeacherViews = Blueprint('teacher_views', __name__)
StudentViews = Blueprint('student_views', __name__)

# Set up login manager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to access this page.', 'warning')
    return redirect(url_for('login'))

def is_admin():
    return current_user.role == 'admin' if current_user.is_authenticated else False

def is_teacher():
    return current_user.role == 'teacher' if current_user.is_authenticated else False

def is_student():
    return current_user.role == 'student' if current_user.is_authenticated else False

# Views for the Admin role
@AdminViews.route('/admin_dashboard')
def admin_dashboard():
    if is_admin():
        # ... your admin dashboard logic ...
        return render_template('admin_dashboard.html')
    return unauthorized()

@AdminViews.route('/admin_attendance_overview', methods=['GET', 'POST'])
def admin_attendance_overview():
    if not is_admin():
        return unauthorized()

    form = SearchForm()

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
                'date': entry.date,
                'status': entry.status,
                # Add any other attendance information you want to display
            }
            attendance_data.append(entry_data)

        student_data['attendance_history'] = attendance_data
        attendance_history.append(student_data)

    # Handle form submission for searching
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search_term.data.lower()

        filtered_attendance_history = [student for student in attendance_history
                                       if (search_term in student['first_name'].lower() or
                                           search_term in student['last_name'].lower() or
                                           search_term == student['adm_no'].lower())]

        return render_template('admin_attendance_overview.html', form=form, attendance_history=filtered_attendance_history)

    return render_template('admin_attendance_overview.html', form=form, attendance_history=attendance_history)


@AdminViews.route('/download_registration_data')
def download_registration_data():
    if not is_admin():
        return unauthorized()

    excel_file_path = os.path.join(os.path.dirname(__file__), 'C:/Users/user/Desktop/gpt/registration_data.xlsx')
    
    try:
        return send_file(excel_file_path, as_attachment=True)
    except FileNotFoundError:
        flash('No registration data available for download.', 'danger')
        return redirect(url_for('admin_dashboard'))


@AdminViews.route('/upload', methods=['GET', 'POST'])
def upload():
    if is_logged_in() and is_admin():  # Check if user is logged in and is an admin
        form = UploadForm()  # Create an instance of your UploadForm

        if request.method == 'POST' and form.validate_on_submit():
            file = form.file.data
            data_type = request.args.get('data_type')
            
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

        return render_template('upload.html', form=form)

    else:
        flash('You do not have permission to access this page. Please contact your admin or log in as an admin.', 'danger')
        return redirect(url_for('login'))


# ... other admin views ...

# Views for the Teacher role
@TeacherViews.route('/teacher_dashboard')
def teacher_dashboard():
    if is_teacher():
        # ... your teacher dashboard logic ...
        return render_template('teacher_dashboard.html')
    return unauthorized()

# ... other teacher views ...

# Views for the Student role
@StudentViews.route('/student_dashboard')
def student_dashboard():
    if not is_student():
        return unauthorized()

    email = session.get('user_id')
    student = Student.query.filter_by(email=email).first()

    if student:
        course = student.course
        trimester = student.trimester
        group = student.group
        campus = student.campus
        units = Units.query.filter_by(course=course, trimester=trimester, group=group, campus=campus).all()
        student_units = []

        for unit in units:
            student_units.append({
                'course': unit.course,
                'trimester': unit.trimester,
                'group': unit.group,
                'campus': unit.campus,
                'date': unit.date,
            })

        return render_template('student_dashboard.html', student=student, student_units=student_units)
    else:
        return redirect(url_for('login'))

    return unauthorized()

@StudentViews.route('/attendance_history')
def attendance_history():
    user_id = session.get('user_id')
    if not is_student():
        return unauthorized()

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


@StudentViews.route('/attendance', methods=['GET', 'POST'])
def attendance():
    form = AttendanceForm()  # Create an instance of your form

    if request.method == 'POST' and form.validate_on_submit() and is_logged_in():
        requested_adm_no = form.adm_no.data
        requested_unit_code = form.unit_code.data
        status = form.status.data

        student = Student.query.get(requested_adm_no)
        unit = Units.query.get(requested_unit_code)

        handle_attendance(requested_adm_no, student, unit, status)

    return render_template('attendance.html', form=form)

# ... other student views ...

# ... additional views for each role ...
