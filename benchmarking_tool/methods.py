import os, shutil,glob
import secrets
from pdf2image import convert_from_path
import re
from difflib import get_close_matches
from pathlib import Path
import PIL
from PIL import Image,ExifTags
import numpy as np
import argparse
import random
import cv2

root_path = os.path.dirname(os.path.abspath(__file__))


def create_temp_folder(the_file):
	random_hex = secrets.token_hex(8)
	f_route = root_path+'/static/temp_folder/'+random_hex+'/'
	f_name = the_file.split('.')[0].split('/')[-1]
	f_extension= the_file.split('.')[1]
	os.mkdir(f_route)
	new_file = shutil.copy(the_file, f_route)
	if f_extension == 'pdf':
		image = convert_from_path(new_file,500)
		for indx,element in enumerate(image):
			new_filename = f_route+str(indx)+f_name+'.jpg'
			element.save(new_filename,'JPEG')
	return f_route

def get_all_jpg(folder):
	return glob.glob(folder+"/*.jpg")


def save_picture_gas(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    picture_path = os.path.join(root_path, 'static/gas_photo', picture_fn)
    i = Image.open(form_picture)
    i.save(picture_path)

    return picture_fn



def save_picture(form_picture,location):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    picture_path = os.path.join(root_path,'static/'+location, picture_fn)
    i = Image.open(form_picture)
    if hasattr(i, '_getexif'):
        exifdata = i._getexif()
        try:
            orientation = exifdata.get(274)
        except:
            # There was no EXIF Orientation Data
            orientation = 1
    else:
        orientation = 1
    if orientation is 1:    # Horizontal (normal)
        pass
    elif orientation is 2:  # Mirrored horizontal
        i = i.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 3:  # Rotated 180
        i = i.rotate(180)
    elif orientation is 4:  # Mirrored vertical
        i = i.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 5:  # Mirrored horizontal then rotated 90 CCW
        i = i.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 6:  # Rotated 90 CCW
        i = i.rotate(-90)
    elif orientation is 7:  # Mirrored horizontal then rotated 90 CW
        i = i.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 8:  # Rotated 90 CW
        i = i.rotate(90)
    i.save(picture_path)
    return picture_fn





def save_picture_appliance(form_picture,location):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(root_path,'static/'+location, picture_fn)
    maxsize = (1028, 1028)
    i = Image.open(form_picture)
    if hasattr(i, '_getexif'):
        exifdata = i._getexif()
        try:
            orientation = exifdata.get(274)
        except:
            # There was no EXIF Orientation Data
            orientation = 1
    else:
        orientation = 1
    if orientation is 1:    # Horizontal (normal)
        pass
    elif orientation is 2:  # Mirrored horizontal
        i = i.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 3:  # Rotated 180
        i = i.rotate(180)
    elif orientation is 4:  # Mirrored vertical
        i = i.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 5:  # Mirrored horizontal then rotated 90 CCW
        i = i.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 6:  # Rotated 90 CCW
        i = i.rotate(-90)
    elif orientation is 7:  # Mirrored horizontal then rotated 90 CW
        i = i.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation is 8:  # Rotated 90 CW
        i = i.rotate(90)
    i.save(picture_path)
    return picture_fn


def closeMatches(patterns, word):
     y = get_close_matches(word, patterns,1,0.8)
     print(y)
     return y

def closeMatchesInitial(wordlist,word):
    y = []
    for i in wordlist:
        text = i
        x = re.search(text.lower(),word.lower())
        if x:
            y.append(i)
    return y

def img_array(image):
    from tensorflow.keras.preprocessing.image import img_to_array

# construct the argument parse and parse the arguments
    # load the image
    image = cv2.imread(image)
    orig = image.copy()

    # pre-process the image for classification
    image = cv2.resize(image, (28, 28))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)


    lists = image.tolist()
    return lists


def get_city(sentence):
	myword = sentence.split(',')
	return myword[0]

