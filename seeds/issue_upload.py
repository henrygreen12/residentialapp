import csv
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder


absolute_path = os.path.dirname(os.path.abspath(__file__))


class Issue_Upload(Seeder):
    def run(self):
        with open(absolute_path+'/efficiency.csv','r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for line in csv_reader:
                issue_static = IssueStatic(
                    address = line['address'],
                    issue_detection_1 = line['Efficiency Issue Detection1'],
                    issue_detection_2 = line['Efficiency Issue Detection2'],
                    issue_detection_3 = line['Efficiency Issue Detection3'],
                    issue_detection_4 = line['Efficiency Issue Detection4']


                )
                db.session.add(issue_static)
                db.session.commit()
