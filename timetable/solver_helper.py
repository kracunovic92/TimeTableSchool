import random
import json
from models import Slot, Student, Teacher, Course, Room
from dotenv import load_dotenv
import os
from ortools.sat.python import cp_model
from TimeTable import TimeTable

def load_from_json(path, filename, class_type):
    path = os.path.join(path, filename)
    res = []
    with open(path, 'r') as f:
        data = json.load(f)
        res = [class_type.from_json(i) for i in data]
    return res

def run_solver():


    path = os.getcwd()
    students = load_from_json(path, 'students.json', Student)
    teachers = load_from_json(path, 'teachers.json', Teacher)
    rooms = load_from_json(path, 'classrooms.json', Room)
    courses = load_from_json(path, 'courses.json', Course)

    tt = TimeTable(students, teachers, rooms, courses)

    solutions = tt.find_all_solutions()


    return solutions
