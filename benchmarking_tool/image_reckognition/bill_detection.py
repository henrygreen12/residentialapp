
import os, io
from google.cloud import vision
import pandas as pd
import numpy as np
from sqlalchemy.orm import load_only


root_path = os.path.dirname(os.path.abspath(__file__))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = root_path+"/MyFirstProject-aa47e5bcc8a2.json" #API


client = vision.ImageAnnotatorClient()


def detectText(img): #google recognition function
	with io.open(img, 'rb') as image_file:
		content = image_file.read()

	image = vision.Image(content=content)
	response = client.text_detection(image=image)
	texts = response.text_annotations

	df = pd.DataFrame(columns=['locale', 'description'])
	for text in texts:
		df = df.append(
			dict(
				locale=text.locale,
				description=text.description
			),
			ignore_index=True
		)
	return df

companies = ['atco', 'epcor']

def detect_company(x):
	y = 'error'
	for index, row in x.iterrows():
		if row[1].lower() in companies:
			y =  row[1].lower()
			break
	return y




def detect_atco(x):
	index_found = 0
	found_kwh = []
	found = ''
	address_found = ''
	electricty_charged = 0
	city = ''

	#cutting out natural gas just in case it is in bill
	for index_cut, row_cut in x.iterrows():
		if row_cut[1].lower() == 'natural' and x.at[index_cut+1,'description'].lower() == 'gas' and x.at[index_cut+2,'description'].lower() == 'site':
			x = x[0:index_cut]
			y = x
			break


	# finding address on atco bill
	for index, row in x.iterrows():
		if (row[1].lower() == 'ab'):
			address_found = x.at[index-4,'description'] +' '+ x.at[index-3,'description']+ ' ' + x.at[index-2,'description']
			city = x.at[index-1,'description'].lower()

	#finding the KWH used and appending to list
	for index, row in x.iterrows():
		if row[1].lower() == 'kwh':
			index_found = index
			y = x[index_found-1:index_found+1]
			for index_match, row_match in y.iterrows():
				found = row_match[1]
				try:
					float(found)
					print('found_value' + found)
					found_kwh.append(found)
				except:
					pass
				try:
					found = found.replace("(","")
					float(found)
					print('found_value' + found)
					found_kwh.append(found)
				except:
					continue


	#finding the price paid for atco and appending it to list
	for index, row in x.iterrows():
		if row[1].lower() == 'current' and x.at[index+1,'description'].lower() == 'billing':
			y = x[index_found-2:index_found+2]
			for index_match, row_match in y.iterrows():
				found = row_match[1]
				try:
					float(found)
					print('found_value_current_billing' + found)
				except:
					continue
	return found_kwh, address_found, electricty_charged, city





def detect_epcor(x):
	y = x
	found_kwh = []
	found = ''
	electricty_charged = 0
	city = ''
	# finding possible values for KWH epcor
	for index, row in x.iterrows():
		if row[1].lower() == 'kwh' and x.at[index-2,'description'] == 'used:':
			index_found = index
			y = x[index_found-2:index_found+2]
			for index_match, row_match in y.iterrows():
				found = row_match[1]
				try:
					float(found)
					print('found_value' + found)
					found_kwh.append(found)
				except:
					continue

	#find address using keywords
	for index, row in x.iterrows():
		if row[1].lower() == 'for' and x.at[index+1,'description'].lower() == 'service' and x.at[index+2,'description'] == 'at':
			address_found = x.at[index+3,'description'] +' '+ x.at[index+4,'description']+ ' ' + x.at[index+5,'description']
			print('address_found')


	#electricity charged for epcor
	for index, row in x.iterrows():
		if row[1].lower() == 'electric' and x.at[index+1,'description'].lower() == 'energy':
			electricty_charged = x.at[index+2,'description']
			print('elec_charge_found')
	for index, row in x.iterrows():
		if row[1].lower() == 'ab':
			city = x.at[index-2,'description'] +' '+ x.at[index-1,'description']


	return found_kwh, address_found, electricty_charged, city

def detect_electrical_bill(company, x):
	y = None
	if company == 'epcor':
		y = detect_epcor(x)
	if company == 'atco':
		y = detect_atco(x)

	return y
