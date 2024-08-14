
from collections import defaultdict
from ortools.sat.python import cp_model

class TimeTable:

    def __init__(self,students, teachers, classrooms, courses):
        self.students = students
        self.teachers = teachers
        self.classrooms = classrooms
        self.courses = courses

        self.groups_var_map = None
        self.student_var_map = None
        self.teacher_var_map = None
        self.max_solutions = 5
        self.solver = None
        self.solutions = []

       
    def add_variables(self, model):
        students = self.students.copy()
        teachers = self.teachers.copy()
        courses = self.courses.copy()
        rooms = self.classrooms.copy()

        groups_var_map = {}
        student_var_map = {}
        teacher_var_map = {}
        print(teachers)
        print(students)
        #  Group courses, rooms, slots:
        for course in courses:

            course.calculate_groups()
            groups = course.groups
            print(f'List of groups : {course.id} : {course.groups}')
            for group in groups:
                for room in rooms:
                    for slot in room.slots:
                        if course.week_days and slot.day in ["monday", "tuesday","wednesday",'thursday','friday']:
                            groups_var_map[(course,group,room,slot)] = model.NewBoolVar(
                                f'{course}_{group}_{room}_{slot}'
                            )
                        if not course.week_days and slot.day in ['saturday', 'sunday']:
                            groups_var_map[(course,group,room,slot)] = model.NewBoolVar(
                                f'{course}_{group}_{room}_{slot}'
                            )

        # Group teachers, courses, slots:
        for teacher in teachers:
            for course in teacher.courses:
                for group in course.groups:
                    for slot in teacher.slots:
                        teacher_var_map[(teacher,course,group,slot)] = model.NewBoolVar(
                            f'{teacher}_{course}_{group}_{slot}'
                        )

        # Group students, courses and slots:
        for student in students:
            for course in student.courses:
                    for group in course.groups:
                        for slot in student.slots:
                            student_var_map[(student,course,group,slot)] = model.NewBoolVar(
                                f'{student}_{course}_{group}_{slot}'
                            )
        print("GROUPS VAR")
        for g in groups_var_map.values():
            print(g)
        print("TEACHER")
        for t in teacher_var_map.values():
            print(t)
        print("Student")
        for s in student_var_map.values():
            print(s)
        
        self.groups_var_map = groups_var_map
        self.student_var_map = student_var_map
        self.teacher_var_map = teacher_var_map
    
    def add_base_course_constraints(self, model):
        for room in self.classrooms:
            for slot in room.slots:
                model.Add(
                    sum(self.groups_var_map[(course, group, room, slot)]
                        for course in self.courses
                        for group in course.groups if (course,group,room,slot) in self.groups_var_map) <= 1
                )
        
        for course in self.courses:
            for group in course.groups:
                model.Add(
                    sum(self.groups_var_map[(course, group, room, slot)]
                        for room in self.classrooms
                        for slot in room.slots if (course,group,room,slot) in self.groups_var_map) >= 1
                )
        # for course in self.courses:
        #     max_students = course.max_students
        #     for group in course.groups:
        #         # Collect all the student variables for this course, group, and any slot
        #         student_vars = [
        #             self.student_var_map[(student, course, group, slot)]
        #             for student in self.students
        #             for slot in student.slots
        #             if (student, course, group, slot) in self.student_var_map
        #         ]
                
        #         # Constraint: Number of students in the group should be <= max_students
        #         model.Add(
        #             sum(student_vars) <= max_students
        #         )
                
    def add_base_teacher_constraints(self,model):
    
        #max 1 course/group per slot 
        for teacher in self.teachers:
            for slot in teacher.slots:
                model.Add(
                    sum(self.teacher_var_map[(teacher, course, group, slot)]
                        for course in teacher.courses
                        for group in course.groups if (teacher,course,group,slot) in self.teacher_var_map) <= 1
                )


        for course in self.courses:
            for group in course.groups:
                for room in self.classrooms:
                    for slot in room.slots:
                        room_var = self.groups_var_map.get((course, group, room, slot), None)
                        
                        if room_var is not None:
                            # Create an auxiliary variable to indicate if at least one teacher is available
                            teacher_available = model.NewBoolVar(f'teacher_available_{course}_{group}_{room}_{slot}')
                            
                            # Imply that if the room is scheduled, then there must be a teacher available
                            model.AddImplication(room_var, teacher_available)
                            
                            # Ensure at least one teacher is available if the room is scheduled
                            model.Add(
                                teacher_available <= sum(
                                    self.teacher_var_map.get((teacher, course, group, slot), 0)
                                    for teacher in self.teachers
                                )
                            )
                            
                            # If the room is scheduled, then at least one teacher must be assigned
                            model.Add(
                                sum(self.teacher_var_map.get((teacher, course, group, slot), 0)
                                    for teacher in self.teachers) >= teacher_available
                            ).OnlyEnforceIf(room_var)

        # Room availability if a teacher is assigned
        for room in self.classrooms:
            for slot in room.slots:
                for course in self.courses:
                    for group in course.groups:
                        room_var = self.groups_var_map.get((course, group, room, slot), None)
                        for teacher in self.teachers:
                            teacher_var = self.teacher_var_map.get((teacher, course, group, slot), None)
                            if room_var is not None and teacher_var is not None:
                                model.AddImplication(teacher_var, room_var)

        # Teacher availability if a room is assigned
        for course in self.courses:
            for group in course.groups:
                for slot in self.teachers[0].slots:  # Consider each slot individually
                    for room in self.classrooms:
                        room_var = self.groups_var_map.get((course, group, room, slot), None)
                        for teacher in self.teachers:
                            teacher_var = self.teacher_var_map.get((teacher, course, group, slot), None)
                            if room_var is not None and teacher_var is not None:
                                model.AddImplication(room_var, teacher_var)



    def add_base_student_constraints(self,model):

        for student in self.students:
            for course in student.courses:
                # Constraint to ensure exactly one group for each course
                model.Add(
                    sum(
                        self.student_var_map[(student, course, group, slot)]
                        for group in course.groups
                        for slot in student.slots
                        if (student, course, group, slot) in self.student_var_map
                    ) == 1
                )

        for (course,group,room,slot) in self.groups_var_map.keys():

            student_var = [self.student_var_map[(student,course,group,slot)] for student in self.students if(student,course,group,slot) in self.student_var_map]
            model.Add(
                self.groups_var_map[(course,group,room,slot)] <= cp_model.LinearExpr.Sum(student_var)
            )
        for (student,course,group,slot) in self.student_var_map.keys():

            course_var = [self.groups_var_map[(course,group,room,slot)] for room in self.classrooms if (course,group,room,slot) in self.groups_var_map]
            model.Add(
                self.student_var_map[(student,course,group,slot)] <= cp_model.LinearExpr.Sum(course_var)
            )



    def add_teacher_constraints(self, model):
        pass
    def add_coures_constraints(self, model):
        pass

    def add_optimal_number_of_rooms(self, model):

        rooms = self.groups_var_map
        rm_list = []

        for r,v in rooms.items():
            rm_list.append(v)
        print("added minimization process")
        model.Minimize(sum(rm_list)) 


    def exclude_current_solution(self,model,solver):
        literals = []
        for var in (
            list(self.groups_var_map.values()) +
            list(self.teacher_var_map.values()) +
            list(self.student_var_map.values())
        ):
            # Create a boolean variable to represent the inequality
            diff_var = model.NewBoolVar(f'diff_{var.Name()}')
            model.Add(var != solver.Value(var)).OnlyEnforceIf(diff_var)
            model.Add(var == solver.Value(var)).OnlyEnforceIf(diff_var.Not())
            literals.append(diff_var)
    
        # Ensure at least one variable is different
        model.AddBoolOr(literals)
  
    def find_all_solutions(self):

        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        self.add_variables(model)
        base_constrains_status = self.add_base_constraints(model, solver)
        other_constraints_status = self.add_other_constraints(model, solver)
        self.add_optimal_number_of_rooms(model)
        #self.add_optimal_number_of_students(model)

        print(f' base_constraints_status {base_constrains_status}')
        print(f'other constraint_status {other_constraints_status}')
        if base_constrains_status and other_constraints_status:

            status = solver.Solve(model)
            print("Status")
            print(status)
            print(cp_model.OPTIMAL)
            print(cp_model.INFEASIBLE)
            i = 1
            while (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE) and i < self.max_solutions:
                
                print(f"SOLUTION {i}")
                i += 1
                self.exclude_current_solution(model,solver)
                status = solver.Solve(model)
                self.add_solution(solver)
                self.print_classes(solver)

        return self.solutions
    
    def add_other_constraints(self,model,solver):
        constraints = []
        constraints.append(self.add_coures_constraints)
        constraints.append(self.add_teacher_constraints)
        for i, const_function in enumerate(constraints):
            print(f"New CONSTRAINT {i}")
            const_function(model)
            status = solver.Solve(model)
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                print("Other constraints added")
            else:
                print("Some misstake with other constraints")
                return False
        self.model = model
        return True

    def add_base_constraints(self, model, solver):
        base_constraints = []
        base_constraints.append(self.add_base_course_constraints)
        base_constraints.append(self.add_base_teacher_constraints)
        base_constraints.append(self.add_base_student_constraints)
        
        for i, const_function in enumerate(base_constraints):
            print(f"BASE CONSTRAINT {i}")
            const_function(model)
            status = solver.Solve(model)
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                print("Basic constraints added")
            else:
                print("Some misstake with basic constraints")
                return False
        self.model = model
        return True
        

    def print_solution(self, solution):
        
        for classroom in solution:
            print(f"{classroom['course']}: {classroom['group']} : Room: {classroom['room']} : Time: {classroom['slot']}")
            print(f"Teacher : {classroom['teacher']}")
            for i,s in enumerate(classroom['students']):
                print(f'{i} : {s}')


    def print_solutions(self):
        solutions = self.solutions.copy()

        for i,sol in enumerate(solutions):
            print(f"SOLUTION {i}:")
            self.print_solution(sol)

    def print_classes(self, solver):
        for var,variable in self.groups_var_map.items():

            if solver.Value(variable) == 1:
                course = var[0]
                group = var[1]
                room = var[2]
                slot = var[3]
                print(str(course) + "  " + str(slot))

                for  t,t2  in self.teacher_var_map.items():

                    if solver.Value(t2) == 1 and t[3] == slot:
                        print(t)
                
                        for s,s2 in self.student_var_map.items():
                            if solver.Value(s2) == 1 and s[3] == slot:
                                print(s)
                print('---------------------------------')

            

                        
    def solve_with_incremental_constraints(self):
        """
        Testing function
        """
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        best_solution = None
        self.add_variables(model)

        base_constraints = []
        base_constraints.append(self.add_base_course_constraints)
        base_constraints.append(self.add_base_teacher_constraints)
        base_constraints.append(self.add_base_student_constraints)

        constraints = []
        #constraints.append(self.add_teacher_constraints)
        #constraints.append(self.add_coures_constraints)

        #self.add_optimal_number_of_students(model)
        self.add_optimal_number_of_rooms(model)

        for i, const_funct  in enumerate(base_constraints):
            print(f"SOLUTION {i}: ")
            const_funct(model)
        
            status = solver.Solve(model)
            if status == cp_model.FEASIBLE:
                print( "Feasable")
            if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
                print(f'Solution for constraint {const_funct}:')
                    # Add printed solution
                for var, variable in self.course_var_map.items():

                    if solver.Value(variable) == 1:
                        print(var)
                print('Teachers')
                for var, variable in self.teacher_var_map.items():
                    if solver.Value(variable) == 1:
                        print(var)
                print('Students')
                for var, variable in self.student_var_map.items():
                    if solver.Value(variable) == 1:
                        print(var)
                    best_solution = solver
                print("Solution with basic constraints exists")
            else:
                print("Solution with basic constraints doesn't exist")

        for i, const_funct in enumerate(constraints):
            print(f"Other {i}: ")
            const_funct(model)
            status = solver.Solve(model)

            if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
                best_solution = solver
                print(f'Solution for constraint {const_funct}:')
                # Add printed solution
                for var, variable in self.course_var_map.items():

                    if solver.Value(variable) == 1:
                        print(var)
                print('Teachers')
                for var, variable in self.teacher_var_map.items():
                    if solver.Value(variable) == 1:
                        print(var)
                print('Students')
                for var, variable in self.student_var_map.items():
                    if solver.Value(variable) == 1:
                        print(var)
            else:
                print(f'Solution doesnt exist {const_funct} :')

        self.solver = best_solution
        solver = best_solution



                


    def add_solution(self, solver):
        classes = []
        for var, variable in self.groups_var_map.items():
            if solver.Value(variable) == 1:
                course = var[0]
                group = var[1]
                room = var[2]
                slot = var[3]
                classroom = {
                    'course': course.to_dict(),
                    'group' : group,
                    'room': room.to_dict(),
                    'slot': slot,
                    'teacher': None,
                    'students': []
                }
                
                # Find the teacher for this course and slot
                # {teacher}_{course}_{group}_{slot}
                for t, t2 in self.teacher_var_map.items():
                    if solver.Value(t2) == 1 and slot == t[3] and course == t[1] and group == t[2]:
                        classroom['teacher'] = t[0].to_dict()
                
                # Find students for this course and slot
                # {student}_{course}_{group}_{slot}
                for s, s2 in self.student_var_map.items():
                    if solver.Value(s2) == 1 and slot == s[3] and course == s[1] and group == s[2]:
                        classroom['students'].append(s[0].to_dict())
                
                classes.append(classroom)
                
        self.solutions.append(classes)
 