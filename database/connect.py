from sqlalchemy.engine import create_engine
from sqlalchemy import event, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, Session
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


def adding_user(session: Session, first_name: str, last_name: str, email: str, role: str="student") -> bool:
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
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role
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


def get_user(session, email) -> models.User:
    """
    This function checks if a user is in the database.

    @param session: sqlalchemy.orm.session.Session, the session to use to check the user
    @param email: str, the email of the user
    """
    user: models.User = session.query(models.User).filter_by(email=email).first()
    if user is not None:
        return user
    else:
        return None
    

def get_user_by_id(session: Session, user_id: int) -> models.User:
    """
    This function returns a user from the database.
    """
    user: models.User = session.query(models.User).filter_by(id=user_id).first()
    if user is not None:
        return user
    else:
        return None
    

def get_student(session: Session, user_email: str) -> models.Student:
    """
    This function returns a student from the database
    """
    user = get_user(session, user_email)
    if user is not None:
        if user.role == "student":
            return user.students[0]
        else:
            return None
    else:
        return None
    

def get_student_by_id(session: Session, student_id: int) -> models.Student:
    """
    This function returns a student from the database.
    """
    student: models.Student = session.query(models.Student).filter_by(id=student_id).first()
    if student is not None:
        return student
    else:
        return None


def adding_course(session: Session, course_name: str, course_number: int, professor_email: str) -> bool:
    """
    This function adds a course to the database. If the course already exists, it returns False.
    Otherwise, it adds the course and returns True.
    """
    course: models.Course = session.query(models.Course).filter_by(name=course_name).first()
    professor: models.Professor = session.query(models.Professor).filter_by(email=professor_email).first()
    if course is None:
        course: models.Course = models.Course(name=course_name, identifier=course_number)
        if professor is not None:
            course.professors.append(professor)
            session.add(course)
            session.commit()
            return True
        else:
            return False
    else:
        return False


def get_course(session: Session, course_id: int, user_email: str) -> models.Course:
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
        
        


def edit_course(session: Session, course_id: int, course_name: str, course_number: str, user_email: str) -> models.Course:
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


def join_course(session: Session, course_id: id, student_email: str) -> bool:
    """
    This function adds a student to a course. If the student is already in the course, it returns False.
    Otherwise, it adds the student to the course and returns True.
    """
    course = session.query(models.Course).filter_by(id=course_id).first()
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


def get_courses(session: Session, user_email: str) -> list:
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
    
    
def add_app(session: Session, course_id: int, user_email: str, name: str, intro: str, start_time: int, end_time: int, num_entries: int, max_students: int, template_link: str, stopwords: list):
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
            for stopword in stopwords:
                app.stopwords.append(
                    models.Stopword(word=stopword)
                )
            session.add(app)
            session.commit()
            return app
        else:
            return None
    else:
        return None


def get_apps(session: Session, course_id: int, user_email: str) -> list:
    """
    This function returns all the apps of a course.
    """
    course = get_course(session, course_id, user_email)
    if course is not None:
        return course.apps
    else:
        return None
    

def get_app(session: Session, app_id: int, user_email: str) -> models.App:
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
    

def edit_app(session: Session, app_id: int, app_name: str, user_email: str, intro: str, start_time: int, end_time: int, num_entries: int, max_students: int, template_link: str, stopwords: list=[]) -> models.App:
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
            app.name = app_name
            app.intro = intro
            app.start_time = start_time
            app.end_time = end_time
            app.num_entries = num_entries
            app.max_students = max_students
            app.template = template_link
            # Get the stopwords of the app
            app_stopwords = [stopword.word for stopword in app.stopwords]
            # Check if each item in app_stopwords is in stopwords
            # if not, disable the stopword
            for stopword in app_stopwords:
                if stopword not in stopwords:
                    app.stopwords[app_stopwords.index(stopword)].enabled = False
            # Check if each item in stopwords is in app_stopwords
            # if not, add the stopword
            for stopword in stopwords:
                if stopword not in app_stopwords:
                    app.stopwords.append(
                        models.Stopword(word=stopword)
                    )
            session.commit()
            return app
        else:
            return None
    else:
        return None


def join_app(session: Session, app_id: int, student_email: str) -> bool:
    """
    This function adds a student to an app. If the student is already in the app, it returns False.
    Otherwise, it adds the student to the app and returns True.
    """
    app = session.query(models.App).filter_by(id=app_id).first()
    student = session.query(models.Student).filter_by(email=student_email).first()
    if app is not None and student is not None:
        if student not in app.enrolled_students:
            app.enrolled_students.append(student)
            session.commit()
            return True
        else:
            return False
    else:
        return False


def check_user_in_app(session: Session, app_id: int, user_email: str) -> bool:
    """
    This function checks if a user is enrolled in an app.
    """
    app = get_app(session, app_id, user_email)
    user = get_user(session, user_email)
    if app is not None and user is not None:
        if user.role == "student":
            if user.students[0] in app.enrolled_students:
                return True
            else:
                return False
        elif user.role == "professor":
            if user.professors[0] in get_course(session, app.binded_courses[0].id, user_email).professors:
                return True
            else:
                return False
    else:
        return False


def get_app_entries(session: Session, app_id: int, user_email: str) -> list[models.Entry]:
    """
    This function returns all the entries of an app.
    """
    app = get_app(session, app_id, user_email)
    if app is not None:
        # Check if the user is a student
        user = get_user(session, user_email)
        if user is not None and user.role == "student":
            # Check if the student is enrolled in the app
            entries = []
            if user.students[0] in app.enrolled_students:
                # Get the entries authored by the student
                for entry in app.entry_list:
                    if entry.student_id == user.students[0].id:
                        entries.append(entry)
                return entries
            else:
                return None
        elif user is not None and user.role == "professor":
            # Check if the professor is the owner of the app
            if user.professors[0] in get_course(session, app.binded_courses[0].id, user_email).professors:
                return app.entry_list
            else:
                return None
    else:
        return None


def add_entry(session: Session, app_id: int, student_email: str, entry_text: str, study_start_time: int, study_duration_minutes: int, create_at = datetime.datetime.now(), update_at = datetime.datetime.now()) -> models.Entry:
    """
    This function adds an entry to the database.
    """
    app = get_app(session, app_id, student_email)
    student = session.query(models.Student).filter_by(email=student_email).first()
    if app is not None and student is not None:
        # Check if the student is enrolled in the app
        if student in app.enrolled_students:
            entry = models.Entry(
                student_id=student.id,
                app_id=app.id,
                content=entry_text,
                study_start_time=datetime.datetime.fromtimestamp(study_start_time),
                study_duration_minutes=study_duration_minutes,
                create_at=create_at,
                update_at=update_at
            )
            session.add(entry)
            session.commit()
            # Add the entry to the app
            app.entry_list.append(entry)
            session.commit()
            return entry
        else:
            return None
    else:
        return None


def get_entry(session: Session, entry_id: int, user_email: str) -> models.Entry:
    """
    This function returns an entry from the database.
    """
    entry: models.Entry = session.query(models.Entry).filter_by(id=entry_id).first()
    if entry is not None:
        app = get_app(session, entry.app_id, user_email)
        # Check if the app is not None
        if app is not None:
            # Check if the user is a student
            user = get_user(session, user_email)
            if user is not None and user.role == "student":
                # Check if the student is enrolled in the app
                if user.students[0] in app.enrolled_students:
                    # Check if the student is the owner of the entry
                    if user.students[0].id == entry.student_id:
                        return entry
                    else:
                        return None
                else:
                    return None
            elif user is not None and user.role == "professor":
                # Check if the professor is the owner of the app
                if user.professors[0] in get_course(session, app.binded_courses[0].id, user_email).professors:
                    return entry
                else:
                    return None
                
    

def edit_entry(session: Session, entry_id: int, user_email: str, entry_text: str, study_start_time: int, study_duration_minutes: int, update_at = datetime.datetime.now()) -> models.Entry:
    """
    This function edits an entry in the database.
    """
    entry = get_entry(session, entry_id, user_email)
    if entry is not None:
        entry.content = entry_text
        entry.study_start_time = datetime.datetime.fromtimestamp(study_start_time)
        entry.study_duration_minutes = study_duration_minutes
        entry.update_at = update_at
        session.commit()
        return entry
    else:
        return None
                