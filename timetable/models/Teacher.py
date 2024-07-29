import json

class Teacher:

    def __init__(self, name, lastname, courses = [], available_slots = []):

        self._name = name
        self._lastname = lastname
        self._courses = courses or []
        self._available_slots = available_slots or []

    def __repr__(self):
        return f"{self.name} {self.lastname}"
    def __str__(self):
        return f"{self.name} {self.lastname}"
    
    def __hash__(self):
        return hash((self.name, self.lastname))
    def __eq__(self, other):
        if isinstance(other,Teacher):
            if other.name == self.name and other.lastname == self.lastname:
                return True
        return False
    
    def to_dict(self):
        return {
            "name": self.name,
            "lastname": self.lastname,
            "courses": [course.to_dict(exclude_teacher=True) for course in self.courses] if self.courses else None,
            "slots": [slot.to_dict() for slot in self.slots] if self.slots else None,
        }

    @classmethod
    def from_dict(cls, data):
        from .Course import Course
        from .Slot import Slot
        courses = [Course.from_dict(course_data) for course_data in data['courses']] if data['courses'] else []
        slots = [Slot.from_dict(slot_data) for slot_data in data.get('slots', [])]
        return cls(data['name'], data['lastname'], courses, slots)

    def to_json(self):
        return json.dumps(self.to_dict())
    
    def from_json(data):
        return Teacher.from_dict(json.loads(data))
    @property
    def name(self):
        return self._name
    @property
    def lastname(self):
        return self._lastname
    @property
    def languages(self):
        return self._languages
    
    @property
    def courses(self):
        return self._courses
    
    @property
    def slots(self):
        return self._available_slots
    
    @slots.setter
    def avaliable_slots(self, avaliable_slots):
        self._avaliable_slots = avaliable_slots
    
    @courses.setter
    def courses(self, cours):
        self._courses = cours
