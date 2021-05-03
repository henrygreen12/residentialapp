# import os
# import secrets
# from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
# import random
# from dotenv import load_dotenv
# from flask_sqlalchemy import SQLAlchemy
# import math
# from models import *
# from models.role import Role
# from forms import *
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from flask_login import login_user, current_user, logout_user, login_required
# from flask_mail import Mail, Message
# from flask_admin import Admin, AdminIndexView
# from flask_admin.contrib.sqla import ModelView
# from flask_migrate import Migrate
# from models.equipment import Equipment
# from model_weather import *
# import datetime
# from sqlalchemy import Column, Integer, DateTime

# # from flask_security import Security,SQLAlchemyUserDatastore, current_user


# # -----------------------------------------------------------

# #     # role = Role(name='admin',description='admin')
# #     # db.session.add(role)
# #     # db.session.commit()

# bcrypt = Bcrypt(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'
# mail = Mail(app)
# mail.init_app(app)
# admin = Admin(app, name='admin')
# migrate = Migrate(app, db)

# # ------------------------------------------------


# class MyModelView(ModelView):
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.is_admin()

#     def inaccessible_callback(self, name, **kwargs):
#         return redirect(url_for('login'))


# class MyAdminIndexView(AdminIndexView):
#     def is_accessible(self):
#         return current_user.is_admin


# admin.add_view(MyModelView(User, db.session))
# admin.add_view(MyModelView(Customer, db.session))
# admin.add_view(MyModelView(DHW, db.session))
# admin.add_view(MyModelView(ElectricalEquipment, db.session))
# admin.add_view(MyModelView(ElectricalUsage, db.session))
# admin.add_view(MyModelView(GasUsage, db.session))
# admin.add_view(MyModelView(HeatingEquipment, db.session))
# admin.add_view(MyModelView(Occupancy, db.session))
# admin.add_view(MyModelView(WaterUsage, db.session))
# admin.add_view(MyModelView(Weather, db.session))
# admin.add_view(MyModelView(Survey, db.session))


# #################################################

# #to reload the user object from the user ID stored in the session.
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# def save_picture(form_picture,location):
# 	random_hex = secrets.token_hex(8)
# 	file_extension = os.path.splitext(form_picture.filename)[1]
# 	picture_filename = random_hex + file_extension
# 	picture_path = os.path.join(app.root_path,'static/'+location,picture_filename)
# 	form_picture.save(picture_path)
# 	return picture_filename


# #######################################
# # Routes
# #######################################

# # route for a user to register

# @app.route('/okotoks/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     if request.method == "POST":
#         email = request.form["email"]
#         first_name = request.form["first_name"]
#         last_name = request.form["last_name"]
#         password = request.form["password"]
#         confirm_password = request.form["confirm_password"]
#         secret_code = request.form["secret_code"]
#         gas_bill = request.files['gas_photo_bill']
#         electrical_bill = request.files['electrical_photo_bill']
#         form = RegistrationForm(
#             email=email,
#             first_name=first_name,
#             last_name=last_name,
#             password=password,
#             confirm_password=confirm_password,
#             secret_code=secret_code,
#             gas_bill = gas_bill,
#             electrical_bill = electrical_bill
#         )
#         if form.validate_on_submit():
#             customer = Customer.query.filter_by(
#                 secret_code=secret_code).first()
#             role = Role.query.filter_by(name='User').first()
#             if (customer == None):
#                 flash('Please check your secret code', 'danger')
#             else:
#                 hashed_password = bcrypt.generate_password_hash(
#                     password).decode('utf-8')
#                 user = User(
#                     email=form.email.data,
#                     first_name=form.first_name.data,
#                     last_name=form.last_name.data,
#                     password=hashed_password,
#                     customer_id=customer.id,
#                     role_id=role.id)
#                 if gas_bill and electrical_bill:
#                     gas_picture = save_picture(gas_bill,"gas_folder")
#                     electrical_picture = save_picture(electrical_bill,"electrical_folder")
#                     gas_usage = GasUsage(
#                         gas_file = gas_picture,
#                         customer_id=customer.id
#                     )
#                     electrical_usage = ElectricalUsage(
#                         electrical_file = electrical_picture,
#                         customer_id=customer.id
#                     )
#                 else:
#                     gas_usage = GasUsage(
#                         customer_id=customer.id
#                     )
#                     electrical_usage = ElectricalUsage(
#                         customer_id=customer.id
#                     )
#                 db.session.add(user)
#                 db.session.add(gas_usage)
#                 db.session.add(electrical_usage)
#                 db.session.commit()
#                 return redirect(url_for('login'))
#     else:
#         form = RegistrationForm(
#             email="",
#             first_name="",
#             last_name="",
#             password="",
#             confirm_password="",
#             secret_code="",
#             gas_bill = "",
#             electrical_bill = ""
#         )
#     return render_template('register.html', title='Register', form=form, last_updated=dir_last_updated('static'))

# # Route for the user to login
# @app.route('/okotoks/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]
#         form = LoginForm(
#             email=email,
#             password=password
#         )
#         if form.validate_on_submit():
#             user = User.query.filter_by(email=email).first()
#             if user and bcrypt.check_password_hash(user.password, password):
#                 login_user(user)
#                 next_page = request.args.get('next')
#                 flash(f"Welcome {email}", 'success')
#                 return redirect(next_page) if next_page else redirect(url_for('home'))
#             else:
#                 flash(
#                     f"Login Unsuccessful,Please check your email and Password!", 'danger')
#                 return redirect(url_for('login'))
#     else:
#         form = LoginForm(email="")
#     return render_template('login.html', title='Login', form=form)

# # route for the user to logout
# @app.route('/okotoks/logout', methods=['GET', 'POST'])
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# # route for the user to request a new password
# @app.route('/okotoks/reset_password', methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     if request.method == 'POST':
#         email = request.form["email"]
#         form = RequestResetForm(email=email)
#         if form.validate_on_submit():
#             user = User.query.filter_by(email=email).first()
#             send_reset_email(user)
#             flash(
#                 'An email has been sent with instructions to reset your password', 'info')
#             return redirect(url_for('login'))
#     else:
#         form = RequestResetForm(email='')
#     return render_template('reset_request.html', title='Reset Password', form=form)

# # route for the user to reset his password
# @app.route('/okotoks/reset_password/<token>', methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     user = User.verify_reset_token(token)
#     if user is None:
#         flash('That is an invalid or expired token', 'warning')
#         return redirect(url_for('reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(
#             form.password.data).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()
#         flash(f"Thank You. Your Password has been updated.You can now log in", 'success')
#         return redirect(url_for('login'))
#     return render_template('reset_token.html', title='Reset Password', form=form)

# # route for updating the user account
# @app.route('/okotoks/update_user/', methods=['GET', 'POST'])
# @login_required
# def update_user():
#     if request.method == 'POST':
#         email = request.form["email"]
#         current_password = request.form['current_password']
#         new_password = request.form["new_password"]
#         confirm_password = request.form["confirm_password"]
#         form = UpdateAccountForm(email=email,current_password=current_password,
#                 new_password=new_password,confirm_password=confirm_password)
#         if form.validate_on_submit():
#             if bcrypt.check_password_hash(current_user.password, current_password):
#                 hashed_password = bcrypt.generate_password_hash(
#                     new_password).decode('utf-8')
#                 current_user.email = form.email.data
#                 current_user.password = hashed_password
#                 db.session.commit()
#                 flash(f"Thank You. Your Account has been updated.", 'success')
#                 return redirect(url_for('home'))
#     else:
#         form = UpdateAccountForm(email=current_user.email, current_password="",
#             new_password="",confirm_password="")
#     return render_template("user_update.html",title='Update Account', form=form,last_updated=dir_last_updated('static'))





# @app.route('/')
# @app.route('/okotoks/')
# @login_required
# def home():
#     building_info = Customer.query.get(current_user.customer_id)
#     current_weather = edmonton_weather.query.order_by(edmonton_weather.id.desc()).first()
#     current_temp = current_weather.temperature
#     furnace_output = (building_info.building_feet)*50*(2.5/4)
#     #current_regress = 1 - (current_temp + 45)/(22.5 +45)
#     #hour_output = furnace_output*current_regress*(1/0.8)



#     return render_template('home.html', title='home', current_temp = current_temp, furnace_output = furnace_output, last_updated=dir_last_updated('static'))


# @app.route('/okotoks/customer_info', methods=['GET', 'POST'])
# @login_required
# def customer_info():
#     if request.method == "POST":
#         phone_number = request.form["phone_number"]
#         #from new survey
#         occupantCount = request.form ["occupantCount"]
#         kidCount = request.form ["kidCount"]
#         maleCount = request.form ["maleCount"]
#         setPoint = request.form ["setPoint"]
#         thermostatNight = request.form ["thermostatNight"]
#         stoveEveryDay = request.form ["stoveEveryDay"]
#         stoveType = request.form["stoveType"]
#         atticAccess = request.form["atticAccess"]
#         dishwasher = request.form["dishwasher"]
#         windowFrost = request.form["windowFrost"]
#         coldAreas = request.form["coldAreas"]
#          #need to add list of cold areas from form into database
#         heatedGarage = request.form["heatedGarage"]
#         clothesDryerType = request.form["clothesDryerType"]
#         # need to add list of renovations from form into database
#         customer = Customer.query.get(current_user.customer_id)
#         customer.phone_number = phone_number
#         survey = customer.survey

#         if survey == None:
#             new_survey = Survey(
#                 occupantCount = occupantCount,
#                 kidCount=kidCount,
#                 maleCount = maleCount,
#                 setPoint = setPoint,
#                 thermostatNight = thermostatNight,
#                 stoveEveryDay = stoveEveryDay,
#                 stoveType = stoveType,
#                 atticAccess = atticAccess,
#                 dishwasher = dishwasher,
#                 windowFrost = windowFrost,
#                 coldAreas = coldAreas,
#                 heatedGarage = heatedGarage,
#                 clothesDryerType = clothesDryerType,
#                 customer_id=customer.id)
#             db.session.add(new_survey)
#         else:
#             survey.occupantCount=occupantCount
#             survey.kidCount=kidCount
#             survey.maleCount=maleCount
#             survey.setPoint=setPoint
#             survey.thermostatNight=thermostatNight
#             survey.stoveEveryDay=stoveEveryDay
#             survey.stoveType=stoveType
#             survey.atticAccess=atticAccess
#             survey.dishwasher=dishwasher
#             survey.coldAreas=coldAreas
#             survey.heatedGarage=heatedGarage
#             survey.clothesDryerType=clothesDryerType
#         db.session.commit()
#         return redirect(url_for('home'))
#     else:
#         return render_template('survey.html',title='Customer', last_updated=dir_last_updated('static'))



# @app.route('/okotoks/audit', methods=['GET', 'POST'])
# @login_required
# def audit():
#     if request.method == "POST":
#         heatingType = request.form ["heatingType"]
#         heatingAge = request.form["heatingAge"]
#         heatingCapacity = request.form["heatingCapacity"]
#         waterHeatingType = request.form["waterHeatingType"]
#         waterHeatingAge = request.form["waterHeatingAge"]
#         storageVolume = request.form ["storageVolume"]
#         inputCapacity = request.form["inputCapacity"]
#         fridgeCount = request.form["fridgeCount"]
#         freezerCount = request.form["freezerCount"]
#         microwaveCount = request.form["microwaveCount"]
#         blenderCount = request.form["blenderCount"]
#         coffeeMakerCount = request.form["coffeeMakerCount"]
#         computerCount = request.form["computerCount"]
#         dishwasherCount = request.form["dishwasherCount"]
#         washerCount = request.form["washerCount"]
#         dryerCount = request.form["dryerCount"]
#         garageOpenerCount = request.form["garageOpenerCount"]
#         kettleCount = request.form["kettleCount"]
#         ovenCount = request.form["ovenCount"]
#         toasterCount = request.form["toasterCount"]
#         toasterOvenCount = request.form["toasterOvenCount"]
#         sumpPumpCount = request.form["sumpPumpCount"]
#         vacuumCount = request.form["vacuumCount"]
#         customer = Customer.query.get(current_user.customer_id)
#         equipment = customer.equipment
#         if equipment == None:
#             new_audit = Equipment(heatingType = heatingType,
#             heatingAge = heatingAge,
#             heatingCapacity = heatingCapacity,
#             waterHeatingAge = waterHeatingAge,
#             waterHeatingType = waterHeatingType,
#             inputCapacity = inputCapacity, fridgeCount=fridgeCount, freezerCount=freezerCount, microwaveCount=microwaveCount, blenderCount=blenderCount, coffeeMakerCount=coffeeMakerCount,
#                               computerCount=computerCount, dishwasherCount=dishwasherCount, washerCount=washerCount, dryerCount=dryerCount,
#                               garageOpenerCount=garageOpenerCount, kettleCount=kettleCount, ovenCount=ovenCount, toasterCount=toasterCount,
#                               toasterOvenCount=toasterOvenCount, sumpPumpCount=sumpPumpCount, vacuumCount=vacuumCount, customer_id=customer.id)
#             db.session.add(new_audit)
#         else:
#             equipment.heatingCapacity = heatingCapacity
#             equipment.heatingType = heatingType
#             equipment.heatingAge = heatingAge
#             equipment.waterHeatingAge = waterHeatingAge
#             equipment.waterHeatingType = waterHeatingType
#             equipment.inputCapacity = inputCapacity
#             equipment.fridgeCount = fridgeCount
#             equipment.freezerCount = freezerCount
#             equipment.microwaveCount=microwaveCount
#             equipment.blenderCount=blenderCount
#             equipment.coffeeMakerCount=coffeeMakerCount
#             equipment.computerCount=computerCount
#             equipment.dishwasherCount=dishwasherCount
#             equipment.washerCount=washerCount
#             equipment.dryerCount=dryerCount
#             equipment.garageOpenerCount = garageOpenerCount
#             equipment.kettleCount = kettleCount
#             equipment.ovenCount = ovenCount
#             equipment.toasterCount = toasterCount
#             equipment.toasterOvenCount = toasterOvenCount
#             equipment.sumpPumpCount = sumpPumpCount
#             equipment.vacuumCount = vacuumCount
#         db.session.commit()
#         return redirect(url_for('home'))
#     else:
#         return render_template('diyAudit.html',title='Do-Yourself-Audit', last_updated=dir_last_updated('static'))


# # Function to check the secret code when registering
# @app.route('/check-code/', methods=['POST'])
# def check_code():
#     secret_code = request.form['secret_code']
#     customer = Customer.query.filter_by(secret_code=secret_code).first()
#     if (customer == None):
#         return {'success': False}
#     else:
#         return {'success': True}

# # function to send email
# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request', sender='server@pollen.one',
#                   recipients=[user.email])
#     msg.body = f''' To reset your password, visit the following link :

# {url_for('reset_token',token=token,_external=True)}

#     If you didn't make the request, please ignore this email
#     '''
#     mail.send(msg)

# #function to get the latitude and the longitude from the database

# @app.route('/okotoks/street_map/',methods=['GET', 'POST'])
# @login_required
# def get_longitude_and_latitude():
#     customer = Customer.query.get(current_user.customer_id)
#     return render_template('street_map_customer.html',title='Street Map',customer=customer, last_updated=dir_last_updated('static'))


# @app.route('/okotoks/hotwater/',methods=['GET', 'POST'])
# @login_required
# def hotwater():
#     building_info = Customer.query.get(current_user.customer_id)
#     current_weather = edmonton_weather.query.order_by(edmonton_weather.id.desc()).first()
#     current_temp = current_weather.temperature
#     furnace_output = (building_info.building_feet)*50*(2.5/4)
#     output = 30
#     rvalue = 12
#     heighttank = 5
#     rvalue = 12
#     heightank = 5
#     gravity = 32.174*3600*3600
#     mixed_water_temp  = 40.6
#     mixed_water_temp_fahrenheit = (mixed_water_temp*(9/5))+32
#     ambient_temperature = 22.5
#     ambient_temperature_fahrenheit = (ambient_temperature*(9/5))+32
#     tankvolume = 35
#     air_density = (9.7794*(10**(-16))*(ambient_temperature**6)-0.00000000000104438738*(ambient_temperature**5) + 0.00000000040582770153*(ambient_temperature**4)-0.00000007793160224894*(ambient_temperature**3)+0.0000139445206721191*(ambient_temperature**2)-0.00425395065332666*ambient_temperature+1.28252222279131)*0.0623
#     air_dynamic_viscosity = ((4.2335*(10**-16)*ambient_temperature**6-0.00000000000019274775*ambient_temperature**5-0.00000000007340906814*ambient_temperature**4+0.00000006985378704768*ambient_temperature**3-0.0000415678183959202*ambient_temperature**2+0.0495879959302156*ambient_temperature+17.2300706085878)*10**(-6))*2411.9686
#     air_thermal_conductivity  =(6.63*(10**(-18))*ambient_temperature**6 - (4.65037*(10**-15))*ambient_temperature**5 + 0.00000000000037999011*ambient_temperature **4 + 0.00000000026304081567*ambient_temperature**3 - 0.00000005374945618218*ambient_temperature**2 + 0.0000744509174472757*ambient_temperature  + 0.024225420692397)*0.58
#     air_specific_heat  = ((9.227*(10**(-17))*ambient_temperature**6-0.0000000000000788933*ambient_temperature**5+0.00000000001871938721*ambient_temperature**4-0.00000000051361083903*ambient_temperature**3+0.00000024455950031143*ambient_temperature**2+0.0000182814596129314*ambient_temperature+1.00502296478241)*1000)*0.000238846
#     air_diffusion_rate = air_thermal_conductivity/(air_density*air_specific_heat)
#     air_prandtl_number = (air_specific_heat*air_dynamic_viscosity)/air_thermal_conductivity
#     outer_tank_diamter =  2*math.sqrt(tankvolume/(3.14159265359*heighttank*7.48052))
#     outer_tank_radius = outer_tank_diamter/2
#     inner_tank_radius = outer_tank_radius-(1/24)
#     k_tank = (1/24)/rvalue
#     flue_inside = 0.15*outer_tank_diamter
#     flue_thickness = 0.08/12
#     flue_outside = flue_inside + flue_thickness
#     surface_temperature_sides = 75.5

#     ra_sides = (gravity*(1/ambient_temperature_fahrenheit)*(surface_temperature_sides-ambient_temperature_fahrenheit)*(heighttank**3))/(air_diffusion_rate*air_dynamic_viscosity)
#     nu_sides = (0.825+((0.387 * ra_sides**(1/6) / ((1+((0.492/air_prandtl_number)**(9/16)))**(8/27)))))**2
#     h_sides =(air_thermal_conductivity*nu_sides)/(heighttank)
#     surface_temperature_top = 75.5

#     ra_top =(gravity*(1/ambient_temperature_fahrenheit)*(surface_temperature_top-ambient_temperature_fahrenheit)*((0.25*3.14159265359*(outer_tank_diamter**2))/((3.14159265359*outer_tank_diamter)))**3)/(air_diffusion_rate*air_dynamic_viscosity)
#     nu_top = 0.54*(ra_top**(1/4))
#     h_top = (air_thermal_conductivity*nu_top)/((0.25*3.14159265359*(outer_tank_diamter**2))/(3.14159265359*outer_tank_diamter))
#     return render_template('hotwater.html',title='Hot Water',output = output, current_temp = current_temp, rvalue=rvalue,
#         heighttank = heighttank, gravity=gravity,mixed_water_temp=mixed_water_temp,mixed_water_temp_fahrenheit=mixed_water_temp_fahrenheit,
#         ambient_temperature_fahrenheit = ambient_temperature_fahrenheit,tankvolume=tankvolume,
#         air_density=air_density,air_dynamic_viscosity=air_dynamic_viscosity,
#         air_thermal_conductivity=air_thermal_conductivity,air_specific_heat=air_specific_heat,air_diffusion_rate=air_diffusion_rate,
#         air_prandtl_number=air_prandtl_number,outer_tank_diamter = outer_tank_diamter,
#         outer_tank_radius=outer_tank_radius,inner_tank_radius=inner_tank_radius,
#         k_tank=k_tank, flue_inside=flue_inside,flue_thickness=flue_thickness, flue_outside=flue_outside,surface_temperature_sides = surface_temperature_sides,
#         ra_sides=ra_sides,nu_sides=nu_sides,h_sides=h_sides,surface_temperature_top=surface_temperature_top,
#         ra_top = ra_top, nu_top=nu_top, h_top=h_top, heightank = heightank, last_updated=dir_last_updated('static'))




# # --------------------------------------------------
# if __name__ == "__main__":
#     app.debug = True
#     app.run()




