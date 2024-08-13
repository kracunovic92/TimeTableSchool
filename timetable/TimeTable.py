
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
          
        
        self.groups_var_map = groups_var_map
        self.student_var_map = student_var_map
        self.teacher_var_map = teacher_var_map
    
    def add_base_course_constraints(self, model):

        # At most one course per room per slot
        for room in self.classrooms:
            for slot in room.slots:
                model.AddAtMostOne(
                    self.groups_var_map[(course,group, room, slot)]
                    for course in self.courses for group in course.groups if (course,group,room,slot) in self.groups_var_map
                )
        #At least one course per week
        for course in self.courses:
            for group in course.groups:

                weekend = [self.groups_var_map[(course,group, room, slot)] for room in self.classrooms for slot in room.slots if (slot.day  in ['saturday','sunday'] and (course,group,room,slot) in self.groups_var_map)]
                weekdays = [self.groups_var_map[(course, group, room, slot)]for room in self.classrooms for slot in room.slots if (slot.day not in ['saturday', 'sunday'] and (course,group,room,slot) in self.groups_var_map)]
                if   not course.week_day:
                    model.AddExactlyOne(weekend)
                    #model.Add(sum(weekend) == 1)
                else:
                    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
                    # Create indicator variables for each day
                    day_indicators = {}
                    for day in days:
                        day_indicators[(course,group , day)] = model.NewBoolVar(f'{course}_{group}_{day}_indicator')

                    # Ensure exactly two of these indicators are true
                    model.Add(cp_model.LinearExpr.Sum([day_indicators[(course,group, day)] for day in days]) == 2)

                    for day in days:
                        # Gather all the possible course variables for the given day
                        course_var_for_day = [self.groups_var_map[(course,group, room, slot)]
                                            for room in self.classrooms
                                            for slot in room.slots if slot.day == day]
                        # Ensure that if the indicator is true, at least one course variable for that day is true
                        model.AddBoolOr(course_var_for_day).OnlyEnforceIf(day_indicators[(course,group, day)])
                        # Ensure that if the indicator is false, none of the course variables for that day are true
                        for var in course_var_for_day:
                            model.Add(var == 0).OnlyEnforceIf(day_indicators[(course,group, day)].Not())

                
    def add_base_teacher_constraints(self,model):
        # At most one course per teacher per slot
        for teacher in self.teachers:
            for slot in teacher.slots:
                model.AddAtMostOne(
                    self.teacher_var_map[(teacher, course,group, slot)]
                    for course in teacher.courses for group in course.groups
                )

        #If teacher can teach course in given time slot,
        #then course must exist in room
        for teacher,course,group, slot in self.teacher_var_map.keys():        
            course_room_vars = [self.groups_var_map[(course,group, room, slot)] for room in self.classrooms if (course,group,room,slot) in self.groups_var_map]
            model.Add(
                self.teacher_var_map[(teacher, course,group, slot)] <= cp_model.LinearExpr.Sum(course_room_vars)
            )
        # #If room exist teacher must be able to teach
        for course,group,room,slot in self.groups_var_map.keys():
            teacher_vars = [self.teacher_var_map[(teacher,course,group, slot)] for teacher in self.teachers if(teacher,course,group,slot) in self.teacher_var_map]
            model.Add(
                self.groups_var_map[(course,group,room,slot)] <= cp_model.LinearExpr.Sum(teacher_vars)
            )

        # If One teaching theaces 1 group non other can do that
        for course in self.courses:
            for group in course.groups:
                pass
                #TODO

    def add_base_student_constraints(self,model):

        for student in self.students:
            for course in student.courses:
                group_vars = []
                for group in course.groups:
                    for slot in student.slots:
                        if (student, course, group, slot) in self.student_var_map:
                            group_var = self.student_var_map[(student, course, group, slot)]
                            if group_var not in group_vars:
                                group_vars.append(group_var)
                
                # Ensure exactly one group per course for each student
                model.AddExactlyOne(group_vars)
                if course.week_days:
                # For courses on weekdays, select exactly two slots
                    for group in course.groups:
                        slot_vars = [
                            self.student_var_map[(student, course, group, slot)]
                            for slot in student.slots
                            if (student, course, group, slot) in self.student_var_map
                        ]
                        model.Add(sum(slot_vars) == 2)
                else:
                    # For courses on weekends, select exactly one slot
                    for group in course.groups:
                        slot_vars = [
                            self.student_var_map[(student, course, group, slot)]
                            for slot in student.slots
                            if (student, course, group, slot) in self.student_var_map
                        ]
                        model.Add(sum(slot_vars) == 1)


        # Constraint: Ensure that each student can attend exactly one course at a time
        for student in self.students:
            for slot in student.slots:
                model.AddAtMostOne(
                    self.student_var_map[(student, course, group, slot)]
                    for course in student.courses
                    for group in course.groups
                    if (student, course, group, slot) in self.student_var_map if (student,course,group,slot) in self.student_var_map
                )
        

        # Ensure consistency between student attendance and course availability in rooms
        for (course, group, room, slot) in self.groups_var_map.keys():
            student_vars = [
                self.student_var_map[(student, course, group, slot)]
                for student in self.students
                if (student, course, group, slot) in self.student_var_map
            ]
            model.Add(
                self.groups_var_map[(course, group, room, slot)] <= cp_model.LinearExpr.Sum(student_vars)
            )

        for (student, course, group, slot) in self.student_var_map.keys():
            course_vars = [
                self.groups_var_map[(course, group, room, slot)]
                for room in self.classrooms
                if (course, group, room, slot) in self.groups_var_map
            ]
            model.Add(
                self.student_var_map[(student, course, group, slot)] <= cp_model.LinearExpr.Sum(course_vars)
            )
            
    def add_teacher_constraints(self, model):
        
        # Teacher should teach only if students can come to course
        for teacher,course,group,slot in self.teacher_var_map.keys():
            students = [self.student_var_map[(s,course,group, slot)] for s in self.students if (s,course,group,slot) in self.student_var_map]
            model.Add(self.teacher_var_map[(teacher,course,group, slot)] <= (cp_model.LinearExpr.Sum(students)))

    def add_coures_constraints(self, model):
        
        # Constraint: Each student should attend exactly one group for each course
        for student in self.students:
            for course in student.courses:
                # Variables for each group selection
                group_selection_vars = [
                    model.NewBoolVar(f"group_selected_{student}_{course}_{group}")
                    for group in course.groups
                ]

                # Select exactly one group for each student for each course
                model.AddExactlyOne(group_selection_vars)

                # Create a map for the group selection variables
                group_var_map = {
                    group: group_selection_vars[i]
                    for i, group in enumerate(course.groups)
                }

                for group in course.groups:
                    slot_vars = [
                        self.student_var_map[(student, course, group, slot)]
                        for slot in student.slots
                        if (student, course, group, slot) in self.student_var_map
                    ]

                    # If the group is selected, then the slots should match the requirements
                    if course.week_days:
                        # For courses on weekdays, select exactly two slots
                        model.Add(sum(slot_vars) == 2).OnlyEnforceIf(group_var_map[group])
                    else:
                        # For courses on weekends, select exactly one slot
                        model.Add(sum(slot_vars) == 1).OnlyEnforceIf(group_var_map[group])

                    # If the group is not selected, no slots should be chosen
                    model.Add(sum(slot_vars) == 0).OnlyEnforceIf(group_var_map[group].Not())


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
                print("Basic constraints added")
            else:
                print("Some misstake with basic constraints")
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
        for var,variable in self.course_var_map.items():

            if solver.Value(variable) == 1:
                course = var[0]
                slot = var[2]
                print(str(course) + "  " + str(slot))

                for  t,t2  in self.teacher_var_map.items():

                    if solver.Value(t2) == 1 and slot == t[2] and course == t[1]:
                        print('\t'+str(t[0]))
                
                        for s,s2 in self.student_var_map.items():
                            if solver.Value(s2) == 1 and slot == s[2] and course == s[1]:
                                print('\t\t '+str(s[0]))
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
        constraints.append(self.add_teacher_constraints)
        constraints.append(self.add_coures_constraints)

        self.add_optimal_number_of_students(model)
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
 