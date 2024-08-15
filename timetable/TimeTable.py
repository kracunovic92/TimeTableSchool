
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
        self.trygrp = None
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
        student_group_var_map = {}

        for student in students:
            for course in student.courses:
                for group in course.groups:
                    student_group_var_map[(student,course,group)] = model.NewBoolVar(f'{student}_{course}_{group}')
        #  Group courses, rooms, slots:
        for course in courses:

            course.calculate_groups()
            groups = course.groups
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
        print("FF15")
        print(student_group_var_map)
        self.groups_var_map = groups_var_map
        self.student_var_map = student_var_map
        self.teacher_var_map = teacher_var_map
        self.trygrp = student_group_var_map
    
    def add_base_course_constraints(self, model):

        # Each room can have at most one group at any given slot
        for room in self.classrooms:
            for slot in room.slots:
                model.Add(
                    sum(self.groups_var_map[(course, group, room, slot)]
                        for course in self.courses
                        for group in course.groups
                        if (course, group, room, slot) in self.groups_var_map) <= 1
                )
        
        # Each course 2 or 1 time per week
        for course in self.courses:
            for group in course.groups:
                
                days = ['saturday', 'sunday']

                weekend = [self.groups_var_map[(course,group,room,slot)] for room in self.classrooms for slot in room.slots if slot.day in days and (course,group,room,slot) in self.groups_var_map]
                weekdays = [self.groups_var_map[(course,group,room,slot)] for room in self.classrooms for slot in room.slots if slot.day not in days and (course,group,room,slot) in self.groups_var_map] 
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

                if course.week_days:

                    day_indicators = {}
                    for day in days:
                        day_indicators[(course,group, day)] = model.NewBoolVar(f'{course}_{group}_{day}_indicator')
                    model.Add(cp_model.LinearExpr.Sum([day_indicators[(course,group, day)] for day in days]) == 2)

                    for day in days:
                        course_var_for_day = [self.groups_var_map[(course,group, room, slot)]
                                            for room in self.classrooms
                                            for slot in room.slots if slot.day == day]
                        
                        model.AddBoolOr(course_var_for_day).OnlyEnforceIf(day_indicators[(course,group, day)])

                    for var in course_var_for_day:
                        model.Add(var == 0).OnlyEnforceIf(day_indicators[(course,group, day)].Not())
                else:
                    model.Add(sum(weekend) == 1)
                    model.Add(sum(weekdays) == 0)

                
    def add_base_teacher_constraints(self,model):
        
        # Each slot have at most one coures held
        for teacher in self.teachers:
            for slot in teacher.slots:
                
                all_slots = [self.teacher_var_map[(teacher,course,group,slot)] for course in teacher.courses for group in course.groups ]
                model.AddAtMostOne(all_slots)

        # Each course, group, room, and slot must have a teacher assigned if the course is scheduled
        for course in self.courses:
            for group in course.groups:
                for room in self.classrooms:
                    for slot in room.slots:
                        if (course, group, room, slot) in self.groups_var_map:
                            # Create a variable for teacher assignment in this slot
                            teacher_assignment_vars = [
                                self.teacher_var_map[(teacher, course, group, slot)]
                                for teacher in self.teachers
                                if (teacher, course, group, slot) in self.teacher_var_map
                            ]
                            # Ensure that there is at least one teacher assigned if the course is scheduled
                            model.Add(sum(teacher_assignment_vars) > 0).OnlyEnforceIf(self.groups_var_map[(course, group, room, slot)])

        # Ensure that at most one room is assigned for the same course, group, and slot
        for course in self.courses:
            for group in course.groups:
                slot_to_room_assignments = {}

                for room in self.classrooms:
                    for slot in room.slots:
                        if (course, group, room, slot) in self.groups_var_map:
                            if slot not in slot_to_room_assignments:
                                slot_to_room_assignments[slot] = []
                            slot_to_room_assignments[slot].append(self.groups_var_map[(course, group, room, slot)])

                
                for slot, assignments in slot_to_room_assignments.items():
                    model.Add(sum(assignments) <= 1)

    def add_base_student_constraints(self, model):

        # Ensure that each student can attend exactly one course at the time
        for student in self.students:
            for slot in student.slots:
                model.AddAtMostOne(self.student_var_map[student,course,group,slot]
                                   for course in  student.courses for group in course.groups)

        for student in self.students:
            for course in self.courses:
                grp = [self.trygrp[(student,course,group)] for group in course.groups if (student,course,group) in self.trygrp]
                if len(grp) > 0:
                    model.AddExactlyOne(grp)


        for student in self.students:
            for course in self.courses:
                for group in course.groups:
                    list_slots = [self.student_var_map[(student,course,group,slot)] for slot in student.slots if (student,course,group,slot) in self.student_var_map]
                    if (student,course,group) in self.trygrp:
                        model.Add(sum(list_slots) == 0).OnlyEnforceIf(self.trygrp[(student,course,group)].Not())
                        model.Add(sum(list_slots) > 0).OnlyEnforceIf(self.trygrp[(student,course,group)])

        for course in self.courses:
            max_studnets = course.max_students
            for group in course.groups:

                grp_list = [self.trygrp[(student,course,group)] for student in self.students if (student,course,group) in self.trygrp]
                model.Add(sum(grp_list) <= max_studnets)
        
        for (course,group,room,slot) in self.groups_var_map.keys():
            
            student_var = [self.student_var_map[(student,course,group,slot)] for student in self.students  if (student,course,group,slot) in self.student_var_map]
            grup_var = [self.trygrp[(student,course,group)] for student in self.students if (student,course,group) in self.trygrp]

            model.Add(sum(student_var) == sum(grup_var)).OnlyEnforceIf(self.groups_var_map[(course,group,room,slot)])
            #model.Add(sum(student_var)== 0).OnlyEnforceIf(self.groups_var_map[(course,group,room,slot)].Not())
                    
    def add_teacher_constraints(self, model):
        # Teacher should teach only if students can come to course
        for teacher,course,group,slot in self.teacher_var_map.keys():
            students = [self.student_var_map[(s,course,group,slot)] for s in self.students if (s,course,group,slot) in self.student_var_map]
            model.Add(self.teacher_var_map[(teacher,course,group,slot)] <= (cp_model.LinearExpr.Sum(students)))

    def add_coures_constraints(self, model):

        print("BONUSSESESE")
        for student in self.students:
            for other in student.bonus:
                print(f"{student} :: {other}")
                for slot in student.slots:
                    student_in_slot = [
                        self.student_var_map[(student, course,group, slot)]
                        for course in student.courses for group in course.groups if (student,course,group,slot) in self.student_var_map 
                    ]
                    other_student_in_slot = [
                        self.student_var_map[(other, other_course,group, slot)]
                        for other_course in other.courses for group in other_course.groups if (other,other_course,group,slot) in self.student_var_map
                    ]

                    for s in student_in_slot:
                        model.Add(sum(other_student_in_slot) >= 1).OnlyEnforceIf(s)
                    
                for  slot in other.slots:
                    student_in_slot = [
                        self.student_var_map[(student, course,group, slot)]
                        for course in student.courses for group in course.groups if (student,course,group,slot) in self.student_var_map 
                    ]
                    other_student_in_slot = [
                        self.student_var_map[(other, other_course,group, slot)]
                        for other_course in other.courses for group in other_course.groups if (other,other_course,group,slot) in self.student_var_map
                    ]
                    for s in other_student_in_slot:
                        model.Add(sum(student_in_slot) >= 1).OnlyEnforceIf(s)

                    # # If student attends a class in this slot, other_student must attend a class in this slot
                    #model.AddBoolOr([var.Not() for var in student_in_slot] + other_student_in_slot)
                
                    # # If other_student attends a class in this slot, student must attend a class in this slot
                    #model.AddBoolOr([var.Not() for var in other_student_in_slot] + student_in_slot)

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
                #self.print_classes(solver)

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

    def add_course_group_availability_constraints(self, model):
        # Constraint: A course-group session can only happen if all students can attend
        for (course, group, room, slot) in self.groups_var_map.keys():
            student_attendances = [self.student_var_map[(student, course, group, slot)]
                                for student in self.students
                                if (student, course, group, slot) in self.student_var_map]

            # Constraint to ensure all students in the group can attend
            if student_attendances:
                model.Add(sum(student_attendances) == len(student_attendances)).OnlyEnforceIf(self.groups_var_map[(course, group, room, slot)])

    def add_base_constraints(self, model, solver):
        base_constraints = []
        
        base_constraints.append(self.add_base_course_constraints)
        base_constraints.append(self.add_base_teacher_constraints)
        base_constraints.append(self.add_base_student_constraints)
        #base_constraints.append(self.add_course_group_availability_constraints)
        
        for i, const_function in enumerate(base_constraints):
            print(f"BASE CONSTRAINT {i}")
            const_function(model)
            status = solver.Solve(model)
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                #self.print_classes(solver)
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
            #self.print_solution(sol)

    def print_classes(self, solver):

        for var,variable in self.groups_var_map.items():

            if solver.Value(variable) == 1:
                course = var[0]
                group = var[1]
                room = var[2]
                slot = var[3]
                print(str(course) + "  "+str(group) + " " + str(slot))

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
 