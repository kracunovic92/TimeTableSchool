
import unittest
from timetable.models import Student

class TestCourse(unittest.TestCase):

    def setUp(self):
        
        student1 = Student("Lazar","Kracunovic","0601580009")
        student2 = Student("Milos", "Kracunovic")

    def test_init_course(self):
        pass




if __name__ == '__main__':
    unittest.main()
