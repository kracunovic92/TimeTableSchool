import unittest
from timetable import TimeTable
import json
import os
from ortools.sat.python import cp_model
from dotenv import load_dotenv
from timetable.models import Slot,Student,Teacher,Course,Room


class TestTimeTable(unittest.TestCase):

    def setUp(self):
        
        load_dotenv()
        self.path = os.getenv('DATA_EXAMPLE_PATH')
        self.paths_list = []
        for i in range(10):
            new_path = self.path + f'/data_set_{i}'
            self.paths_list.append(new_path)


    def load_from_json(self,path,filename,class_type):

        path = os.path.join(path,filename)
        res = []
        with open(path,'r') as f:
            data = json.load(f)
            res = [class_type.from_json(i) for i in data]
            return res
        
    
    def test1(self):
        path = self.paths_list[0]
        teachers = self.load_from_json(path,'teachers.json',Teacher)
        students =  self.load_from_json(path,'students.json',Student)
        rooms = self.load_from_json(path,'rooms.json',Room)
        courses = self.load_from_json(path,'course.json',Course)

        tt = TimeTable.TimeTable(students,teachers,rooms,courses)
        tt.solve()
        #tt.print_classes(tt.solver)
        
        self.assertTrue(tt.status == cp_model.OPTIMAL or tt.status == cp_model.FEASIBLE, "Doesnt exist")




if __name__ == '__main__':
    unittest.main()