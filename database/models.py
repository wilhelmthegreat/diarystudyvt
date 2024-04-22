from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Date, Float, Boolean, ForeignKey, ForeignKeyConstraint, 
                        TIMESTAMP, Integer, String, Table, UniqueConstraint, and_, func,
                        inspect, or_)
from sqlalchemy.orm import Mapped, backref, relationship
from datetime import datetime


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


app_entry_table = Table('app_entry', Model.metadata,
    Column('app_id', Integer, ForeignKey('apps.id'), primary_key=True),
    Column('entry_id', Integer, ForeignKey('entries.id'), primary_key=True)
)


class User(Model):
    __tablename__ = 'users'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = Column(String(50), nullable=False)
    last_name: Mapped[str] = Column(String(50), nullable=False)
    email: Mapped[str] = Column(String(50), nullable=False, unique=True)
    role: Mapped[str] = Column(String(50), nullable=False)
    
    professors: Mapped[list['Professor']] = relationship("Professor", back_populates="users")
    students: Mapped[list['Student']] = relationship("Student", back_populates="users")

    def __repr__(self):
        return f'<User first_name={self.first_name} last_name={self.last_name} email={self.email} role={self.role}>'
    
class Student(Model):
    __tablename__ = 'students'
    id: Mapped[int] = Column(Integer, ForeignKey('users.id'), primary_key=True)
    email: Mapped[str] = Column(String(50), nullable=False, unique=True)
    
    users: Mapped[User] = relationship('User', back_populates='students')
    entry_list: Mapped[list['Entry']] = relationship('Entry', back_populates='student')
    courses: Mapped[list['Course']] = relationship('Course', secondary=course_student_table, back_populates='students')
    enrolled_apps: Mapped[list['App']] = relationship('App', secondary=app_student_table, back_populates='enrolled_students')

    def __repr__(self):
        return f'<Student email={self.email}>'
    
class Professor(Model):
    __tablename__ = 'professors'
    id: Mapped[int] = Column(Integer, ForeignKey('users.id'), primary_key=True)
    email: Mapped[str] = Column(String(50), nullable=False, unique=True)
    
    users: Mapped[list['User']] = relationship('User', back_populates='professors')
    courses: Mapped[list['Course']] = relationship('Course', secondary=course_professor_table, back_populates='professors')

    def __repr__(self):
        return f'<Professor email={self.email}>'
    
class Course(Model):
    __tablename__ = 'courses'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(50), nullable=False)
    identifier: Mapped[str] = Column(String(50), nullable=False)
    
    students: Mapped[list['Student']] = relationship('Student', secondary=course_student_table, back_populates='courses')
    professors: Mapped[list['Professor']] = relationship('Professor', secondary=course_professor_table, back_populates='courses')
    apps: Mapped[list['App']] = relationship('App', secondary=course_app_table, back_populates='binded_courses')
    
    def __repr__(self):
        return f'<Course name={self.name} identifier={self.identifier}>'

class App(Model):
    __tablename__ = 'apps'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(50), nullable=False) # Name of the app
    intro: Mapped[str] = Column(String(50), nullable=False) # Intro to the app
    start_time: Mapped[datetime] = Column(TIMESTAMP, nullable=False) # Start time of the app
    end_time: Mapped[datetime] = Column(TIMESTAMP, nullable=False) # End time of the app
    num_entries: Mapped[int] = Column(Integer, nullable=False) # Number of entries in the app
    max_students: Mapped[int] = Column(Integer, nullable=False) # Maximum number of students in the app
    template: Mapped[str] = Column(String(50), nullable=False) # Template of the app
    
    enrolled_students: Mapped[list['Student']] = relationship('Student', secondary=app_student_table, back_populates='enrolled_apps')
    binded_courses: Mapped[list['Course']] = relationship('Course', secondary=course_app_table, back_populates='apps')
    entry_list: Mapped[list['Entry']] = relationship('Entry', secondary=app_entry_table, back_populates='app')
    stopwords: Mapped[list['Stopword']] = relationship('Stopword', back_populates='app')
    
    def __repr__(self):
        return f'<App intro={self.intro} start_time={self.start_time} end_time={self.end_time} num_entries={self.num_entries} max_students={self.max_students}>'


class Stopword(Model):
    __tablename__ = 'stopwords'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    word: Mapped[str] = Column(String(50), nullable=False)
    app_id: Mapped[int] = Column(Integer, ForeignKey('apps.id'), nullable=False)
    enabled: Mapped[bool] = Column(Boolean, nullable=False, default=True) # This will be used as a flag to make sure when we change the stopword, 
                                                            # we don't delete it from the database to make the app entries consistent.
    
    app: Mapped[App] = relationship('App', back_populates='stopwords')
    
    def __repr__(self):
        return f'<Stopword word={self.word}, app_id={self.app_id}>'
 

class Entry(Model):
    __tablename__ = 'entries'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey('students.id'), nullable=False)
    app_id: Mapped[int] = Column(Integer, ForeignKey('apps.id'), nullable=False)
    content: Mapped[str] = Column(String(50), nullable=False)
    study_start_time: Mapped[int] = Column(TIMESTAMP, nullable=False)
    study_duration_minutes: Mapped[int] = Column(Integer, nullable=False)
    create_at: Mapped[datetime] = Column(TIMESTAMP, nullable=False)
    update_at: Mapped[datetime] = Column(TIMESTAMP, nullable=False)
    
    student: Mapped[Student] = relationship('Student', back_populates='entry_list')
    app: Mapped[App] = relationship('App', back_populates='entry_list')
    
    def __repr__(self):
        return f'<Entry content={self.content} create_at={self.create_at} update_at={self.update_at} study_start_time={self.study_start_time} study_duration_minutes={self.study_duration_minutes}>'

