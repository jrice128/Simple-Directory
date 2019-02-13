import os
import secrets
from PIL import Image, ImageDraw
from datetime import timedelta
from flask import session, render_template, url_for, flash, redirect, request
from phoneDirectory import app, db, bcrypt
from phoneDirectory.forms import LoginForm, NewEmployeeForm, EditEmployeeForm, NewAdminForm, RegisterAdminForm
from phoneDirectory.forms import LocationForm, DeleteForm
from phoneDirectory.models import Employee, Admin
from flask_login import login_user, current_user, logout_user, login_required
import json

dataPath = os.path.join(app.root_path, 'static', 'data.json')
with open(dataPath) as json_file:
    jsonData = json.load(json_file)
buildingImages = jsonData['BuildingImages']

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', employees=Employee.query.all())


@app.route("/maps")
def maps():
    return render_template('maps.html', buildingImages=buildingImages)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f'Already logged in!', 'warning')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Incorrect Credentials.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/admins")
@login_required
def admins():
    adminList = Admin.query.all()
    admin = []
    for entry in adminList:
        admin.append(entry.email)
    return render_template('admins.html', admin=admin)


@app.route("/delAdmin", methods=['GET', 'POST'])
@login_required
def delAdmin():
    if Admin.query.count() == 1:
        flash(f'Please appoint a new Administrator before deleting this account.', 'danger')
        return redirect(url_for('admins'))
    email = request.args['email']
    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        flash(f'Error, {email} not a registered Administrator.')
        return redirect(url_for('admins'))
    form = DeleteForm()
    if form.validate_on_submit():
        if form.confirm.data:
            db.session.delete(admin)
            db.session.commit()
            flash(f'Administrator record deleted.', 'warning')
            return redirect(url_for('admins'))
        elif form.cancel.data:
            flash(f'Record deletion canceled.', 'warning')
            return redirect(url_for('admins'))
        else:
            return redirect(url_for('home'))
    return render_template('delAdmin.html', title='Delete Administrator', email=email, form=form)


@app.route("/addAdmin", methods=['GET', 'POST'])
@login_required
def addAdmin():
    form = NewAdminForm()
    if form.cancel.data:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        admin = Admin(email=form.email.data)
        db.session.add(admin)
        db.session.commit()
        flash(
            f'Administrator account for {admin.email} created. Please go to phone.yourcompany.com/register to finalize account.')
        return redirect(url_for('home'))
    return render_template('addAdmin.html', title='Add Administrator', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterAdminForm()

    if form.cancel.data:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        newAdmin = Admin.query.filter_by(email=form.email.data).first()
        if newAdmin:
            if newAdmin.password == None:
                newAdmin.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                db.session.add(newAdmin)
                db.session.commit()
                flash(f'New administrator account created for {newAdmin.email}.')
                return redirect(url_for('login'))

    return render_template('register.html', title='Register New Administrator', form=form)


def save_picture(formPicture):
    random_hex = secrets.token_hex(8)
    _, fExt = os.path.splitext(formPicture.filename)
    pictureFn = random_hex + fExt
    picturePath = os.path.join(app.root_path, 'static', 'emp_pictures', pictureFn)
    fullPicturePath = os.path.join(app.root_path, 'static', 'emp_pictures', 'full', pictureFn)
    formPicture.save(fullPicturePath)
    outputSize = (100, 100)
    image = Image.open(formPicture)
    image.thumbnail(outputSize)
    image.save(picturePath)
    return pictureFn


@app.route("/addEmployee", methods=['GET', 'POST'])
def addEmployee():
    if not current_user.is_authenticated:
        flash('Login Required.', 'danger')
        return redirect(url_for('home'))
    form = NewEmployeeForm()
    if form.cancel.data:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        if form.picture.data:
            picture_fn = save_picture(form.picture.data)
        else:
            picture_fn = "defaultprofile.jpg"
        emp = Employee(firstName=form.firstName.data,
                       lastName=form.lastName.data, extension=form.extension.data,
                       title=form.title.data, department=form.department.data, email=form.email.data,
                       picture=picture_fn, building=form.building.data)
        db.session.add(emp)
        db.session.commit()
        if form.locSelect.data:
            emp = Employee.query.filter_by(email=form.email.data).first()
            return redirect(url_for('empLocation', emp=emp.id))
        else:
            flash(f'Employee"{emp.firstName} {emp.lastName}" created!', 'success')
            return redirect(url_for('home'))
    return render_template('addEmployee.html', title='Add Employee', form=form)


@app.route("/editEmployee", methods=['GET', 'POST'])
def editEmployee():
    if not current_user.is_authenticated:
        flash('Login Required.', 'danger')
        return redirect(url_for('home'))
    id = request.args['emp']
    emp = Employee.query.filter_by(id=id).first()
    if not emp:
        flash(f'Error, not a valid employee entry. Please notify site administrator. ID={id}', 'warning')
        return redirect(url_for('home'))
    form = EditEmployeeForm(obj=emp)
    if form.cancel.data:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        emp.firstName = form.firstName.data
        emp.lastName = form.lastName.data
        emp.extension = form.extension.data
        emp.title = form.title.data
        emp.department = form.department.data
        emp.email = form.email.data
        emp.building = form.building.data

        if form.resetPicture.data:
            if emp.picture != "defaultprofile.jpg":
                # picture_path = os.path.join(app.root_path, 'static/emp_pictures', emp.picture)
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', emp.picture))
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', 'full', emp.picture))
            emp.picture = "defaultprofile.jpg"
        elif form.picture.data:
            if not isinstance(form.picture.data, str):
                if emp.picture != "defaultprofile.jpg":
                    # picture_path = os.path.join(app.root_path, 'static/emp_pictures', emp.picture)
                    os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', emp.picture))
                    os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', 'full', emp.picture))
                emp.picture = save_picture(form.picture.data)
        if form.resetLocation.data:
            emp.buildingLoc = 'None'
        db.session.commit()

        if form.locSelect.data:
            flash(f'form.locSelect.data = {form.locSelect.data}')
            return redirect(url_for('empLocation', emp=id))
        else:
            flash(f'Employee Record for {emp.firstName} {emp.lastName} updated.',
                  'success')
            return redirect(url_for('home'))
    return render_template('editEmployee.html', title='Edit Employee Record', form=form)


def locOnImage(building, xLoc, yLoc):
    random_hex = secrets.token_hex(8)
    pictureFn = random_hex + '.png'
    sourceImgPath = os.path.join(app.root_path, 'static', 'building_maps', buildingImages[building])
    saveImgPath = os.path.join(app.root_path, 'static', 'emp_locations', pictureFn)

    image = Image.open(sourceImgPath)
    draw = ImageDraw.Draw(image)
    r = 15
    draw.ellipse((xLoc - r, yLoc - r, xLoc + r, yLoc + r), fill=(0, 156, 104, 150))
    image.save(saveImgPath)
    return pictureFn


@app.route("/empLocation", methods=['GET', 'POST'])
@login_required
def empLocation():
    args = request.args['emp']
    if "?" in args:
        args = args.split('?')
        id = args[0]
        coords = args[1].split(',')
        xLoc = int(coords[0])
        yLoc = int(coords[1])
        emp = Employee.query.filter_by(id=id).first()
        buildingLoc = locOnImage(emp.building, xLoc, yLoc)
        return redirect(url_for('empLocationConf', emp=id, img=buildingLoc))
    else:
        id = args
    emp = Employee.query.filter_by(id=id).first()
    if not emp:
        flash(f'Employee record error, please notify site administrator. ID={id}', 'danger')
        return redirect(url_for('home'))
    return render_template('empLocation.html', title='Add Employee Building Location',
                           emp=id, loc=emp.building)


@app.route("/empLocationConf", methods=['GET', 'POST'])
@login_required
def empLocationConf():
    id = request.args['emp']
    buildingLoc = request.args['img']

    emp = Employee.query.filter_by(id=id).first()

    form = LocationForm()

    if form.validate_on_submit():
        if form.confirm.data:
            if emp.buildingLoc and emp.buildingLoc != 'None':
                os.remove(os.path.join(app.root_path, 'static', 'emp_locations', emp.buildingLoc))
            emp.buildingLoc = buildingLoc
            db.session.commit()
            flash(f'Location saved for {emp.firstName} {emp.lastName}')
            return redirect(url_for('home'))
        elif form.redo.data:
            os.remove(os.path.join(app.root_path, 'static', 'emp_locations', buildingLoc))
            return redirect(url_for('empLocation', emp=id))
        elif form.cancel.data:
            os.remove(os.path.join(app.root_path,'static', 'emp_locations', buildingLoc))
            return redirect(url_for('home'))
    # buildingLoc = locOnImage(emp.building, xLoc, yLoc)
    return render_template('empLocationConf.html', title='Confirm Employee Building Location',
                           emp=id, map=buildingLoc, form=form)


@app.route("/delEmployee", methods=['GET', 'POST'])
@login_required
def delEmployee():
    id = request.args['emp']
    emp = Employee.query.filter_by(id=id).first()
    if not emp:
        flash(f'Employee record error, please notify site administrator. ID={id}', 'danger')
        return redirect(url_for('home'))
    form = DeleteForm()
    if form.validate_on_submit():
        if form.confirm.data:
            if emp.buildingLoc and emp.buildingLoc != 'None':
                os.remove(os.path.join(app.root_path, 'static', 'emp_locations', emp.buildingLoc))
            if emp.picture != "defaultprofile.jpg":
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', emp.picture))
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', 'full', emp.picture))
            db.session.delete(emp)
            db.session.commit()
            flash(f'Employee record deleted.', 'warning')
            return redirect(url_for('home'))
        elif form.cancel.data:
            flash(f'Record deletion canceled.', 'warning')
            return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))
    return render_template('delEmployee.html', title='Delete Employee', first=emp.firstName,
                           last=emp.lastName, form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out.', 'success')
    return redirect(url_for('home'))
