import csv
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder


absolute_path = os.path.dirname(os.path.abspath(__file__))


class Appliance_Companies(Seeder):
    def run(self):
        with open(absolute_path+'/appliance_companies.csv','r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for line in csv_reader:
                appliance_company = ApplianceCompanies(
                    company_name = line['Appliance Brand']

                )
                db.session.add(appliance_company)
                db.session.commit()
