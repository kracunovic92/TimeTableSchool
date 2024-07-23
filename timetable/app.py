from flask import Flask, request, jsonify
from TimeTable import TimeTable
from models import Slot,Student,Teacher,Course,Room

app = Flask(__name__)

@app.route('/solve', methods=['POST'])
def solve_timetable():
    data = request.json
    students = data.get('students', [])
    teachers = data.get('teachers', [])
    classrooms = data.get('classrooms', [])
    courses = data.get('courses', [])

    student_data = [Student.from_json(i) for i in students]
    teacher_data = [Teacher.from_json(i) for i in teachers]
    classroom_data = [Room.from_json(i) for i in classrooms]
    courses_data = [Course.from_json(i) for i in courses]

    timetable = TimeTable(student_data, teacher_data, classroom_data, courses_data)
    solution = timetable.solve()

    if solution:
        return jsonify(solution)
    else:
        return jsonify({'error' : 'No solution found'}, 400)

if __name__ == "__main__":
    app.run(debug=True)
