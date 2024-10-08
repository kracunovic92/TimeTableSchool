from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import sys
import copy

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(__name__, template_folder=resource_path('templates'), static_folder=resource_path('static'))

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

from models import Course, Room, Teacher, Student, Slot
from solver_helper import run_solver

data_courses = []
data_students = []
data_teachers = []
data_classrooms = []


def delete_json_files(directory):
    if(os.path.exists(directory)):
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                os.remove(os.path.join(directory, filename))

def load_data():
    directory = resource_path('data')

    courses_path = os.path.join(directory, 'courses.json')
    classrooms_path = os.path.join(directory, 'classrooms.json')
    teachers_path = os.path.join(directory, 'teachers.json')
    students_path = os.path.join(directory, 'students.json')

    if os.path.exists(courses_path) and os.path.getsize(courses_path) != 0:
        with open(courses_path, 'r') as f:
            global data_courses
            data = json.load(f)
            data_courses = [Course.from_json(i) for i in data]

    if os.path.exists(classrooms_path) and os.path.getsize(classrooms_path) != 0:
        with open(classrooms_path, 'r') as f:
            global data_classrooms
            data = json.load(f)
            data_classrooms = [Room.from_json(i) for i in data]

    if os.path.exists(teachers_path) and os.path.getsize(teachers_path) != 0:
        with open(teachers_path, 'r') as f:
            global data_teachers
            data = json.load(f)
            data_teachers = [Teacher.from_json(i) for i in data]

    if os.path.exists(students_path) and os.path.getsize(students_path) != 0:
        with open(students_path, 'r') as f:
            global data_students
            data = json.load(f)
            data_students = [Student.from_json(i) for i in data]

# delete_json_files(resource_path('data'))

@app.route('/', methods = ['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/delete-json', methods=['POST'])
def delete_json():
    delete_json_files(resource_path('data'))
    data_classrooms.clear()
    data_teachers.clear()
    data_students.clear()
    data_courses.clear()
    return redirect(url_for('index')) 

@app.route('/courses', methods=['GET', 'POST'])
def manage_courses():
    load_data()

    if request.method == 'POST':

        action = request.form.get('action')
        if action == 'add_course':

            weekend = request.form.get('weekends')
            max_students = int(request.form.get('max_students'))
            course = Course(
                id=request.form['course_id'].strip(),
                max_students=max_students,
                week_days=True if weekend == "False" else False
            )
            
            
            data_courses.append(course)
            save_data('courses')

        elif action == 'remove_course':
            course_removal = request.form.getlist('remove_courses[]')

            if course_removal:
                for c in course_removal:
                    data_courses[:] = [course for course in data_courses 
                                if not (course.id == c)]

            save_data('courses')

        #return redirect(url_for('index'))
    return render_template('courses.html', courses=data_courses)

@app.route('/classrooms', methods=['GET', 'POST'])
def manage_classrooms():
    load_data()
    if request.method == 'POST':

        action = request.form.get('action')
        if action == 'add_room':

            global available_slots
            available_slots = []

            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in days:
                slots = request.form.getlist(f'availability[{day}][]')
                for slot in slots:
                    start_time, end_time = slot.split('-')
                    start_hour = start_time.split(':')[0]
                    end_hour = end_time.split(':')[0]

                    available_slots.append(Slot(str(day.lower()), start_hour, end_hour))

            classroom = Room(
                room_id=request.form['name'].strip(),
                available_slots = available_slots
            )

            data_classrooms.append(classroom)
            save_data('classrooms')

        elif action == 'remove_room':
            room_removal = request.form.getlist('remove_rooms[]')

            if room_removal:
                for r in room_removal:
                    data_classrooms[:] = [room for room in data_classrooms 
                                if not (room.id == r)]

            save_data('classrooms')
        #return redirect(url_for('index'))
    return render_template('classrooms.html', rooms=data_classrooms)
    

@app.route('/teachers', methods=['GET', 'POST'])
def manage_teachers():
    load_data()
    if request.method == 'POST':

        action = request.form.get('action')

        if action == 'add_teacher':


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
                slots = request.form.getlist(f'availability[{day}][]')
                for slot in slots:
                    start_time, end_time = slot.split('-')
                    start_hour = start_time.split(':')[0]
                    end_hour = end_time.split(':')[0]

                    slots_tmp.append(Slot(str(day.lower()), start_hour, end_hour))


            teacher = Teacher(
                name = name.strip(),
                lastname = lastname.strip(),
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

            save_data('teachers')

        elif action == 'remove_teacher':

            teacher_removal = request.form.getlist('remove_teacher[]')

            if teacher_removal:
                for t in teacher_removal:
                    name, lastname = t.split()
                    data_teachers[:] = [teacher for teacher in data_teachers 
                                if not (teacher.name == name and teacher.lastname == lastname)]
            save_data('teachers')
        # return redirect(url_for('index'))
    return render_template('teachers.html', courses=data_courses, teachers = data_teachers)

@app.route('/students', methods=['GET', 'POST'])
def manage_students():
    load_data()
    if request.method == 'POST':

        action = request.form.get('action')

        if action == 'add_student':

            name = request.form['name']
            lastname = request.form['lastname']
            courses=request.form.getlist('courses')

            bonus_constraints = request.form.getlist('other_students[]')

            selected_bonuses = [student for student in data_students if str(student) in bonus_constraints]
            selected_courses = [course for course in data_courses if str(course.id) in courses]

            for s in selected_courses:
                s.current_students += 1
                s.calculate_groups()
                for student in data_students:
                    for course in student.courses:
                        if course.id == s.id:
                            course.groups = s.groups
                            course.current_students = s.current_students
                    
                save_data('courses')
                if len(s.groups) > 1:
                    for teacher in data_teachers:
                        for course in teacher.courses:
                            if course.id == s.id:
                                course.groups = s.groups
                                course.current_students = s.current_students

                    save_data('teachers')

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
                name=name.strip(),
                lastname=lastname.strip(),
                courses=selected_courses,
                available_slots=slots_tmp,
                constraints = selected_bonuses
            )


            data_students.append(student)

            
            save_data('students')

        elif action == 'remove_student':

            students_removal = request.form.getlist('remove_students[]')

            if students_removal:
                for s in students_removal:
                    name, lastname = s.split()
                    print(f'{name} {lastname}')
                    
                    student_to_remove = next((student for student in data_students 
                                            if student.name.strip() == name and student.lastname.strip() == lastname), None)
                    
                    if student_to_remove:
                        for sc in student_to_remove.courses:
                            for c in data_courses:
                                if c.id == sc.id:
                                    c.current_students -= 1
                                    c.calculate_groups()
                            
                                    save_data('courses')
                                    save_data('teachers')
                        
                        data_students[:] = [student for student in data_students 
                                            if student != student_to_remove]

            save_data('students')
                    

    return render_template('students.html', courses=data_courses, students = data_students)

@app.route('/view_timetable', methods=['GET', 'POST'])
def view_timetable():
    solutions = run_solver()
    return render_template('timetable.html', solutions=solutions)


def save_data(data_type):
    directory = resource_path('data')
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, f'{data_type}.json')

    with open(file_path, 'w') as f:
        if data_type == "courses":
            json.dump(data_courses, f, indent=4, default=Course.to_json)
        elif data_type == "teachers":
            json.dump(data_teachers, f, indent=4, default=Teacher.to_json)
        elif data_type == "students":
            json.dump(data_students, f, indent=4, default=Student.to_json)
        else:
            json.dump(data_classrooms, f, indent=4, default=Room.to_json)
