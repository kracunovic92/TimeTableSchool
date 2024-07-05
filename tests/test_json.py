import unittest
from timetable.models import Student, Slot, Teacher, Room, Course


class TestJson(unittest.TestCase):

    def setUp(self):

        self.slot1 = Slot("Monday",11, 12)
        self.slot2 = Slot("Wednesday",1,3)

        self.teacher1 = Teacher("Nikola", "Pasic", ['english','french'],[],[self.slot1])

        self.course1 = Course("Math",1, teacher = self.teacher1)
        self.course2 = Course("English",2, teacher = self.teacher1)

        self.teacher1.courses = [self.course1]

        self.student1 = Student("Lazar","Kracunovic","0601580009",courses= [self.course1, self.course2], available_slots=[self.slot1, self.slot2])

        self.room1 = Room(1,[self.slot1, self.slot2])

    def test_course_json(self):

        course = self.course1
        json_course = course.to_json()
        course2 = Course.from_json(json_course)
        self.assertTrue(course2 == course, "Course Json")


    def test_slot_json(self):

        slot = self.slot1
        json_slot = slot.to_json()
        slot2 = Slot.from_json(json_slot)
        self.assertTrue(slot == slot2, "Slot Json")
    
    def test_teacher_json(self):

        teacher = self.teacher1
        json_teacher = teacher.to_json()
        teacher2 = Teacher.from_json(json_teacher)
        self.assertTrue(teacher == teacher2, "Teacher Json")

    def test_student_json(self):

        student = self.student1
        json_student = student.to_json()
        student2 = Student.from_json(json_student)
        self.assertTrue(student == student2, "Student Json")

    def test_room_json(self):

        room = self.room1
        json_room = room.to_json()
        room2 = Room.from_json(json_room)
        
        self.assertTrue(room == room2, f"Room Json {room}:{room2}")

