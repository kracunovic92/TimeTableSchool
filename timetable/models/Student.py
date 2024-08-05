import json


class Student:

    def __init__(self,name, lastname, phone = "", courses = None, available_slots = None, constraints = None):

        self._name =  name
        self._lastname = lastname
        self._phone = phone
        self._courses = courses or []
        self._available_slots = available_slots or []
        self._bonus_constraints = constraints or []
    
    def __repr__(self):
        return f"{self.name} {self.lastname}"
    def __str__(self):
        return f"{self.name} {self.lastname}"
    
    def __hash__(self):
        return hash((self.name, self.lastname))
    
    def __eq__(self, other):
        if isinstance(other, Student):
            if other.name == self.name and other.lastname == self.lastname:
                return True
        return False

    def to_dict(self):
        return {
            "name": self.name,
            "lastname": self.lastname,
            "phone": self.phone,
            "courses": [course.to_dict(exclude_teacher=True) for course in self.courses] if self.courses else None,
            "slots": [slot.to_dict() for slot in self.slots] if self.slots else None,
            "bonus_constraints": [constraint.to_dict() for constraint in self._bonus_constraints] if self._bonus_constraints else None
        }

    @classmethod
    def from_dict(cls, data):
        from .Course import Course
        from .Slot import Slot
        courses = [Course.from_dict(course_data) for course_data in data.get('courses')] if data['courses'] else None
        slots = [Slot.from_dict(slot_data) for slot_data in data['slots']] if data['slots'] else None
        constraints = [Student.from_dict(student_data) for student_data in data['bonus_constraints']] if data['bonus_constraints'] else None
        return cls(data['name'], data['lastname'], data['phone'], courses, slots,constraints)

    def to_json(self):
        return json.dumps(self.to_dict())
    
    def from_json(data):
        return Student.from_dict(json.loads(data))
    
    @property
    def name(self):
        return self._name
    
    @property
    def lastname(self):
        return self._lastname
    
    @property
    def phone(self):
        return self._phone
    
    @property
    def courses(self):
        return self._courses
    
    @property
    def slots(self):
        return self._available_slots
    @property
    def bonus(self):
        return self._bonus_constraints
    
    
    @courses.setter
    def courses(self, courses_list):
        from .Course import Course

        if not isinstance(courses_list, list):
            raise ValueError("Courses must be a list")
        for course in courses_list:
            if not isinstance(course,type(Course)):
                raise ValueError("This should be Course Object")
        self._courses = courses_list

    @slots.setter
    def available_slots(self, slots_list):
        from .Slot import Slot
        if not isinstance(slots_list, list):
            raise ValueError("Slots must be a list")
        for slot in slots_list:
            if not isinstance(slot,type(Slot)):
                raise ValueError("This should be a Slot Object")
            
        self._available_slots = slots_list
    @name.setter
    def name(self, name):
        self._name = name
    
    @lastname.setter
    def lastname(self, l):
        self._lastname = l

