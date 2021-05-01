import json
import requests
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder

absolute_path = os.path.dirname(os.path.abspath(__file__))

class CompanySeeder(Seeder):
	def run(self):
		with open(absolute_path+'/contractor.json') as json_file:
			data = json.load(json_file)
			for line in data['data']:
				address = remove_new_line(line['address'])
				customer_base = line['customerBase']
				email_company = line['email']
				name = line['name']
				phone_number = line['phone']
				services_areas = line['serviceAreas']
				services_offered = line['servicesOffered']
				postal_code = remove_dash_or_double_space(line['address'])

				company = Company(
					name = name,
					email_company = email_company,
					address = address,
					phone_number = phone_number,
					code = secret_code_generator(4,2),
					customer_base = customer_base,
					services_areas = services_areas,
					postal_code = postal_code
				)

				if services_offered != None:
					for element in services_offered:
						service = Service.query.filter_by(name=element).first()
						if service == None:
							my_service = Service(
								name = element,
							)
							my_service.company = company
							db.session.add(my_service)
						else :
							company.services.append(service)
					db.session.add(company)
		db.session.commit()
