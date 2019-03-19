from datetime import timedelta
from flask import session, current_app


@current_app.before_request
def before_request():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(minutes=30)
