import csv
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder
import datetime


absolute_path = os.path.dirname(os.path.abspath(__file__))


class AAAAElectricalRates(Seeder):
    def run(self):
        _current_date = datetime.datetime.now() # IMPORTANT: should keep date info on data set instead of on this script
        cities = ['edmonton', 'calgary', 'camrose', 'sedgewick'] # if expading database to more cities, add city here and have data with the correct name
        for _city in cities:
            file_name = absolute_path + f"/electrical_rates_{_city}.csv"  # assumes naming for source file
            try:
                with open(file_name, 'r') as f:
                    csv_reader = csv.DictReader(f)
                    if (_city == "sedgewick"): # sedgewick has different data format
                        for line in csv_reader:
                            electrical_rates = ElectricalRates(
                                retailer = line['Retailer'],
                                plan_details= line['Plan Details'],
                                pricing = line['Pricing'],
                                contract_length = line['Contract Length'],
                                early_exit_fee = float(line['Early Exit Fee']),
                                retail_admin_fee = float(line['Retail Admin Fee']),
                                retailer_charge = float(line['Retailer Charge']),
                                variable_distribution = float(line['Variable Distribution']),
                                fixed_distribution = float(line['Fixed Distribution']),
                                varible_transmission = float(line['Variable Transmission']),
                                per_kwh_rate_rider = float(line['Per KwH rate Rider']),
                                balancing_pool_rate_rider = float(line['Balancing Pool Rider']),
                                transmission_rate_rider = float(line['Transmission Rate Rider']),
                                local_access_fee = float(line['Local Access Fee']),

                                city = _city,
                                month = _current_date.month,
                                year = _current_date.year,
                                total_rate = None
                            )

                            db.session.add(electrical_rates)
                            db.session.commit()  # potential performance issue with commiting every row. try batch commits (moves overhead to memory i guess)

                    else: # assuming all future data will have the same format.
                        for line in csv_reader:
                            electrical_rates = ElectricalRates(
                                retailer = line['company'],
                                plan_details= line['plan_details1'],
                                pricing = line['plan_details2'],
                                contract_length = line['contract_details1'],
                                early_exit_fee = float(0) if line['contract_details2'] == "Early Exit Fee: No" else float(1), # 1 is placeholder - need more definite data
                                retail_admin_fee = float(-1), # data missing
                                retailer_charge = float(line['rates']),
                                variable_distribution = 0, # data missing
                                fixed_distribution = 0, # data missing
                                varible_transmission = 0, # data missing
                                per_kwh_rate_rider = 0, # data missing
                                balancing_pool_rate_rider = 0, # data missing
                                transmission_rate_rider = 0, # data missing
                                local_access_fee = 0, # data missing

                                city = _city,
                                month = _current_date.month,
                                year = _current_date.year,
                                total_rate = float(line['total_rate'])
                            )

                            db.session.add(electrical_rates)
                            db.session.commit()  # potential performance issue with commiting every row. try batch commits (moves overhead to memory i guess)

                print(f"{_city.capitalize()} done.")

            except IOError:
                print ("Could not read file:", file_name)
