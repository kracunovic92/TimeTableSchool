import json
from .Student import Student

class Course:

    def __init__(self,language,id, students = [], teacher = [], week_days = True):

        self._language = language
        self._id = id
        self._students = students
        self._teacher = teacher
        self._time_slot = None
        self._week_days = week_days

    def __eq__(self, other):

        if isinstance(other,Course):
            if self.language == other.language and self.id == other.id:
                return True
        return False
    
    def __hash__(self):
        return hash(str(self.id))
    
    def __repr__(self):
        return f'{self.language}_{self.id}'
    def __str__(self):
        return f'{self.language}_{self.id}'
    
    def to_dict(self, exclude_teacher = False):
        return {
            "language": self.language,
            "id" : self.id,
            "students":[s.to_dict() for s in self.students] if self.students else None,
            "teacher": self.teacher.to_dict() if self.teacher and not exclude_teacher  else None,
            "slots": [s.to_dict() for s in self.time_slot] if self.time_slot else None,
            "weekdays" : self.week_days
        }
    
    @classmethod
    def from_dict(cls, data):
        from .Student import Student
        from .Teacher import Teacher
        from .Slot import Slot
        students = [Student.from_dict(student_data) for student_data in data['students']] if data['students'] else None
        teacher = Teacher.from_dict(data['teacher']) if data.get('teacher') else None
        return cls(data['language'],data['id'],students,teacher, data['weekdays'])
    
    def to_json(self):
        return json.dumps(self.to_dict())

    def from_json(data):
        return Course.from_dict(json.loads(data))

    
    @property
    def language(self):
        return self._language
    
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
    
    @language.setter
    def language(self, lan):
        self._language = lan
    
    @id.setter
    def id(self, id):
        self._id =id

    @students.setter
    def students(self, students):
        self._students = students
    
    @teacher.setter
    def teacher(self, teacher):
        self._teacher = teacher
    