from .Slot import Slot
import json

class Room:
    

    def __init__(self, room_id, available_slots = []):
        
    
        Slot.check_list(available_slots)
        slots = Slot.remove_duplicates(available_slots)
        self._id = room_id
        self._available_slots = slots
    

    def __eq__(self, other):

        if isinstance(other, Room) and self.id == other.id:
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.id}"
    def __str__(self) -> str:
        return f"{self.id}"

    def __hash__(self) -> int:
        return hash(self.id)
    def to_dict(self):
        return {
            "id": self.id,
            "slots": [ slot.to_dict() for slot in self.slots]
        }    

    @classmethod
    def from_dict(cls, data):

        slots = [Slot.from_dict(slot_data) for slot_data in data["slots"]]
        return cls(data['id'], slots)
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def from_json(data):
        return Room.from_dict(json.loads(data))

    @property
    def id(self):
        return self._id
    
    @property
    def slots(self):
        return self._available_slots
    
    def add_slot(self, slot):
        self._available_slots.append(slot)
    
