import json


class Slot:

    def __init__(self, day, start_time, end_time):
        
        start_time = int(start_time)
        end_time = int(end_time)
        self.check_day(day)
        self.check_time(start_time,end_time)

        self.day = day.lower()
        self.start_time = start_time
        self.end_time = end_time


    def to_dict(self):
        return {
            'day': self.day,
            'start': self.start_time,
            'end': self.end_time
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['day'],data['start'],data['end'])
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def from_json(data):
        return Slot.from_dict(json.loads(data))

    def __repr__(self):
        return f"{self.day}:{self.start_time}:{self.end_time}"
    def __str__(self):
        
        return f"{self.day}:{self.start_time}:{self.end_time}"
    

    def __eq__(self, other):

        if isinstance(other, Slot):
            return self.day == other.day and self.start_time == other.start_time and  self.end_time == other.end_time
        
        return False
    
    def __hash__(self):
        return hash((self.day,self.start_time,self.end_time))

    def check_day(self,day):

        const_day = day.lower()
        list_days = ["monday", "tuesday","wednesday",'thursday','friday','saturday']

        if const_day not in list_days:
            raise ValueError(f"This day doesnt exist {day}")
        
    def check_time(self, start_time, end_time):

        if start_time > end_time:
            raise ValueError(f"You can't end before you start {start_time} < {end_time}")
    

    def check_list(slot_list):

        for slot in slot_list:
            
            if not isinstance(slot,Slot):
                raise ValueError(f'Slot {slot} is not instance of Slot')
            
        return True


    def has_duplicates(slot_list):

        seen = set()
        for slot in slot_list:
            if slot in seen:
                return True
            seen.add(slot)
        return False
    
    def remove_duplicates(slot_list):

        seen = set()

        for slot in slot_list:
            if slot not in seen:
                seen.add(slot)
        
        return list(seen)
    
