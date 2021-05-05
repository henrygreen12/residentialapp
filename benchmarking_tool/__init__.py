import os
from flask_seeder import FlaskSeeder
from .app import create_app
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_migrate import Migrate
from .accounts.views import accounts
from .main.views import main 
from dotenv import load_dotenv
from .admin import *
from .models import base
from flask_wtf.csrf import CSRFProtect
# from flask_login_multi.login_manager import LoginManager

#flask mobility not wokring
from flask_mobility import Mobility


load_dotenv() 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'accounts.login'
login_manager.login_message_category = 'info'
mail = Mail(app)
mail.init_app(app)
admin.init_app(app)
migrate = Migrate(app, db)
seeder = FlaskSeeder()
seeder.init_app(app, db)
CSRFProtect(app)


app=create_app()


mobile = Mobility(app)





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
