import unittest
from timetable.models import Slot


class TestSlot(unittest.TestCase):

    def setUp(self):

        self.slot1 = Slot("Monday", 11, 12)
        self.slot2 = Slot("monday",12,13)
        self.slot3 = Slot("monday",11,12)

        self.slot_list_duplicate = [self.slot1,self.slot2,self.slot3]
        self.slot_list_without_duplicate = [self.slot1,self.slot2]

    
    def test_init_slot_good(self):

        slot = Slot("Monday", 11,12)

        self.assertTrue(slot != None, "Bad Slot initialization")

    
    def test_init_bad(self):

        with self.assertRaises(ValueError):
                slot = Slot("Monday_", 11,12)
        with self.assertRaises(ValueError):
              slot = Slot("Monday", 12,11)
    
    def test_to_string(self):
         
        slot = Slot("Monday", 11,12)
        self.assertTrue(f'{slot}' == 'monday:11:12', "Bad ToString")

    def test_list_for_duplicates(self):
        
        self.assertFalse(Slot.has_duplicates(self.slot_list_without_duplicate),"Doesn't have duplicates Fail")
        self.assertTrue(Slot.has_duplicates(self.slot_list_duplicate),"Have duplicates fail")

    def test_remove_duplicates(self):
         
        list_without_duplicates = Slot.remove_duplicates(self.slot_list_without_duplicate)
        print(list_without_duplicates)
        self.assertTrue(len(list_without_duplicates) ==2, "Remove duplicates Fail")

    def test_json(self):
         
        slot = Slot("monday",12,13)
        json_slot = slot.to_json()

        slot2 = Slot.from_json(json_slot)

        self.assertTrue(slot == slot2, "Slot json")

            
if __name__ == '__main__':
     unittest.main()
