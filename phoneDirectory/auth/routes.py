from flask import  render_template, url_for, flash, redirect, request, Blueprint
from phoneDirectory import db, bcrypt
from phoneDirectory.auth.forms import LoginForm, NewAdminForm, RegisterAdminForm, DeleteForm
from phoneDirectory.models import Admin
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint('auth', __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f'Already logged in!', 'warning')
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash('Incorrect Credentials.', 'danger')
    return render_template('login.html', title='Login', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out.', 'success')
    return redirect(url_for('main.home'))


@auth.route("/admins")
@login_required
def admins():
    adminList = Admin.query.all()
    admin = []
    for entry in adminList:
        admin.append(entry.email)
    return render_template('admins.html', admin=admin)


@auth.route("/delAdmin", methods=['GET', 'POST'])
@login_required
def delAdmin():
    if Admin.query.count() == 1:
        flash(f'Please appoint a new Administrator before deleting this account.', 'danger')
        return redirect(url_for('auth.admins'))
    email = request.args['email']
    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        flash(f'Error, {email} not a registered Administrator.')
        return redirect(url_for('auth.admins'))
    form = DeleteForm()
    if form.validate_on_submit():
        if form.confirm.data:
            db.session.delete(admin)
            db.session.commit()
            flash(f'Administrator record deleted.', 'warning')
            return redirect(url_for('auth.admins'))
        elif form.cancel.data:
            flash(f'Record deletion canceled.', 'warning')
            return redirect(url_for('auth.admins'))
        else:
            return redirect(url_for('main.home'))
    return render_template('delAdmin.html', title='Delete Administrator', email=email, form=form)


@auth.route("/addAdmin", methods=['GET', 'POST'])
@login_required
def addAdmin():
    form = NewAdminForm()
    if form.cancel.data:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        admin = Admin(email=form.email.data)
        db.session.add(admin)
        db.session.commit()
        flash(
            f'Administrator account for {admin.email} created. '
            f'Please go to phone.yourcompany.com/register to finalize account.')
        return redirect(url_for('main.home'))
    return render_template('addAdmin.html', title='Add Administrator', form=form)


@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterAdminForm()

    if form.cancel.data:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        newAdmin = Admin.query.filter_by(email=form.email.data).first()
        if newAdmin:
            if newAdmin.password is None:
                newAdmin.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                db.session.add(newAdmin)
                db.session.commit()
                flash(f'New administrator account created for {newAdmin.email}.')
                return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register New Administrator', form=form)
