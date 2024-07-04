import unittest
from timetable.models import Room, Slot


class TestStudent(unittest.TestCase):


    def setUp(self):

        self.slot1 = Slot("Monday", 11, 12)
        self.slot2 = Slot("Wednesday", 1, 3)
        

    def test_init_room(self):
        
        room = Room(1,[self.slot1])
        self.assertTrue(room != None, "Bad Room init")




if __name__ == '__main__':
    unittest.main()