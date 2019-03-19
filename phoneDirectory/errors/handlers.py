from flask import Blueprint, render_template, request

errors = Blueprint('errors', __name__)

errorTextBase = "Hello, I received the following error when accessing the directory:\n"


@errors.app_errorhandler(404)
@errors.app_errorhandler(410)
@errors.app_errorhandler(500)
def httperror(error):
    errorText = errorTextBase + \
                f"\n\nError Code: {error.code}" \
                f"\nURL Requested: {request.url}" \
                f"\nReferrer:{request.referrer}"

    if error.code == 404:
        return render_template('errors/404.html',
                               urlPath=request.url,
                               errorCode=error.code,
                               urlRef=request.referrer,
                               errorText=errorText), error.code
    else:
        return render_template('errors/error.html',
                               urlPath=request.url,
                               errorCode=error.code,
                               urlRef=request.referrer,
                               errorText=errorText), error.code
