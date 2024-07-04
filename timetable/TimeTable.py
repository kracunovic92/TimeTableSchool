
from ortools.sat.python import cp_model
from models import Slot

class TimeTable:

    def __init__(self,students, teachers, classrooms, courses):
        self.students = students
        self.teachers = teachers
        self.classrooms = classrooms
        self.courses = courses

        self.student_var = None
        self.teachers_var = None
        self.calssrooms_var = None
        self.courses_var = None


    def add_variables(self, model):
        students = self.students.copy()
        teachers = self.teachers.copy()
        courses = self.courses.copy()
        rooms = self.classrooms.copy()

        res = {}
        for student in students:

            student_slots = student.get_slots()
            student_courses = student.get_courses()

            for teacher in teachers:

                teacher_slots = teacher.get_slots()
                teacher_courses = teacher_courses.get_courses()

                for course in courses:

                    if (course in teacher_courses) and (course in student_courses):

                        for room in rooms:
                            
                            for slot in room.get_slots():
                                if (slot in student_slots) and (slot in teacher_slots):
                                    res[(student,teacher,course,room,slot)] = model.NewBoolVar(
                                        f"{student}_{teacher}_{course}_{room}_{slot}"
                                    )
        return res

    
    def solve(self):

        model = cp_model.CpModel()



        # 
        # define all variables:

        

        
