from .base import db


class TMY_Edmonton(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(200), unique=False)
    hour = db.Column(db.String(200), unique=False)
    dry_bulb_temperature = db.Column(db.Float, unique=False)
    dew_point_temperature = db.Column(db.Float, unique=False)
    relative_humidity = db.Column(db.Float, unique=False)
    atomic_pressure = db.Column(db.Float, unique=False)
    horizontial_radiation = db.Column(db.Float, unique=False)
    ex_direct_normal_radiation = db.Column(db.Float, unique=False)
    infrared_radiation_from_sky = db.Column(db.Float, unique=False)
    global_horizontal_radiation = db.Column(db.Float, unique=False)
    direct_normal_radiation = db.Column(db.Float, unique=False)
    diffuse_hortizontal_radiation = db.Column(db.Float, unique=False)
    global_horizontal_illuminance = db.Column(db.Float, unique=False)
    direct_normal_illuminance = db.Column(db.Float, unique=False)
    direct_horizontal_illuminance = db.Column(db.Float, unique=False)
    zenith_luminance = db.Column(db.Float, unique=False)
    wind_direction = db.Column(db.Float, unique=False)
    wind_speed = db.Column(db.Float, unique=False)
    total_sky_cover = db.Column(db.Float, unique=False)
    opaque_sky_cover = db.Column(db.Float, unique=False)
    ceiling_height = db.Column(db.Float, unique=False)
    present_weather_code =db.Column(db.String(200), unique=False)

