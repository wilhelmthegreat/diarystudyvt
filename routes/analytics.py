from flask import Blueprint, request, Response
from urllib.parse import quote
from config.database import database_uri
import database.connect as database
from flask_cors import CORS, cross_origin
from utils.jwt_utils import validate_token_in_request, generate_token
from utils.api_response_wrapper import (
    success_response,
    client_error_response,
    server_error_response,
)
from datetime import datetime
from dsmodelling import modelling
from dsmodelling import lda_modelling

# Set up the routes blueprint
analytics_routes = Blueprint("analytics_routes", __name__)

@analytics_routes.route("/", methods=["GET"])
@analytics_routes.route("", methods=["GET"])
def get_entries_dashboard(course_id:int, app_id: int):
    """This route will get the wordcloud object of all entries in a coures if the user is a professor"""
    jwt_result = validate_token_in_request(request)
    if jwt_result["code"] != 0:
        return client_error_response(
            data={},
            internal_code=jwt_result["code"],
            status_code=401,
            message=jwt_result["message"],
        )
    payload = jwt_result["data"]
    email = payload["email"]
    # Check if the user set the parameter indicating the limit of words to be shown
    limit = request.args.get("limit")
    limit_num = 12 # Default value
    if limit is not None and limit.isdigit() and int(limit) > 0 and int(limit) < 100:
        limit_num = int(limit)
    elif limit is not None:
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=400,
            message="Invalid limit value, you must provide a number between 1 and 100",
        )
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    user = database.get_user(session=session, email=email)
    if user is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found",
        )
    # Check if the given course_id and app_id are valid
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found or you are not enrolled in this app",
        )
    entries = database.get_app_entries(session=session, app_id=app_id, user_email=email)
    all_entries = []
    sents = []
    for entry in entries:
        all_entries.append(entry.content)
        usr = database.get_user_by_id(session, entry.student_id)
        sents.append({
            'sentence': modelling.get_sentence_no_word(entry.content),
            'sentiment': modelling.sentiment(entry.content),
            'user': usr.first_name+" "+usr.last_name,
            'user_id': entry.student_id,
            })
    stopw = []
    for stopword in app.stopwords:
        stopw.append(stopword.word)
    session.close()
    return success_response(data={
        "wordcloud": modelling.word_cloud('\n'.join(all_entries), stopw, limit_num),
        "sentences": sents,
        "graph": [{'x': modelling.word_count(e), 'y': modelling.sentiment(e)} for e in all_entries]
        })


@analytics_routes.route("/word_relations/<word>", methods=["GET"])
@analytics_routes.route("/word_relations/<word>", methods=["GET"])
def word_clicked_dashboard(course_id:int, app_id:int, word:str):
    """This route will get the wordcloud object of all entries in a coures if the user is a professor"""
    jwt_result = validate_token_in_request(request)
    if jwt_result["code"] != 0:
        return client_error_response(
            data={},
            internal_code=jwt_result["code"],
            status_code=401,
            message=jwt_result["message"],
        )
    payload = jwt_result["data"]
    email = payload["email"]
    # Check if the user set the parameter indicating the limit of words to be shown
    limit = request.args.get("limit")
    limit_num = 12 # Default value
    if limit is not None and limit.isdigit() and int(limit) > 0 and int(limit) < 100:
        limit_num = int(limit)
    elif limit is not None:
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=400,
            message="Invalid limit value, you must provide a number between 1 and 100",
        )
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    user = database.get_user(session=session, email=email)
    if user is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found",
        )
    # Check if the given course_id and app_id are valid
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found or you are not enrolled in this app",
        )
    entries = database.get_app_entries(session=session, app_id=app_id, user_email=email)
    all_entries = []
    sents = []
    for entry in entries:
        all_entries.append(entry.content)
        sent = modelling.get_sentence(entry.content, word)
        if sent is not None:
            usr = database.get_user_by_id(session, entry.student_id)
            sents.append({
                'sentence': sent,
                'sentiment': modelling.sentiment(entry.content),
                'user': usr.first_name+" "+usr.last_name,
                'user_id': entry.student_id,
                })
    stopw = []
    for stopword in app.stopwords:
        stopw.append(stopword.word)
    session.close()
    return success_response(data={
        'wordcloud': modelling.associated_word_cloud('\n'.join(all_entries), word, stopw, limit_num),
        'sentences': sents
    })


@analytics_routes.route("/lda_html", methods=["GET"])
@analytics_routes.route("/lda_html/", methods=["GET"])
def lda_html(course_id:int, app_id:int):
    """This route will get the lda visualization in html format"""
    jwt_result = validate_token_in_request(request)
    if jwt_result["code"] != 0:
        return client_error_response(
            data={},
            internal_code=jwt_result["code"],
            status_code=401,
            message=jwt_result["message"],
        )
    payload = jwt_result["data"]
    email = payload["email"]
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    user = database.get_user(session=session, email=email)
    if user is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found",
        )
    # Check if the given course_id and app_id are valid
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found or you are not enrolled in this app",
        )
    entries = database.get_app_entries(session=session, app_id=app_id, user_email=email)
    all_entries = []
    for entry in entries:
        all_entries.append(entry.content)
    session.close()
    if len(all_entries) == 0:
        return '<h1>No entries found in this app!</h1>'
    lda_model, corpus, dictionary = lda_modelling.lda_model(all_entries, num_topics=4, passes=15)
    lda_visualization_html = lda_modelling.lda_visualization_html(lda_model, corpus, dictionary)
    return lda_visualization_html
