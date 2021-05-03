import os
import random
import string
import secrets
from benchmarking_tool.models import *


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

def remove_dash_or_double_space(mysentence):
	line = mysentence[-9:]
	if '  ' in line:
		line = mysentence.replace("  "," ")
		return line[-7:]
	if '-' in line:
		line = mysentence.replace("-"," ")
		return line[-7:]
	else:
		return line[-7:]

