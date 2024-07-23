import random
import json
from models import Slot,Student,Teacher,Course,Room
from dotenv import  load_dotenv
import os
from ortools.sat.python import cp_model

from TimeTable import TimeTable

def load_from_json(path,filename,class_type):

    path = os.path.join(path,filename)
    res = []
    with open(path,'r') as f:
        data = json.load(f)
        res = [class_type.from_json(i) for i in data]
        return res
    
if __name__ == '__main__':

    load_dotenv()
    path = os.getenv('DATA_EXAMPLE_PATH')

    teachers = load_from_json(path,'teachers.json',Teacher)
    students =  load_from_json(path,'students.json',Student)
    rooms = load_from_json(path,'rooms.json',Room)
    courses = load_from_json(path,'course.json',Course)

    for s in students:
        print(s.courses)
        
    tt = TimeTable(students,teachers,rooms,courses)
    model = cp_model.CpModel()
    #res = tt.add_variables(model)

    tt.solve()
    
