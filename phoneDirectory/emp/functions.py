import os
import secrets
from PIL import Image, ImageDraw
from flask import current_app
import json

dataPath = os.path.join(current_app.root_path, 'static', 'data.json')
with open(dataPath) as json_file:
    jsonData = json.load(json_file)
buildingImages = jsonData['BuildingImages']


def locOnImage(building, xLoc, yLoc):
    random_hex = secrets.token_hex(8)
    pictureFn = random_hex + '.png'
    sourceImgPath = os.path.join(current_app.root_path, 'static', 'building_maps', buildingImages[building])
    saveImgPath = os.path.join(current_app.root_path, 'static', 'emp_locations', pictureFn)

    image = Image.open(sourceImgPath)
    draw = ImageDraw.Draw(image)
    r = 15
    draw.ellipse((xLoc - r, yLoc - r, xLoc + r, yLoc + r), fill=(0, 156, 104, 150))
    image.save(saveImgPath)
    return pictureFn


def savePicture(formPicture):
    random_hex = secrets.token_hex(8)
    _, fExt = os.path.splitext(formPicture.filename)
    pictureFn = random_hex + fExt
    picturePath = os.path.join(current_app.root_path, 'static', 'emp_pictures', pictureFn)
    fullPicturePath = os.path.join(current_app.root_path, 'static', 'emp_pictures', 'full', pictureFn)
    formPicture.save(fullPicturePath)
    outputSize = (100, 100)
    image = Image.open(formPicture)
    image.thumbnail(outputSize)
    image.save(picturePath)
    return pictureFn
