from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


from phoneDirectory import routes
from phoneDirectory.emp.routes import emp
from phoneDirectory.auth.routes import auth
from phoneDirectory.main.routes import main

app.register_blueprint(emp)
app.register_blueprint(auth)
app.register_blueprint(main)