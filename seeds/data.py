import csv
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder

absolute_path = os.path.dirname(os.path.abspath(__file__))


class SedgewickSeeder(Seeder):
	def run(self):
		with open(absolute_path+'/sedgewick_tax.csv','r') as csv_file:
			city = 'sedgewick'
			csv_reader = csv.DictReader(csv_file)
			for line in csv_reader:
				building_feet = float(put_to_zero(line['BLDG_FEET']))
				building_description = line['BLDG_DESC']
				first_story_sf = 0
				second_story_sf = 0
				third_story_sf = 0
				basement_sf = 0


					# Creating Square Footage Distrubution based upon home type
				if building_description == "1 1/2 Storey & Basement":
					first_story_sf = building_feet*(2/3)
					second_story_sf = building_feet*(1/3)
					third_story_sf = 0
					basement_sf = building_feet*(2/3)


				elif building_description == "1 1/2 Sty. Slab on Grade":
					first_story_sf = building_feet*(2/3)
					second_story_sf = building_feet*(1/3)
					third_story_sf = 0
					basement_sf = 0


				elif building_description == "1 3/4 Storey & Basement":
					first_story_sf = building_feet*(4/7)
					second_story_sf = building_feet*(3/7)
					third_story_sf = building_feet*0
					basement_sf = building_feet*(2/3)



				elif building_description == "1 3/4 Storey Basementless":
					first_story_sf = building_feet*(4/7)
					second_story_sf = building_feet*(3/7)
					third_story_sf = building_feet*0
					basement_sf = 0


				elif building_description == "1 3/4 Sty. Slab on Grade":
					first_story_sf = building_feet*(4/7)
					second_story_sf = building_feet*(3/7)
					third_story_sf = building_feet*0
					basement_sf = 0




				elif building_description == "1 Storey & Basement":
					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = building_feet



				elif building_description == "1 Storey & Bonus Upper":
					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = building_feet


				elif building_description == "1 Storey Basementless":

					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = 0






				elif building_description == "1 Storey Slab on Grade":

					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = 0


				elif building_description == "1 Storey Upper":
					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = building_feet



				elif building_description == "2 Storey & Basement":

					first_story_sf = building_feet*(1/2)
					second_story_sf = building_feet*(1/2)
					third_story_sf = 0
					basement_sf = building_feet*(1/2)





				elif building_description == "2 Storey Basementless":

					first_story_sf = building_feet*(1/2)
					second_story_sf = building_feet*(1/2)
					third_story_sf = 0
					basement_sf = 0





				elif building_description == "2 Storey Slab on Grade":

					first_story_sf = building_feet*(1/2)
					second_story_sf = building_feet*(1/2)
					third_story_sf = 0
					basement_sf = 0


				elif building_description == "3 Storey & Basement":

					first_story_sf = building_feet*(1/3)
					second_story_sf = building_feet*(1/3)
					third_story_sf = building_feet*(1/3)
					basement_sf = building_feet*(1/3)


				elif building_description == "3 Storey Basementless":

					first_story_sf = building_feet*(1/3)
					second_story_sf = building_feet*(1/3)
					third_story_sf = building_feet*(1/3)
					basement_sf = 0


				elif building_description == "Split Entry":
					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = building_feet

				elif building_description == "Split Entry & Bonus Upper":
					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = building_feet


				elif building_description == "Split Level":
					first_story_sf = building_feet*(2/3)
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = building_feet

				elif building_description == "Split Level & Crawl Space":
					first_story_sf = building_feet
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = 0
				else:
					first_story_sf = 0
					second_story_sf = 0
					third_story_sf = 0
					basement_sf = 0

				customer = Customer(
					tax_year = 0,
					address= line['ADDRESS'],
					year_built = int(put_to_zero(line['YEAR_BUILT'])),
					building_description = line['BLDG_DESC'],
					building_meter = 0,
					building_feet = float(put_to_zero(line['BLDG_FEET'])),
					garage = None,
					fireplace = None,
					basement = None,
					assessment = 0,
					latitude = float(put_to_zero(line['LATITUDE'])),
					longitude = float(put_to_zero(line['LONGITUDE'])),
					secret_code = secret_code_generator(4,2),
					first_story_sf = first_story_sf,
					second_story_sf = second_story_sf,
					third_story_sf = third_story_sf,
					basement_sf = basement_sf,
					city = city
				)
				try:
					db.session.add(customer)
					db.session.commit()
				except:
					db.session.rollback()


		try:
			city = City(city = city)
			db.session.add(city)
			db.session.commit()
		except:
			db.session.rollback()



