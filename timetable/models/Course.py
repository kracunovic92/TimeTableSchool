import json
from .Student import Student

class Course:

    def __init__(self,id, students = [], teacher = [], week_days = True, groups = [], max_students = 4):

        self._id = id # Book / Lvl
        self._students = students
        self._teacher = teacher
        self._time_slot = None
        self._week_days = week_days
        self._groups = []
        self._max_students = max_students
        self._current_students = 0

    def __eq__(self, other):

        if isinstance(other,Course):
            if self.language == other.language and self.id == other.id:
                return True
        return False
    
    def __hash__(self):
        return hash(str(self.id))
    
    def __repr__(self):
        return f'{self.id}'
    def __str__(self):
        return f'{self.id}'
    
    def to_dict(self, exclude_teacher = False):
        return {
            "id" : self.id,
            "students":[s.to_dict() for s in self.students] if self.students else None,
            "teacher": self.teacher.to_dict() if self.teacher and not exclude_teacher  else None,
            "slots": [s.to_dict() for s in self.time_slot] if self.time_slot else None,
            "weekdays" : self.week_days,
            "groups" : self.groups,
            "max_students" : self.max_students
        }
    
    @classmethod
    def from_dict(cls, data):
        from .Student import Student
        from .Teacher import Teacher
        from .Slot import Slot
        students = [Student.from_dict(student_data) for student_data in data['students']] if data['students'] else None
        teacher = Teacher.from_dict(data['teacher']) if data.get('teacher') else None

        return cls(data['id'],students,teacher, data['weekdays'],data['groups'], data['max_students'])
    
    def to_json(self):
        return json.dumps(self.to_dict())

    def from_json(data):
        return Course.from_dict(json.loads(data))

    def calculate_groups(self):

        max_students = self.max_students
        tmp_students = self.current_students

        print(f'max students : {max_students}')
        print(f'curr studs : {tmp_students}')

        br = tmp_students // int(max_students) + 1
        self.groups = [i for i in range(1,br+1)]
        
    @property
    def groups(self):
        return self._groups
    @property
    def max_students(self):
        return self._max_students
    @property
    def current_students(self):
        return self._current_students
    
    @property
    def id(self):
        return self._id
    
    @property
    def students(self):
        return self._students
    
    @property
    def teacher(self):
        return self._teacher
    
    @property
    def time_slot(self):
        return self._time_slot
    
    @property
    def week_days(self):
        return self._week_days
    
    @week_days.setter
    def week_day(self, day):
        self._week_days = day
    
    @max_students.setter
    def max_students(self, max_stud):
        self._max_students = max_stud
    @current_students.setter
    def current_students(self,curr_stud):
        self._current_students = curr_stud
    @groups.setter
    def groups(self, gp):
        self._groups = gp

    
    @id.setter
    def id(self, id):
        self._id =id

    @students.setter
    def students(self, students):
        self._students = students
    
    @teacher.setter
    def teacher(self, teacher):
        self._teacher = teacher
    