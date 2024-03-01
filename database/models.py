from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Date, Float, Boolean, ForeignKey, ForeignKeyConstraint,
                        Integer, String, Table, UniqueConstraint, and_, func,
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