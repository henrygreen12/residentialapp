from flask_sqlalchemy import SQLAlchemy
import json
import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import os
from benchmarking_tool.models import *
from python_scripts import *
import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from python_scripts import *
from benchmarking_tool.app import create_app
load_dotenv()

app = create_app()
db.app = app
db.init_app(app)

def weather_pull():
    with db.app.app_context():
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=edmonton&appid=b543e04dda3e7a9ada2c9f3cd28e6db6')
        r = r.json()
        temperature = float(r["main"]["temp"])-273.15
        current_condition = r['weather'][0]['main']
        description = r['weather'][0]['description']
        pressure = r['main']['pressure']
        humidity = r['main']['humidity']
        wind_speed = r['wind']['speed']
        wind_deg = r['wind']['deg']
        clouds = r['clouds']['all']
        sunrise = r['sys']['sunrise']
        sunset = r['sys']['sunset']
        weather = EdmontonWeather(current_condition=current_condition,description=description,temperature=temperature,pressure=pressure,humidity=humidity,wind_speed=wind_speed,wind_deg=wind_deg,clouds=clouds,sunrise=sunrise,sunset=sunset)
        db.session.add(weather)
        db.session.commit()


sched_method1 = BlockingScheduler(daemon=True)
sched_method1.add_job(weather_pull,'interval',seconds=10)
sched_method1.start()
