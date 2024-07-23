
from ortools.sat.python import cp_model
from models import Slot

class TimeTable:

    def __init__(self,students, teachers, classrooms, courses):
        self.students = students
        self.teachers = teachers
        self.classrooms = classrooms
        self.courses = courses

        self.course_var_map = None
        self.student_var_map = None
        self.teacher_var_map = None

    def add_variables(self, model):
        students = self.students.copy()
        teachers = self.teachers.copy()
        courses = self.courses.copy()
        rooms = self.classrooms.copy()

        course_var_map = {}
        student_var_map = {}
        teacher_var_map = {}

        # Variables: Add courses to rooms for room's slots:
        for course in courses:
            for room in rooms:
                for slot in room.slots:
                    course_var_map[(course,room,slot)] = model.NewBoolVar(
                        f'{course}_{room}_{slot}'
                    )

        # Variables: Add teachers to courses for teacher's slots:
        for teacher in teachers:
            for course in teacher.courses:
                for slot in teacher.slots:
                    teacher_var_map[(teacher,course,slot)] = model.NewBoolVar(
                        f'{teacher}_{course}_{slot}'
                    )

        # Variables: Add students to courses:
        for student in self.students:
            for course in student.courses:
                    student_var_map[(student,course,slot)] = model.NewBoolVar(
                        f'{student}_{course}_{slot}'
                    )
          
        
        self.course_var_map = course_var_map
        self.student_var_map = student_var_map
        self.teacher_var_map = teacher_var_map
    
    def add_constraints(self, model):

        # Room capacity: At most one course per room per slot
        for room in self.classrooms:
            for slot in room.slots:
                model.AddAtMostOne(
                    self.course_var_map[(course, room, slot)]
                    for course in self.courses
                )
        # Rooms imam 1 kurs nedeljno
        for course in self.courses:
                model.AddExactlyOne(
                    self.course_var_map[(course, room, slot)]
                    for room in self.classrooms for slot in  room.slots
                )



        
        for teacher,course,slot in self.teacher_var_map.keys():
            model.AddImplication(
                self.teacher_var_map[(teacher,course,slot)],
                self.course_var_map[(course,room,slot)]
            )

        # Teacher constraint: At most one course per teacher per slot
        for teacher in self.teachers:
            for slot in teacher.slots:
                model.AddAtMostOne(
                    self.teacher_var_map[(teacher, course, slot)]
                    for course in teacher.courses
                )
        # Ensure each teacher has at least one course
        for teacher in self.teachers:
            model.Add(
                sum(self.teacher_var_map[(teacher, course, slot)]
                    for course in teacher.courses
                    for slot in teacher.slots) >= 1
            )


    
    def solve(self):
        model = cp_model.CpModel()
        # Add variables
        self.add_variables(model)
        self.add_constraints(model)

        student_variables = self.student_var_map
        teacher_variables = self.teacher_var_map
        courses_variables = self.course_var_map

        # Create the solver and solve
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('Solution:')
            # Add printed solution
            for var, variable in courses_variables.items():

                if solver.value(variable) == 1:
                    print(var)
            print('Teachers')
            for var, variable in teacher_variables.items():
                if solver.value(variable) == 1:
                    print(var)
        else:
            print('No solution found.')

    def print_classes(self, solver):

        courses = []

        for var,variable in {self.course_var_map}.items():

            if solver.value(variable) == 1:
                course = var[0]
                room = var[1]
                slot = var[2]

                for  t,t2  in {self.teacher_var_map}.items():

                    if solver.value(t2) == 1 and slot == t[2] and room == t[1]:
                        pass

                

