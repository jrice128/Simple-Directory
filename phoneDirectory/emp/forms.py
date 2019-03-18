from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, ValidationError, Regexp, Optional
from phoneDirectory import app
from phoneDirectory.models import Employee
import json
import os

# JSON data import
dataPath = os.path.join(app.root_path, 'static', 'data.json')
with open(dataPath) as json_file:
    jsonData = json.load(json_file)
buildings = [tuple(l) for l in jsonData['BuildingForm']]
departments = [tuple(l) for l in jsonData['DepartmentForm']]


class NewEmployeeForm(FlaskForm):
    firstName = StringField('First Name/Room', validators=[DataRequired(), Length(min=1, max=50),
                                                           Regexp(r'^[A-Za-z0-9\s_-]*$', flags=0,
                                                                  message=u'Invalid input.')])
    lastName = StringField('Last Name', validators=[Optional(), Length(min=1, max=50),
                                                    Regexp(r'^[A-Za-z0-9\s_-]*$', flags=0, message=u'Invalid input.')])
    extension = StringField('Extension(s)',
                            validators=[Optional(), Regexp(r'^[0-9\s,]*$', flags=0, message=u'Invalid input.')])
    title = StringField('Title', validators=[Length(max=50),
                                             Regexp(r'^[A-Za-z0-9\s_.,-]*$', flags=0, message=u'Invalid input.')])
    department = SelectField('Department', choices=departments,
                             validators=[Regexp(r'^[A-Za-z0-9\s&/_-]*$', flags=0, message=u'Invalid input.')])
    email = StringField('Email',
                        validators=[Optional(), Regexp(r'^[A-Za-z0-9./@_-]*$', flags=0, message=u'Invalid input.'),
                                    Email()])
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'tif'])])
    building = SelectField('Building', choices=buildings,
                           validators=[Regexp(r'^[A-Za-z0-9\s_-]*$', flags=0, message=u'Invalid input.')])

    cancel = SubmitField('Cancel')
    submit = SubmitField('Add Employee')
    locSelect = SubmitField('Add Employee and Pick Employee Location')

    def validate_firstName(self, firstName):
        employee = Employee.query.filter_by(lastName=self.lastName.data, firstName=self.firstName.data).all()

        if employee:
            raise ValidationError('There is already an employee with that exact name.')

    def validate_lastName(self, lastName):
        employee = Employee.query.filter_by(lastName=self.lastName.data, firstName=self.firstName.data).all()

        if employee:
            raise ValidationError('There is already an employee with that exact name.')

    def validate_email(self, email):
        email = Employee.query.filter_by(email=email.data).all()

        if email and email[0].email != '':
            raise ValidationError(
                f'There is already an employee with that exact email: ({email[0].firstName} {email[0].lastName})')

    def validate_extension(self, extension):
        extension = Employee.query.filter_by(extension=extension.data).all()

        if extension:
            raise ValidationError(
                f'There is already an employee with that extension: ({extension[0].firstName} {extension[0].lastName})')


class EditEmployeeForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50),
                                                      Regexp(r'^[A-Za-z0-9\s_-]*$', flags=0,
                                                             message=u'Invalid input.')])
    lastName = StringField('Last Name', validators=[Optional(), Length(min=1, max=50),
                                                    Regexp(r'^[A-Za-z0-9\s_-]*$', flags=0, message=u'Invalid input.')])
    extension = StringField('Extension(s)',
                            validators=[Optional(), Regexp(r'^[0-9\s,]*$', flags=0, message=u'Invalid input.')])
    title = StringField('Title', validators=[Length(max=50),
                                             Regexp(r'^[A-Za-z0-9\s_.,-]*$', flags=0, message=u'Invalid input.')])
    department = SelectField('Department', choices=departments,
                             validators=[Regexp(r'^[A-Za-z0-9\s&/_-]*$', flags=0, message=u'Invalid input.')])
    email = StringField('Email',
                        validators=[Optional(), Regexp(r'^[A-Za-z0-9./@_-]*$', flags=0, message=u'Invalid input.'),
                                    Email()])
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'tif'])])

    resetPicture = BooleanField('Reset Picture to Default')
    resetLocation = BooleanField('Reset Location')
    building = SelectField('Building', choices=buildings, validators=[Regexp(r'^[A-Za-z0-9\s_-]*$',
                                                                             flags=0, message=u'Invalid input.')])

    id = HiddenField('ID')

    cancel = SubmitField('Cancel')
    submit = SubmitField('Save Employee Record')
    locSelect = SubmitField('Save Record and Edit Employee Location')

    def validate_firstName(self, firstName):
        employee = Employee.query.filter_by(lastName=self.lastName.data, firstName=self.firstName.data).all()

        if employee and int(employee[0].id) != int(self.id.data):
            raise ValidationError(
                f'There is already an employee with that exact name. rec{employee[0].id}, form{self.id.data}')

    def validate_lastName(self, lastName):
        employee = Employee.query.filter_by(lastName=self.lastName.data, firstName=self.firstName.data).all()

        if employee and int(employee[0].id) != int(self.id.data):
            raise ValidationError('There is already an employee with that exact name.')

    def validate_email(self, email):
        email = Employee.query.filter_by(email=email.data).all()

        if email and email[0].email != '' and int(email[0].id) != int(self.id.data):
            raise ValidationError(
                f'There is already an employee with that exact email: ({email[0].firstName} {email[0].lastName})')

    def validate_extension(self, extension):
        extension = Employee.query.filter_by(extension=extension.data).all()

        if extension and int(extension[0].id) != int(self.id.data):
            raise ValidationError(
                f'There is already an employee with that extension: ({extension[0].firstName} {extension[0].lastName})')


class LocationForm(FlaskForm):
    confirm = SubmitField('Save Location Selection')
    redo = SubmitField('Redo Location Selection')
    cancel = SubmitField('Cancel Location Selection')


class DeleteForm(FlaskForm):
    confirm = SubmitField('Confirm Delete')
    cancel = SubmitField('Cancel')
