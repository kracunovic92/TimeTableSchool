from model import db, Teacher, Student, Course, Classroom, Availability

def populate_db():
    teacher1 = Teacher(name="John Doe", course_id=1)
    teacher2 = Teacher(name="Jane Smith", course_id=2)
    
    student1 = Student(name="Alice Johnson", courses=[1, 2])
    student2 = Student(name="Bob Brown", courses=[1])
    
    course1 = Course(language="Math 101")
    course2 = Course(language="Science 101")
    
    classroom1 = Classroom(name="Room 1")
    classroom2 = Classroom(name="Room 2")
    
    availability1 = Availability(day="Monday", slot="08:00", teacher=teacher1, course=course1, classroom=classroom1)
    availability2 = Availability(day="Tuesday", slot="10:00", teacher=teacher2, course=course2, classroom=classroom2)
    
    db.session.add_all([teacher1, teacher2, student1, student2, course1, course2, classroom1, classroom2, availability1, availability2])
    db.session.commit()

if __name__ == '__main__':
    from app import app
    with app.app_context():
        db.create_all()
        populate_db()
