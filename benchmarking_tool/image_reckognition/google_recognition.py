
import os, io
from google.cloud import vision
import pandas as pd
import numpy as np
from sqlalchemy.orm import load_only
from .models import *
from .methods import *


root_path = os.path.dirname(os.path.abspath(__file__))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = root_path+"/ServiceAccountToken.json" #API


client = vision.ImageAnnotatorClient()


def detectText(img): #google recognition function
	with io.open(img, 'rb') as image_file:
		content = image_file.read()

	image = vision.types.Image(content=content)
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


def detect_address(picture_path,folder):
	image = os.path.join(root_path,os.environ['STATIC_PATH'],folder,picture_path,)
	temp_folder = create_temp_folder(image)
	all_jpg = get_all_jpg(temp_folder)
	for i in all_jpg:
		rex = detectText(i) #apply the image recognition application

		A = np.array(rex) #converting the image recognition OUTPUT into a numpy array
		CardA = A.shape
		
		nA_rows, nA_cols = CardA
		address_entities = Customer.query.with_entities(Customer.address).all()
		addresses = list(map(lambda x : x.address, address_entities))
		

		for i in range(0, nA_rows): #loop to identify create the structure of the address
			houseN = A[i:i+1:1,1]
			StreetNm = A[i+1:i+2:1,1]
			StreetType = A[i+2:i+3:1,1]
			City = A[i+3:i+4:1,1]
			CityType = A[i+4:i+5:1,1]
			Province = A[i+5:i+6:1,1]
			Address = (houseN + " " + StreetNm + " " + StreetType + " " + City + " " + CityType + " " + Province)
			MiniAdd = (houseN + " " + StreetNm + " " + StreetType)
			print('miniaddress:' + MiniAdd )
			if MiniAdd in addresses:	
				return Address
	return None
