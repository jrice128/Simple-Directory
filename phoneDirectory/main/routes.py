import os
from flask import render_template, current_app, Blueprint
from phoneDirectory.models import Employee
import json

main = Blueprint('main', __name__)

dataPath = os.path.join(current_app.root_path, 'static', 'data.json')
with open(dataPath) as json_file:
    jsonData = json.load(json_file)
buildingImages = jsonData['BuildingImages']


@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html', employees=Employee.query.all())


@main.route("/maps")
def maps():
    return render_template('maps.html', buildingImages=buildingImages)
