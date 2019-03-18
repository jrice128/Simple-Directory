from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),
                                             Regexp(r'^[A-Za-z0-9./@_-]*$', flags=0, message=u'Invalid input.'),
                                             Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


class NewAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),
                                             Regexp(r'^[A-Za-z0-9./@_-]*$', flags=0, message=u'Invalid input.'),
                                             Email()])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


class DeleteForm(FlaskForm):
    confirm = SubmitField('Confirm Delete')
    cancel = SubmitField('Cancel')
