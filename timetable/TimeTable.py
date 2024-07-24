
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
    
    def add_base_course_constraints(self, model):
        # At most one course per room per slot
        for room in self.classrooms:
            for slot in room.slots:
                model.AddAtMostOne(
                    self.course_var_map[(course, room, slot)]
                    for course in self.courses
                )
        # At least one course per week
        for course in self.courses:
            model.AddBoolOr(self.course_var_map[(course,room,slot)]
                            for room in self.classrooms for slot in room.slots)
            

    def add_base_teacher_constraints(self,model):
        # At most one course per teacher per slot
        for teacher in self.teachers:
            for slot in teacher.slots:
                model.AddAtMostOne(
                    self.teacher_var_map[(teacher, course, slot)]
                    for course in teacher.courses
                )
        # At least one slot per teacher per course
        for teacher in self.teachers:
            for course in teacher.courses:
                model.AddAtMostOne(
                    self.teacher_var_map[(teacher,course,slot)]
                    for slot in teacher.slots
                )
        #If teacher can teach course in given time slot,
        #then course must exist in room
        for teacher,course,slot in self.teacher_var_map.keys():        
            course_room_vars = [self.course_var_map[(course, room, slot)] for room in self.classrooms if (course,room,slot) in self.course_var_map]
            model.Add(
                self.teacher_var_map[(teacher, course, slot)] <= cp_model.LinearExpr.Sum(course_room_vars)
            )
        #If room exist teacher must be able to teach
        for course,room,slot in self.course_var_map.keys():
            teacher_vars = [self.teacher_var_map[(teacher,course,slot)] for teacher in self.teachers if(teacher,course,slot) in self.teacher_var_map]
            model.Add(
                self.course_var_map[(course,room,slot)] <= cp_model.LinearExpr.Sum(teacher_vars)
            )


    def add_base_student_constraints(self,model):

        # Ensure that each student goes to at least one class
        for student in self.students:
            model.Add(
                sum(self.student_var_map[(student,course,slot)]
                    for course in student.courses
                    for slot in student.slots) >=1
            )
        # Ensure that each student goes visit HIS courses at least one a week
        for student in self.students:
            for course in student.courses:
                model.AddBoolOr(
                    self.student_var_map[(student,course,slot)]
                    for slot in student.slots
                )
        # Ensure that each student can attend exactly one course at the time
        for student in self.students:
            for slot in student.slots:
                model.AddAtMostOne(self.student_var_map[student,course,slot]
                                   for course in  student.courses)
        
        # 
        for (course,room,slot) in self.course_var_map.keys():

            student_var = [self.student_var_map[(student,course,slot)] for student in self.students if(student,course,slot) in self.student_var_map]
            model.Add(
                self.course_var_map[(course,room,slot)] <= cp_model.LinearExpr.Sum(student_var)
            )
        for (student,course,slot) in self.student_var_map.keys():

            course_var = [self.course_var_map[(course,room,slot)] for room in self.classrooms if (course,room,slot) in self.course_var_map]
            model.Add(
                self.student_var_map[(student,course,slot)] <= cp_model.LinearExpr.Sum(course_var)
            )
            
        
 


    def add_teacher_constraints(self, model):
        
        # Teacher should teach only if students can come to course
        for teacher,course,slot in self.teacher_var_map.keys():
            students = [self.student_var_map[(s,course,slot)] for s in self.students if (s,course,slot) in self.student_var_map]
            model.Add(self.teacher_var_map[(teacher,course,slot)] <= (cp_model.LinearExpr.Sum(students)))


    def add_coures_constraints(self, model):
        
        for student in self.students:
            for course  in student.courses:
                model.AddAtMostOne(
                    [self.student_var_map[(student,course,slot)] for slot in student.slots]
                )
        
    def add_optimal_number_of_students(self, model):
        
        def calculate_number_of_students():
            slot_scores = {}
            for course, room, slot in self.course_var_map.keys():
                student_count = sum(
                    1 for s in self.students if (s,course,slot) in self.student_var_map
                )
                slot_scores[(course,room, slot)] = student_count
            return slot_scores

        slot_scores = calculate_number_of_students()

        slot_var = {
            (course, room ,slot ): model.NewBoolVar(f'slot_{course}_{room}_{slot}') for  course, room ,slot in slot_scores
        }

        objective_terms = [
            slot_scores[slot] * slot_var[slot]
            for slot in slot_scores
        ]

        model.Maximize(sum(objective_terms))





    def solve_with_incremental_constraints(self):

        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        best_solution = None
        self.add_variables(model)

        base_constraints = []
        base_constraints.append(self.add_base_course_constraints)
        base_constraints.append(self.add_base_teacher_constraints)
        base_constraints.append(self.add_base_student_constraints)

        constraints = []
        constraints.append(self.add_teacher_constraints)
        constraints.append(self.add_coures_constraints)

        self.add_optimal_number_of_students(model)

        for i, const_funct  in enumerate(base_constraints):
            print(f"SOLUTION {i}: ")
            const_funct(model)
        
            status = solver.Solve(model)
            if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
                print(f'Solution for constraint {const_funct}:')
                    # Add printed solution
                for var, variable in self.course_var_map.items():

                    if solver.value(variable) == 1:
                        print(var)
                print('Teachers')
                for var, variable in self.teacher_var_map.items():
                    if solver.value(variable) == 1:
                        print(var)
                print('Students')
                for var, variable in self.student_var_map.items():
                    if solver.value(variable) == 1:
                        print(var)
                    best_solution = solver
                print("Solution with basic constraints exists")
            else:
                print("Solution with basic constraints doesn't exist")


        print("ADD OTHER CONSTRAINTS")
        for i, const_funct in enumerate(constraints):
            print(f"Other {i}: ")
            const_funct(model)
            status = solver.Solve(model)

            if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
                best_solution = solver
                print(f'Solution for constraint {const_funct}:')
                # Add printed solution
                for var, variable in self.course_var_map.items():

                    if solver.value(variable) == 1:
                        print(var)
                print('Teachers')
                for var, variable in self.teacher_var_map.items():
                    if solver.value(variable) == 1:
                        print(var)
                print('Students')
                for var, variable in self.student_var_map.items():
                    if solver.value(variable) == 1:
                        print(var)
            else:
                print(f'Solution doesnt exist {const_funct} :')

        self.solver = best_solution
        solver = best_solution



    def solve(self):
        model = cp_model.CpModel()
        # Add variables
        self.add_variables(model)
        self.add_base_course_constraints(model)
        self.add_base_teacher_constraints(model)
        self.add_base_student_constraints(model)
        self.add_coures_constraints(model)
        self.add_teacher_constraints(model)

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

                        

                

