import random
import json
from models import Slot,Student,Teacher,Course,Room
from dotenv import load_dotenv
import os

load_dotenv()
path = os.getenv('DATA_EXAMPLE_PATH')


def generate_slots(days,start_h,end_h):
    return [Slot(day,i,i+1) for day in days for i in range(start_h,end_h)]

def generate_rooms(slots, number = 2):
    return [Room(f'Room{i+1}', random.sample(slots,k = random.randint(10,len(slots)))) for i in range(number)]

def generate_students(slots, number = 10):
    return [Student(f"S#{i}", f"SL#{i}", f"12345678{i}", [], random.sample(slots,k = random.randint(10,len(slots)))) for i in range(number)]

def generate_teachers(slots, number = 5):
    return [Teacher(f"T#{i}", f"TL#{i}", "English", [], random.sample(slots, k=random.randint(10,len(slots)))) for i in range(number)]
def generate_courses(languages, number = 2):
    return [Course(lang,i+1) for  i in range(number) for lang in languages]

def extend_courses(persons,courses, k = 1):
    for p in persons:
        p.courses.extend(random.sample(courses,k=random.randint(1,len(courses))))



def generate_sample(days,
                    h_start,
                    h_end,
                    number_rooms,
                    number_students,
                    number_teachers,
                    languages,
                    number_courses,
                    extend_k_students,
                    extend_k_teachers
                    ):

    slots = generate_slots(days,h_start,h_end)
    rooms = generate_rooms(slots,number_rooms)
    students = generate_students(slots,number_students)
    teachers = generate_teachers(slots, number_teachers)
    courses = generate_courses(languages,number_courses)

    extend_courses(students,courses,k = extend_k_students)
    extend_courses(teachers,courses, k = extend_k_teachers)
    return slots,rooms,students, teachers, courses

def generate_json_list(path,data,name):
    os.makedirs(path, exist_ok=True)
    json_data = [d.to_json() for d in data]
    
    with open(f'{path}/{name}.json','w') as f:
        json.dump(json_data,f, indent= 4)

def select_random_pair(a, b):
    first = random.randint(8,9)
    second = random.randint(20, 21)
    return [first, second]

if __name__ == '__main__':

    list_days = ["monday", "tuesday","wednesday",'thursday','friday','saturday']
    list_lang = ['English', 'Spain','Russian','Serbian']
    days = [random.sample(list_days, k =random.randint(1,len(list_days))) for _ in range(10)]
    h = [select_random_pair(8,15) for _ in range(10)]
    number_rooms = [random.randint(1,3) for _ in range(10)]
    number_students = [random.randint(40,70) for _ in range(10)]
    number_teachers = [random.randint(2,6) for _ in range(10)]
    languages = [random.sample(list_lang, k = random.randint(1,len(list_lang))) for _ in range(10)]
    number_courses = [random.randint(1,2) for _ in range(10)]
    extend_k_students = [random.randint(1,3) for _ in range(10)]
    extend_k_teachers = [random.randint(1,3) for _ in range(10)]


    for i in range(10):
        new_path = path+f'/data_set_{i}'
        slots, rooms, students, teachers, courses = generate_sample(
                                                                days[i],
                                                                h_start= h[i][0],
                                                                h_end = h[i][1],
                                                                number_rooms= number_rooms[i],
                                                                number_students= number_students[i],
                                                                number_teachers= number_teachers[i],
                                                                languages= languages[i],
                                                                number_courses= number_courses[i],
                                                                extend_k_students= extend_k_students[i],
                                                                extend_k_teachers= extend_k_teachers[i]
                                                                )
        generate_json_list(new_path,rooms,'rooms')
        generate_json_list(new_path,courses,'course')
        generate_json_list(new_path,students,'students')
        generate_json_list(new_path,teachers,'teachers')


