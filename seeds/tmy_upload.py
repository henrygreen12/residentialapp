import csv
from benchmarking_tool.models import *
from python_scripts import *
from flask_seeder import Seeder


absolute_path = os.path.dirname(os.path.abspath(__file__)) 


class TMY_UploadSeeder(Seeder):
    def run(self):
        with open(absolute_path+'/edmonton_city_center_cwec.csv','r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for line in csv_reader:
                tmy_edmonton = TMY_Edmonton(
                    date = line['Date'],
                    hour= line['HH:MM'],
                    dry_bulb_temperature = float((line['Dry Bulb Temperature {C}'])),
                    dew_point_temperature = float((line['Dew Point Temperature {C}'])),
                    relative_humidity = float((line['Relative Humidity {%}'])),
                    atomic_pressure = float((line['Atmospheric Pressure {Pa}'])),
                    horizontial_radiation = float((line['Extraterrestrial Horizontal Radiation {Wh/m2}'])),
                    ex_direct_normal_radiation = float((line['Extraterrestrial Direct Normal Radiation {Wh/m2}'])),
                    infrared_radiation_from_sky = float((line['Horizontal Infrared Radiation Intensity from Sky {Wh/m2}'])),
                    global_horizontal_radiation = float((line['Global Horizontal Radiation {Wh/m2}'])),
                    direct_normal_radiation = float((line['Direct Normal Radiation {Wh/m2}'])),
                    diffuse_hortizontal_radiation = float((line['Diffuse Horizontal Radiation {Wh/m2}'])),
                    global_horizontal_illuminance = float((line['Global Horizontal Illuminance {lux}'])),
                    direct_normal_illuminance = float((line['Direct Normal Illuminance {lux}'])),
                    direct_horizontal_illuminance = float((line['Diffuse Horizontal Illuminance {lux}'])),
                    zenith_luminance = float((line['Zenith Luminance {Cd/m2}'])),
                    wind_direction = float((line['Wind Direction {deg}'])),
                    wind_speed = float((line['Wind Speed {m/s}'])),
                    total_sky_cover = float((line['Total Sky Cover {.1}'])),
                    opaque_sky_cover = float((line['Opaque Sky Cover {.1}'])),
                    ceiling_height = float((line['Ceiling Height {m}'])),
                    present_weather_code = ((line['Present Weather Codes'])),
                )
                db.session.add(tmy_edmonton)
                db.session.commit()
