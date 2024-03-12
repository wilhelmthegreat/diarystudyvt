from sqlalchemy.engine import create_engine
from sqlalchemy import event, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from . import models
import datetime


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


def get_course(session, course_id: int, user_email: str):
    """
    This function returns a course from the database.
    """
    # Get the user from the database
    user = get_user(session, user_email)
    if user is None:
        return None
    # Get the course from the database
    course = session.query(models.Course).filter_by(id=course_id).first()
    # Check if the user is a student or a professor
    if user.role == "student":
        # Check the table course_student to get the course of the student
        if course is not None:
            if user.students[0] in course.students:
                return course
            else:
                return None
        else:
            return None
    elif user.role == "professor":
        # Check the table course_professor to get the course of the professor
        if course is not None:
            if user.professors[0] in course.professors:
                return course
            else:
                return None
        else:
            return None
    else:
        raise ValueError(
            f"User role {user.role} is not handled correctly. " +
            "Please check if the role is correct."
        )
        
        


def edit_course(session, course_id, course_name, course_number, user_email):
    """
    This function edits a course in the database.
    """
    course = get_course(session, course_id, user_email)
    user = get_user(session, user_email)
    if course is not None and user is not None:
        if user.role == "professor":
            course.name = course_name
            course.identifier = course_number
            session.commit()
            return course
        else:
            return None
    else:
        return None


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
    
    
def add_app(session, course_id, user_email, name, intro, start_time: int, end_time: int, num_entries, max_students, template_link):
    """
    This function adds an app to the database.
    """
    course = get_course(session, course_id, user_email)
    if course is not None:
        # Check if the given user is a professor
        user = get_user(session, user_email)
        if user is not None and user.role == "professor":
            # Make the start time and end time to be the datetime format
            start_time = datetime.datetime.fromtimestamp(start_time)
            end_time = datetime.datetime.fromtimestamp(end_time)
            app = models.App(
                name=name,
                intro=intro,
                start_time=start_time,
                end_time=end_time,
                num_entries=num_entries,
                max_students=max_students,
                template=template_link,
                binded_courses=[course]
            )
            session.add(app)
            session.commit()
            return app
        else:
            return None
    else:
        return None


def get_apps(session, course_id, user_email):
    """
    This function returns all the apps of a course.
    """
    course = get_course(session, course_id, user_email)
    if course is not None:
        return course.apps
    else:
        return None
    

def get_app(session, app_id, user_email):
    """
    This function returns an app from the database.
    """
    app = session.query(models.App).filter_by(id=app_id).first()
    if app is not None:
        course = get_course(session, app.binded_courses[0].id, user_email)
        if course is not None:
            return app
        else:
            return None
    else:
        return None
    

def edit_app(session, app_id, name, user_email, intro, start_time: int, end_time: int, num_entries, max_students, template_link):
    """
    This function edits an app in the database.
    """
    app = get_app(session, app_id, user_email)
    if app is not None:
        # Check if the given user is a professor
        user = get_user(session, user_email)
        if user is not None and user.role == "professor":
            # Make the start time and end time to be the datetime format
            start_time = datetime.datetime.fromtimestamp(start_time)
            end_time = datetime.datetime.fromtimestamp(end_time)
            app.name = name
            app.intro = intro
            app.start_time = start_time
            app.end_time = end_time
            app.num_entries = num_entries
            app.max_students = max_students
            app.template = template_link
            session.commit()
            return app
        else:
            return None
    else:
        return None
