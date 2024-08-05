from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)
print(os.getcwd())

from models import Course, Room, Teacher, Student, Slot
from solver_helper import run_solver, load_from_json

data_courses = []
data_students = []
data_teachers = []
data_classrooms = []

    


def load_data():
    if os.path.exists('courses.json'):
        with open('courses.json', 'r') as f:
            global data_courses
            data = json.load(f)
            data_courses = [Course.from_json(i) for i in data]
    if os.path.exists('classrooms.json'):
        with open('classrooms.json', 'r') as f:
            global data_classrooms
            data = json.load(f)
            data_classrooms = [Room.from_json(i) for i in data]
    if os.path.exists('teachers.json'):
        with open('teachers.json', 'r') as f:
            global data_teachers
            data = json.load(f)
            data_teachers = [Teacher.from_json(i) for i in data]
    if os.path.exists('students.json'):
        with open('students.json', 'r') as f:
            global data_students
            data = json.load(f)
            data_students = [Student.from_json(i) for i in data]

load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses', methods=['GET', 'POST'])
def manage_courses():
    if request.method == 'POST':
        course = Course(
            id=request.form['course_id'],
            language=request.form['language'],
        )
        course_json = course.to_json()
        if course_json not in data_courses:
            data_courses.append(course_json)
        save_data('courses')
        #return redirect(url_for('index'))
    return render_template('courses.html')

@app.route('/classrooms', methods=['GET', 'POST'])
def manage_classrooms():
    if request.method == 'POST':

        global available_slots
        available_slots = []

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days:
            # Get all time slots for the specific day
            slots = request.form.getlist(f'availability[{day}][]')
            for slot in slots:
                start_time, end_time = slot.split('-')
                start_hour = start_time.split(':')[0]
                end_hour = end_time.split(':')[0]

                available_slots.append(Slot(str(day.lower()), start_hour, end_hour))

        classroom = Room(
            room_id=request.form['name'],
            available_slots = available_slots
        )

        data_classrooms.append(classroom)
        save_data('classrooms')
        #return redirect(url_for('index'))
    return render_template('classrooms.html')

@app.route('/teachers', methods=['GET', 'POST'])
def manage_teachers():
    load_data()
    if request.method == 'POST':

        name = request.form['name']
        lastname = request.form['lastname']
        courses=request.form.getlist('courses[]')

        selected_courses = []

        for i in data_courses:
            if str(i.id) in courses:
                selected_courses.append(i)

        slots_tmp = []

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days:
            # Get all time slots for the specific day
            slots = request.form.getlist(f'availability[{day}][]')
            for slot in slots:
                start_time, end_time = slot.split('-')
                start_hour = start_time.split(':')[0]
                end_hour = end_time.split(':')[0]

                slots_tmp.append(Slot(str(day.lower()), start_hour, end_hour))


        teacher = Teacher(
            name = name,
            lastname = lastname,
            courses=selected_courses,
            available_slots=slots_tmp
        )

        remove_idx = None
        for t in data_teachers:
            if t.name == teacher.name and t.lastname == teacher.lastname:
                remove_idx = data_teachers.index(t)
                break
        
        if remove_idx != None:
            data_teachers.pop(remove_idx)
                
        data_teachers.append(teacher)
        print(data_teachers)
        save_data('teachers')
        return redirect(url_for('index'))
    return render_template('teachers.html', courses=data_courses)

@app.route('/students', methods=['GET', 'POST'])
def manage_students():

    if request.method == 'POST':

        name = request.form['name']
        lastname = request.form['lastname']
        courses=request.form.getlist('courses')
        bonus_constraints = request.form.getlist('other_students[]')
        print(bonus_constraints)

        selected_bonuses = [student for student in data_students if str(student) in bonus_constraints]
        selected_courses = [course for course in data_courses if str(course.id) in courses]

        slots_tmp = []

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days:
            slots = request.form.getlist(f'availability[{day}][]')
            for slot in slots:
                start_time, end_time = slot.split('-')
                start_hour = start_time.split(':')[0]
                end_hour = end_time.split(':')[0]

                slots_tmp.append(Slot(str(day.lower()), start_hour, end_hour))

        student = Student(
            name=name,
            lastname=lastname,
            courses=selected_courses,
            available_slots=slots_tmp,
            constraints = selected_bonuses
        )

        data_students.append(student)
        save_data('students')
        return redirect(url_for('index'))
    return render_template('students.html', courses=data_courses, students = data_students)

@app.route('/view_timetable')
def view_timetable():
    solutions = run_solver()
    return render_template('timetable.html', solutions=solutions)
   

def save_data(data_type):
    with open(f'{data_type}.json', 'w') as f:
        if data_type == "courses":
            json.dump(data_courses, f, indent=4,default=Course.to_json)
        elif data_type == "teachers":
            json.dump(data_teachers, f, indent=4, default=Teacher.to_json)
        elif data_type == "students":
            json.dump(data_students, f, indent=4, default=Student.to_json)
        else:
            json.dump(data_classrooms, f, indent=4, default=Room.to_json)

if __name__ == '__main__':
    app.run(debug=True)
