import os,shutil,glob,random,string,secrets
from pdf2image import convert_from_path
from pathlib import Path
from .models import *
from dateutil.relativedelta import relativedelta
from datetime import datetime

##########################################################

# helper.py

##########################################################

absolute_path = os.path.dirname(os.path.abspath(__file__))
app_root = Path(__file__).parents[1]

def dir_last_updated():
	folder = absolute_path + '/static'

	return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

##########################################################

# methods.py

##########################################################

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



##########################################################

# python_scripts.py

##########################################################

def convert_to_boolean(str):
	if str == 'true':
		return True
	return False

def put_to_zero(str):
	if str == '':
		return 0
	return str

def secret_code_generator(myupper,mydigit):

	val = ''.join(random.choice(string.ascii_uppercase) for i in range(myupper))
	val += ''.join(random.choice(string.digits) for i in range(mydigit))

	mylist = list(val)
	random.shuffle(mylist)
	code = ''.join(mylist)
	return code

def create_role():
	roles = ['Admin','Municipality','User','Contractor']

	for role in roles:
		dif_role = Role(name=role)
	db.session.add(dif_role)
	db.session.commit()

def remove_new_line(mysentence):
	line = mysentence.replace("\n"," ")
	return line


##########################################################

# accounts/views.py

##########################################################



##########################################################

# main/views.py

##########################################################


def save_picture_gas(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    picture_path = os.path.join(app_root, 'static/gas_photo', picture_fn)
    i = Image.open(form_picture)
    i.save(picture_path)

    return picture_fn


def save_picture_appliance(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    picture_path = os.path.join(app_root, 'static/appliance_photos/img/', picture_fn)
    i = Image.open(form_picture)
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

def save_video(form_picture,location):
	random_hex = secrets.token_hex(8)
	file_extension = os.path.splitext(form_picture.filename)[1]
	picture_filename = random_hex + file_extension
	picture_path = os.path.join(app_root,'benchmarking_tool/static/'+location,picture_filename)
	form_picture.save(picture_path)
	return picture_filename

def transform_date(my_weeks):
    currentDate = datetime.now()
    newDate = currentDate + relativedelta(weeks=my_weeks)
    return newDate.strftime('%m/%d/%Y')

