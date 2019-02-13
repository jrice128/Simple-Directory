from phoneDirectory import db, login_manager

from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(255), nullable=False)
    lastName = db.Column(db.String(255), nullable=True)
    extension = db.Column(db.Integer, unique=False, nullable=True)
    title = db.Column(db.String(255), nullable=True)
    department = db.Column(db.String(255), unique=False, nullable=True)
    email = db.Column(db.String(255), unique=False, nullable=True)
    picture = db.Column(db.String(20), nullable=False, default='defaultprofile.jpg')
    building = db.Column(db.String(255), nullable=True)
    buildingLoc = db.Column(db.String(50), nullable=True, default='None')

    def __repr__(self):
        return f"Emp'{self.firstName}', ext'{self.lastName}'"


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)
