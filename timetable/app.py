from flask import Flask, render_template, request, redirect, url_for, jsonify
from model import db, Teacher, Student, Course, Classroom, Availability
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses', methods=['GET', 'POST'])
def manage_courses():
    if request.method == 'POST':
        course_id = request.form['course_id']
        language = request.form['language']
        
        course = Course(id=course_id, language=language)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('manage_courses'))
    
    return render_template('courses.html')

@app.route('/classrooms', methods=['GET', 'POST'])
def manage_classrooms():
    if request.method == 'POST':
        room_name = request.form['room_name']
        available_days = request.form.getlist('available_days')
        available_slots = request.form.getlist('available_slots')
        
        classroom = Classroom(name=room_name)
        db.session.add(classroom)
        db.session.commit()
        
        for day in available_days:
            for slot in available_slots:
                availability = Availability(day=day, slot=slot, classroom=classroom)
                db.session.add(availability)
        
        db.session.commit()
        return redirect(url_for('manage_classrooms'))
    
    return render_template('classrooms.html')

@app.route('/teachers', methods=['GET', 'POST'])
def manage_teachers():
    if request.method == 'POST':
        name = request.form['name']
        course_id = request.form['course_id']
        available_days = request.form.getlist('available_days')
        available_slots = request.form.getlist('available_slots')
        
        teacher = Teacher(name=name, course_id=course_id)
        db.session.add(teacher)
        db.session.commit()
        
        for day in available_days:
            for slot in available_slots:
                availability = Availability(day=day, slot=slot, teacher=teacher)
                db.session.add(availability)
        
        db.session.commit()
        return redirect(url_for('manage_teachers'))
    
    return render_template('teachers.html')

@app.route('/students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        name = request.form['name']
        course_ids = request.form.getlist('course_ids')
        
        student = Student(name=name)
        db.session.add(student)
        db.session.commit()
        
        for course_id in course_ids:
            student.courses.append(Course.query.get(course_id))
        
        db.session.commit()
        return redirect(url_for('manage_students'))
    
    courses = Course.query.all()
    return render_template('students.html', courses=courses)

@app.route('/export/<data_type>')
def export_data(data_type):
    if data_type == 'courses':
        data = Course.query.all()
        data_list = [{'id': c.id, 'language': c.language} for c in data]
        export_to_json(data_list, 'courses.json')
    elif data_type == 'classrooms':
        data = Classroom.query.all()
        data_list = [{'name': c.name, 'availability': [{'day': a.day, 'slot': a.slot} for a in c.availabilities]} for c in data]
        export_to_json(data_list, 'classrooms.json')
    elif data_type == 'teachers':
        data = Teacher.query.all()
        data_list = [{'name': t.name, 'course_id': t.course_id, 'availability': [{'day': a.day, 'slot': a.slot} for a in t.availabilities]} for t in data]
        export_to_json(data_list, 'teachers.json')
    elif data_type == 'students':
        data = Student.query.all()
        data_list = [{'name': s.name, 'courses': [c.id for c in s.courses]} for s in data]
        export_to_json(data_list, 'students.json')
    else:
        return jsonify({'error': 'Invalid data type'}), 400

    return jsonify({'message': f'{data_type.capitalize()} data exported successfully'})

def export_to_json(data_list, file_name):
    with open(file_name, 'w') as f:
        json.dump(data_list, f, indent=4)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
