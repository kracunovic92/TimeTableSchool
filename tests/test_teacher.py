import unittest
from timetable.models import Course, Slot,Teacher



class TestTeacher(unittest.TestCase):


    def setUp(self):
        
        self.course1 = Course('english',123)
        self.course2 = Course('French', 12)

        self.slot1 = Slot("monday", 1,2)
        self.slot2 = Slot("Sunday", 3,5)

    
    





if __name__ == '__main__':
    unittest.main()