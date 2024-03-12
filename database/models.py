from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Date, Float, Boolean, ForeignKey, ForeignKeyConstraint, 
                        TIMESTAMP, Integer, String, Table, UniqueConstraint, and_, func,
                        inspect, or_)
from sqlalchemy.orm import backref, relationship


Model = declarative_base()

course_student_table = Table('course_student', Model.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True)
)

course_professor_table = Table('course_professor', Model.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('professor_id', Integer, ForeignKey('professors.id'), primary_key=True)
)

course_app_table = Table('course_app', Model.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('app_id', Integer, ForeignKey('apps.id'), primary_key=True)
)

app_student_table = Table('app_student', Model.metadata,
    Column('app_id', Integer, ForeignKey('apps.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True)
)


class User(Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    role = Column(String(50), nullable=False)
    
    professors = relationship("Professor", back_populates="users")
    students = relationship("Student", back_populates="users")

    def __repr__(self):
        return f'<User first_name={self.first_name} last_name={self.last_name} email={self.email} role={self.role}>'
    
class Student(Model):
    __tablename__ = 'students'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    email = Column(String(50), nullable=False, unique=True)
    
    users = relationship('User', back_populates='students')
    courses = relationship('Course', secondary=course_student_table, back_populates='students')
    enrolled_apps = relationship('App', secondary=app_student_table, back_populates='enrolled_students')

    def __repr__(self):
        return f'<Student email={self.email}>'
    
class Professor(Model):
    __tablename__ = 'professors'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    email = Column(String(50), nullable=False, unique=True)
    
    users = relationship('User', back_populates='professors')
    courses = relationship('Course', secondary=course_professor_table, back_populates='professors')

    def __repr__(self):
        return f'<Professor email={self.email}>'
    
class Course(Model):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    identifier = Column(String(50), nullable=False)
    
    students = relationship('Student', secondary=course_student_table, back_populates='courses')
    professors = relationship('Professor', secondary=course_professor_table, back_populates='courses')
    apps = relationship('App', secondary=course_app_table, back_populates='binded_courses')
    
    def __repr__(self):
        return f'<Course name={self.name} identifier={self.identifier}>'

class App(Model):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False) # Name of the app
    intro = Column(String(50), nullable=False) # Intro to the app
    start_time = Column(TIMESTAMP, nullable=False) # Start time of the app
    end_time = Column(TIMESTAMP, nullable=False) # End time of the app
    num_entries = Column(Integer, nullable=False) # Number of entries in the app
    max_students = Column(Integer, nullable=False) # Maximum number of students in the app
    template = Column(String(50), nullable=False) # Template of the app
    
    enrolled_students = relationship('Student', secondary=app_student_table, back_populates='enrolled_apps')
    binded_courses = relationship('Course', secondary=course_app_table, back_populates='apps')
    
    def __repr__(self):
        return f'<App intro={self.intro} start_time={self.start_time} end_time={self.end_time} num_entries={self.num_entries} max_students={self.max_students}>'
