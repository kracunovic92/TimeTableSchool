
from ortools.sat.python import cp_model

class TimeTable:

    def __init__(self,students, teachers, classrooms, courses):
        self.students = students
        self.teachers = teachers
        self.classrooms = classrooms
        self.courses = courses

        self.course_var_map = None
        self.student_var_map = None
        self.teacher_var_map = None

        self.solver = None




    def add_variables(self, model):
        students = self.students.copy()
        teachers = self.teachers.copy()
        courses = self.courses.copy()
        rooms = self.classrooms.copy()

        course_var_map = {}
        student_var_map = {}
        teacher_var_map = {}

        #  Group courses, rooms, slots:
        for course in courses:
            for room in rooms:
                for slot in room.slots:
                    course_var_map[(course,room,slot)] = model.NewBoolVar(
                        f'{course}_{room}_{slot}'
                    )

        # Group teachers, courses, slots:
        for teacher in teachers:
            for course in teacher.courses:
                for slot in teacher.slots:
                    teacher_var_map[(teacher,course,slot)] = model.NewBoolVar(
                        f'{teacher}_{course}_{slot}'
                    )

        # Group students, courses and slots:
        for student in students:
            for course in student.courses:
                    for slot in student.slots:
                        student_var_map[(student,course,slot)] = model.NewBoolVar(
                            f'{student}_{course}_{slot}'
                        )
          
        
        self.course_var_map = course_var_map
        self.student_var_map = student_var_map
        self.teacher_var_map = teacher_var_map
    
    def add_teacher_constraints(self, model):


        # At most one course per teacher per slot
        for teacher in self.teachers:
            for slot in teacher.slots:
                model.AddAtMostOne(
                    self.teacher_var_map[(teacher, course, slot)]
                    for course in teacher.courses
                )
        
        # Ensure each course has exactly one teacher
        for course in self.courses:
           model.AddExactlyOne(
                self.teacher_var_map[(teacher,course,slot)]
                for teacher in self.teachers for slot in teacher.slots if (teacher,course,slot) in self.teacher_var_map
            )


    def add_coures_constraints(self, model):
        # At most one course per room per slot
        for room in self.classrooms:
            for slot in room.slots:
                model.AddAtMostOne(
                    self.course_var_map[(course, room, slot)]
                    for course in self.courses
                )

        # Add Exactly  1 course per week
        for course in self.courses:
                model.AddExactlyOne(
                    self.course_var_map[(course, room, slot)]
                    for room in self.classrooms for slot in  room.slots
                )

        # If teacher can teach course in given time slot,
        # then course must exist in room
        for teacher,course,slot in self.teacher_var_map.keys():
                model.AddImplication(
                    self.teacher_var_map[(teacher,course,slot)],
                    self.course_var_map[(course,room,slot)]
                )

        for course,room,slot in self.course_var_map.keys():
            for student,c,s in self.student_var_map:
                if slot == s and course == c:
                    model.AddImplication(
                        self.course_var_map[(course,room,slot)],
                        self.student_var_map[(student,course, slot)]
                    )
        
        #Ensure each course has at least one teacher     
        for course in self.courses:
            model.Add(
                sum(self.teacher_var_map[(teacher,course,slot)]
                    for teacher in self.teachers
                    for slot in teacher.slots if (teacher,course,slot) in self.teacher_var_map
                    ) >= 1
            )

        for student in self.students:
            for course in student.courses:
                model.AddExactlyOne(
                    self.student_var_map[(student,course,slot)]
                    for slot in student.slots
                )

        for student,course,slot in self.student_var_map.keys():
            model.AddImplication(
                self.student_var_map[(student,course,slot)],
                self.course_var_map[(course,room,slot)]
            )
        

    def add_constraints(self, model):

        self.add_coures_constraints(model)
        self.add_teacher_constraints(model)


        for student in self.students:
            model.Add(
                sum(self.student_var_map[(student,course,slot)]
                    for course in student.courses
                    for slot in student.slots) >=1
            )


    
    def solve(self):
        model = cp_model.CpModel()
        # Add variables
        self.add_variables(model)
        self.add_constraints(model)

        student_variables = self.student_var_map
        teacher_variables = self.teacher_var_map
        courses_variables = self.course_var_map
        #print(self.course_var_map)
        for c in courses_variables:
            print(c)
        for t in teacher_variables:
            print(t)
        for s in student_variables:
            print(s)
        # Create the solver and solve
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        self.status = status
        self.solver = solver
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
            print('Students')
            for var, variable in student_variables.items():
                if solver.value(variable) == 1:
                   print(var)
        else:
            print('No solution found.')

    def print_classes(self, solver):

        courses = []
        
        for var,variable in self.course_var_map.items():

            if solver.value(variable) == 1:
                course = var[0]
                slot = var[2]
                print(str(course) + "  " + str(slot))

                for  t,t2  in self.teacher_var_map.items():

                    if solver.value(t2) == 1 and slot == t[2] and course == t[1]:
                        print('\t'+str(t[0]))
                

                        for s,s2 in self.student_var_map.items():
                            if solver.value(s2) == 1 and slot == s[2] and course == s[1]:
                                print('\t\t '+str(s[0]))
                print('---------------------------------')

                        

                

