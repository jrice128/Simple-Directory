from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from phoneDirectory.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    with app.app_context():

        from phoneDirectory import routes
        from phoneDirectory.emp.routes import emp
        app.register_blueprint(emp)
        from phoneDirectory.auth.routes import auth
        app.register_blueprint(auth)
        from phoneDirectory.main.routes import main
        app.register_blueprint(main)
        from phoneDirectory.errors.handlers import errors
        app.register_blueprint(errors)

    return app
