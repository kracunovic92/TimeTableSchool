import random
import json
from models import Slot,Student,Teacher,Course,Room



if __name__ == '__main__':

    days = ['Monday','Tuesday','Wednesday','Thursday','Friday']
    slots = [Slot(day, i,i+1) for day in days for i in range(8,15)]

    rooms = [Room(f"Room{i+1}",random.sample(slots,k = 20))for  i in range(3)]

    # Generate Students
    students = [Student(f"S#{i}", f"SL#{i}", f"12345678{i}", [], random.sample(slots, k=5)) for i in range(40)]

    # Generate Teachers
    teachers = [Teacher(f"T#{i}", f"TL#{i}", "English", [], random.sample(slots, k=5)) for i in range(5)]

    languages = ['English', 'Japanese','French']


    courses = [Course(random.choice(languages),random.choice([1,2,3])) for  i in range(10)]
    
    print(courses)

    for student in students:
        student.courses.extend(random.sample(courses,k = 1))
    
    for teacher in teachers:
        teacher.courses.extend(random.sample(courses,k=2))

    courses_data = [c.to_json() for c in courses]
    print(courses_data)
    students_data = [s.to_json() for s in students]
    teacher_data = [t.to_json() for t in teachers]
    rooms_data = [r.to_json() for r in rooms]
    path = '/home/korisnik/Desktop/Projects/TimeTable/data/example'
    with open(f'{path}/students.json', 'w') as f:
        json.dump(students_data,f, indent=4)

    with open(f'{path}/teachers.json','w') as f:
        json.dump(teacher_data,f, indent=4)

    with open(f'{path}/rooms.json', 'w') as f:
        json.dump(rooms_data,f,indent=4)
    
    with open(f'{path}/course.json', 'w') as f:
        json.dump(courses_data,f, indent=4)




