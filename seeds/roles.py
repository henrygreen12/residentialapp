
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder

absolute_path = os.path.dirname(os.path.abspath(__file__))

class RoleSeeder(Seeder):
	def run(self):
		roles = ['Admin','Municipality','User','Contractor']

		for role in roles:
			try:
				dif_role = Role(name=role)
				db.session.add(dif_role)
				db.session.commit()

			except:
				db.session.rollback()
				print("Could not upload column:", dif_role)



