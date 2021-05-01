import csv
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder


absolute_path = os.path.dirname(os.path.abspath(__file__))


class Appliance_Upload(Seeder):
    def run(self):
        with open(absolute_path+'/appliance_list.csv','r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for line in csv_reader:
                appliance_static = ApplianceStatic(
                    appliance_name = line['Appliance Name'],
                    category= line['Category'],
                    power = line['Power']


                )
                db.session.add(appliance_static)
                db.session.commit()
