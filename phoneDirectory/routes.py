from datetime import timedelta
from flask import session
from phoneDirectory import app


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
