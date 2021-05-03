from flask_sqlalchemy import SQLAlchemy
import json
import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import os
from app import app
from models import *
from python_scripts import *
import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from .base import *
from .customer import *

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)
    db.init_app(app)
    return app


#from flask_app import db
app = create_app()
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
db = SQLAlchemy()




