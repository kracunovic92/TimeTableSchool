
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


    def add_variables(self, model):
        students = self.students.copy()
        teachers = self.teachers.copy()
        courses = self.courses.copy()
        rooms = self.classrooms.copy()

        course_var_map = {}

        for course in courses:
            for teacher in teachers:
                if course in teacher.courses:
                    for room in rooms:
                        for slot in room.slots:
                            if slot in teacher.slots:
                                course_var_map[(course,teacher, room, slot)]=model.NewBoolVar(
                                    f'{course}_{teacher}_{room}_{slot}'
                                )
        self.course_var_map = course_var_map

        for i in course_var_map:
            print(i)

        print("-----------------------------")

        student_var_map = {}

        for student in self.students:
            for course in student.courses:
                student_var_map[(student,course)] = model.NewBoolVar(
                    f'{student}_{course}'
                )

        self.student_var_map = student_var_map

        for i in student_var_map:
            print(i)

        print('---------------------------------')

    
    def add_constraints(self,model):
        pass
    
    def solve(self):
        model = cp_model.CpModel()
        # Add variables
        var_map = self.add_variables(model)

        student_variables = self.student_var_map
        courses_variables = self.course_var_map

        for course in self.courses:
            model.AddExactlyOne(
                courses_variables[(course,teacher,room,slot)]
                for teacher in self.teachers
                for room in self.classrooms
                for slot in room.slots
                if (course, teacher, room, slot) in courses_variables
            )


        # Constraint: A student can be assigned to a course only if that course is assigned to a slot
        for student in self.students:
            for course in student.courses:
                student_slots = student.slots
                course_assignments = [
                    courses_variables[(course, teacher, room, slot)]
                    for teacher in self.teachers
                    for room in self.classrooms
                    for slot in student_slots
                    if (course, teacher, room, slot) in courses_variables
                ]
                model.AddBoolOr([student_variables[(student, course)].Not()] + course_assignments)

                # Constraint: No overlapping assignments for teachers
        for teacher in self.teachers:
            for slot in set(slot for room in self.classrooms for slot in room.slots):
                model.AddAtMostOne(
                    courses_variables[(course, teacher, room, slot)]
                    for course in self.courses
                    for room in self.classrooms
                    if (course, teacher, room, slot) in courses_variables
                )

        # Constraint: No overlapping assignments for rooms
        for room in self.classrooms:
            for slot in room.slots:
                model.AddAtMostOne(
                    courses_variables[(course, teacher, room, slot)]
                    for course in self.courses
                    for teacher in self.teachers
                    if (course, teacher, room, slot) in courses_variables
                )


        # Create the solver and solve
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('Solution:')
            for key, var in courses_variables.items():
                if solver.Value(var):
                    course, teacher, room, slot = key
                    print(f"Course: {course}, Teacher: {teacher}, Room: {room}, Slot: {slot}")
                    for student in self.students:
                        if solver.Value(student_variables[(student, course)]):
                            print(f"  Student: {student}")
        else:
            print('No solution found.')