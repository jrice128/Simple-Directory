import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from phoneDirectory import app, db
from phoneDirectory.emp.forms import NewEmployeeForm, EditEmployeeForm
from phoneDirectory.emp.forms import LocationForm, DeleteForm
from phoneDirectory.emp.functions import locOnImage, savePicture
from phoneDirectory.models import Employee
from flask_login import current_user, login_required

emp = Blueprint('emp', __name__)


@emp.route("/addEmployee", methods=['GET', 'POST'])
def addEmployee():
    if not current_user.is_authenticated:
        flash('Login Required.', 'danger')
        return redirect(url_for('main.home'))
    form = NewEmployeeForm()
    if form.cancel.data:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        if form.picture.data:
            picture_fn = savePicture(form.picture.data)
        else:
            picture_fn = "defaultprofile.jpg"
        employee = Employee(firstName=form.firstName.data, lastName=form.lastName.data, extension=form.extension.data,
                            title=form.title.data, department=form.department.data, email=form.email.data,
                            picture=picture_fn, building=form.building.data)
        db.session.add(employee)
        db.session.commit()
        if form.locSelect.data:
            employee = Employee.query.filter_by(email=form.email.data).first()
            return redirect(url_for('emp.empLocation', emp=employee.id))
        else:
            flash(f'Employee"{employee.firstName} {employee.lastName}" created!', 'success')
            return redirect(url_for('main.home'))
    return render_template('addEmployee.html', title='Add Employee', form=form)


@emp.route("/editEmployee", methods=['GET', 'POST'])
def editEmployee():
    if not current_user.is_authenticated:
        flash('Login Required.', 'danger')
        return redirect(url_for('main.home'))
    id = request.args['emp']
    employee = Employee.query.filter_by(id=id).first()
    if not employee:
        flash(f'Error, not a valid employee entry. Please notify site administrator. ID={id}', 'warning')
        return redirect(url_for('main.home'))
    form = EditEmployeeForm(obj=employee)
    if form.cancel.data:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        employee.firstName = form.firstName.data
        employee.lastName = form.lastName.data
        employee.extension = form.extension.data
        employee.title = form.title.data
        employee.department = form.department.data
        employee.email = form.email.data
        employee.building = form.building.data

        if form.resetPicture.data:
            if employee.picture != "defaultprofile.jpg":
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', employee.picture))
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', 'full', employee.picture))
            employee.picture = "defaultprofile.jpg"
        elif form.picture.data:
            if not isinstance(form.picture.data, str):
                if employee.picture != "defaultprofile.jpg":
                    os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', employee.picture))
                    os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', 'full', employee.picture))
                employee.picture = savePicture(form.picture.data)
        if form.resetLocation.data:
            employee.buildingLoc = 'None'
        db.session.commit()

        if form.locSelect.data:
            flash(f'form.locSelect.data = {form.locSelect.data}')
            return redirect(url_for('emp.empLocation', emp=id))
        else:
            flash(f'Employee Record for {employee.firstName} {employee.lastName} updated.',
                  'success')
            return redirect(url_for('main.home'))
    return render_template('editEmployee.html', title='Edit Employee Record', form=form)


@emp.route("/empLocation", methods=['GET', 'POST'])
@login_required
def empLocation():
    args = request.args['emp']
    if "?" in args:
        args = args.split('?')
        id = args[0]
        coords = args[1].split(',')
        xLoc = int(coords[0])
        yLoc = int(coords[1])
        employee = Employee.query.filter_by(id=id).first()
        buildingLoc = locOnImage(employee.building, xLoc, yLoc)
        return redirect(url_for('emp.empLocationConf', emp=id, img=buildingLoc))
    else:
        id = args
    employee = Employee.query.filter_by(id=id).first()
    if not employee:
        flash(f'Employee record error, please notify site administrator. ID={id}', 'danger')
        return redirect(url_for('main.home'))
    return render_template('empLocation.html', title='Add Employee Building Location',
                           emp=id, loc=employee.building)


@emp.route("/empLocationConf", methods=['GET', 'POST'])
@login_required
def empLocationConf():
    id = request.args['emp']
    buildingLoc = request.args['img']

    employee = Employee.query.filter_by(id=id).first()

    form = LocationForm()

    if form.validate_on_submit():
        if form.confirm.data:
            if employee.buildingLoc and employee.buildingLoc != 'None':
                os.remove(os.path.join(app.root_path, 'static', 'emp_locations', employee.buildingLoc))
            employee.buildingLoc = buildingLoc
            db.session.commit()
            flash(f'Location saved for {employee.firstName} {employee.lastName}')
            return redirect(url_for('main.home'))
        elif form.redo.data:
            os.remove(os.path.join(app.root_path, 'static', 'emp_locations', buildingLoc))
            return redirect(url_for('emp.empLocation', emp=id))
        elif form.cancel.data:
            os.remove(os.path.join(app.root_path,'static', 'emp_locations', buildingLoc))
            return redirect(url_for('main.home'))
    # buildingLoc = locOnImage(emp.building, xLoc, yLoc)
    return render_template('empLocationConf.html', title='Confirm Employee Building Location',
                           emp=id, map=buildingLoc, form=form)


@emp.route("/delEmployee", methods=['GET', 'POST'])
@login_required
def delEmployee():
    id = request.args['emp']
    employee = Employee.query.filter_by(id=id).first()
    if not employee:
        flash(f'Employee record error, please notify site administrator. ID={id}', 'danger')
        return redirect(url_for('main.home'))
    form = DeleteForm()
    if form.validate_on_submit():
        if form.confirm.data:
            if employee.buildingLoc and employee.buildingLoc != 'None':
                os.remove(os.path.join(app.root_path, 'static', 'emp_locations', employee.buildingLoc))
            if employee.picture != "defaultprofile.jpg":
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', employee.picture))
                os.remove(os.path.join(app.root_path, 'static', 'emp_pictures', 'full', employee.picture))
            db.session.delete(employee)
            db.session.commit()
            flash(f'Employee record deleted.', 'warning')
        elif form.cancel.data:
            flash(f'Record deletion canceled.', 'warning')
        return redirect(url_for('main.home'))

    return render_template('delEmployee.html', title='Delete Employee', first=employee.firstName,
                           last=employee.lastName, form=form)
