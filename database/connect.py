from sqlalchemy.engine import create_engine
from sqlalchemy import event, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from . import models


def init_connection(uri, echo=False):
    engine = create_engine(uri, echo=echo)
    Session = sessionmaker(bind=engine)
    metadata = MetaData()
    metadata.bind = engine
    metadata.reflect(bind=engine)

    # Check if models are already defined in the database
    for model in models.Model.__subclasses__():
        if model.__tablename__ not in metadata.tables:
            model.metadata.create_all(engine)

    return engine, Session, metadata


def adding_user(session, first_name, last_name, email, role="student"):
    """
    This function adds a user to the database. If the user already exists, it returns False.
    Otherwise, it adds the user and returns True.

    @param session: sqlalchemy.orm.session.Session, the session to use to add the user
    @param first_name: str, the first name of the user
    @param last_name: str, the last name of the user
    @param email: str, the email of the user
    @param role: str, the role of the user. It can be 'student' or 'professor'
    """
    user = session.query(models.User).filter_by(email=email).first()
    if user is None:
        user = models.User(
            first_name=first_name, last_name=last_name, email=email, role=role
        )
        if role == "student":
            student = models.Student(email=email, id=user.id)
            user.students.append(student)
        else:
            professor = models.Professor(email=email, id=user.id)
            user.professors.append(professor)
        session.add(user)
        session.commit()
        return True
    else:
        return False


def get_user(session, email):
    """
    This function checks if a user is in the database.

    @param session: sqlalchemy.orm.session.Session, the session to use to check the user
    @param email: str, the email of the user
    """
    user = session.query(models.User).filter_by(email=email).first()
    if user is not None:
        return user
    else:
        return None


def adding_course(session, course_name, course_number, professor_email):
    """
    This function adds a course to the database. If the course already exists, it returns False.
    Otherwise, it adds the course and returns True.
    """
    course = session.query(models.Course).filter_by(name=course_name).first()
    professor = session.query(models.Professor).filter_by(email=professor_email).first()
    if course is None:
        course = models.Course(name=course_name, identifier=course_number)
        if professor is not None:
            course.professors.append(professor)
            session.add(course)
            session.commit()
            return True
        else:
            return False
    else:
        return False


def get_course(session, course_id):
    """
    This function returns a course from the database.
    """
    # Check if session is ready, if not, wait for it
    while not session.is_active:
        pass
    course = session.query(models.Course).filter_by(id=course_id).first()
    if course is not None:
        return course
    else:
        return None


def edit_course(session, course_id, course_name, course_number):
    """
    This function edits a course in the database.
    """
    course = get_course(session, course_id)
    if course is not None:
        course.name = course_name
        course.identifier = course_number
        session.commit()
        return True
    else:
        return False


def join_course(session, course_name, student_email):
    """
    This function adds a student to a course. If the student is already in the course, it returns False.
    Otherwise, it adds the student to the course and returns True.
    """
    course = session.query(models.Course).filter_by(name=course_name).first()
    student = session.query(models.Student).filter_by(email=student_email).first()
    if course is not None and student is not None:
        if student not in course.students:
            course.students.append(student)
            session.commit()
            return True
        else:
            return False
    else:
        return False


def get_courses(session, user_email):
    """
    This function returns all the courses of a user.
    """
    user = get_user(session, user_email)
    if user is not None:
        if user.role == "student":
            # Use table course_student to get the courses of the student
            # Check if the student has courses, otherwise, return []
            return user.students[0].courses if user.students else []
        else:
            # Use table course_professor to get the courses of the professor
            return user.professors[0].courses if user.professors else []
    else:
        return None
