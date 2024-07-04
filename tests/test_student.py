import unittest
from timetable.models import Student,Course,Slot,Teacher



class TestStudent(unittest.TestCase):

    def setUp(self):

        self.course1 = Course("Math",1, teacher = "Smit")
        self.course2 = Course("English",2, teacher = "Jonson")

        self.slot1 = Slot("Monday",11, 12)
        self.slot2 = Slot("Wednesday",1,3)

        self.student = Student("Lazar","Kracunovic","0601580009",courses= [self.course1, self.course2], available_slots=[self.slot1, self.slot2])
    
    def test_init_student_courses(self):
        student = Student("Lazar","Kracunovic","0601580009",courses= [self.course1, self.course2])

        self.assertTrue(len(student.courses) == 2, "Bad student coursees")

    def test_get_slots(self):

        student = self.student
        slot_list  = [self.slot1, self.slot2]
        self.assertTrue(student.slots == slot_list, "Bad getter for slots")

    def test_get_courses(self):

        student = self.student
        course_list = [self.course1, self.course2]

        self.assertTrue(student.courses == course_list, "Bad getter for courses")
    
    def test_bad_course(self):
        student = Student("Lazar","Kracunovic")
        with self.assertRaises(ValueError):
            student.courses = ["bad course"]


    def test_to_string(self):

        student = self.student

        self.assertTrue(f'{student}' == 'Lazar Kracunovic', "Bad ToString")

if __name__ == '__main__':
    unittest.main()