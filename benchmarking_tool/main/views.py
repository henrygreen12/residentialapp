import math
from sqlalchemy import desc
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user, current_user, logout_user, login_required
from ..models import *
from pathlib import Path
import requests
from benchmarking_tool.helper import *
from benchmarking_tool.forms import *
from benchmarking_tool.decorators import *
from benchmarking_tool.functions import *
import secrets
from PIL import Image
from difflib import get_close_matches
from benchmarking_tool.furnace_detect import *
from benchmarking_tool.pvc_steel_detect import *
from benchmarking_tool.image_reckognition.aws_rek import *
from benchmarking_tool.image_reckognition.bill_detection import *
from benchmarking_tool.methods import *
from datetime import datetime,timedelta
from sqlalchemy.sql.expression import func
from flask_mobility.decorators import mobile_template, mobilized
from flask import session
import csv
import operator
import boto3
import sys
import os
import pandas as pd
from flask_mail import Mail, Message
from .admin import *


main = Blueprint('main',__name__,template_folder='templates')
app_root = Path(__file__).parents[1]
root_path = os.path.dirname(os.path.abspath(__file__))

@main.route('/test', methods=['GET','POST'])
@login_required
def testmodelnumber():
        return render_template('compare-my-home.html')

@main.route('/')
@main.route('/overview/',methods=['GET', 'POST'])
@login_required
@type_required
@survey_required
def overview():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    issues = db.session.query(IssueStatic).filter(IssueStatic.address==customer.address).all()
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).limit(4).all()
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    heating_equipment = HeatingEquipment.query.filter_by(customer_id=current_user.id)
    current_weather = EdmontonWeather.query.order_by(EdmontonWeather.id.desc()).first()
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=edmonton&appid=b543e04dda3e7a9ada2c9f3cd28e6db6')
    r = r.json()
    current_temp= float((r["main"]["temp"])-273.15)
    current_condition = r['weather'][0]['main']
    temperature = int((r["main"]["temp"])-273.15)
    icon = r['weather'][0]['icon']
    heating_usage = 0
    current_regress = 0
    x = TMY_Edmonton.query.all()
    elec_bill = ElectricalUsage.query.filter_by(customer_id=customer.id).first()
    elec_consumption = elec_bill.consumption
    elec_cost=elec_bill.cost
    elec_rate=elec_cost/elec_consumption
    gas_rate=6.00
    home_upgrades = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    user_home = [60, 50]
    average_home = [75,62]
    try:
        efficiency = heating_equipment.efficiency*1
    except:
        efficiency = 0.85
        pass
    try:
        furnace_output = heating_equipment.btu_output/947817
    except:
        furnace_output =((building_info.building_feet)*50)/947817
    current_regress = 0
    light_usage = 2.16
    appliance_usage = 9.27
    ventilation_usage = 0.2
    dhw_usage = 27
    lighting_cost = "$" + str(50)
    appliance_cost = "$" + str(50)
    ventilation_cost = "$" + str(50)
    hot_water_cost = "$" + str(50)
    heating_cost = "$" + str(50)
    for row in x:
        current_regress = 1 - (row.dry_bulb_temperature + 45)/(21 +45)
        if current_regress < 0:
            current_regress = 0
        heating_usage = heating_usage+(furnace_output*current_regress*(1/efficiency))

    #added for mobile development 
   # mobile = True
    #if mobile == True:
     #   return redirect(url_for('main.m_utility_costs'))
    print('getting to the overview')

    return render_template('overview.html',title='Overview',customer=customer,appliances=appliances,issues=issues,
        light_usage=light_usage,dhw_usage=dhw_usage, heating_usage = heating_usage,
        ventilation_usage = ventilation_usage,appliance_usage = appliance_usage,
        last_updated=dir_last_updated(), lighting_cost = lighting_cost, appliance_cost = appliance_cost, ventilation_cost = ventilation_cost,
        hot_water_cost = hot_water_cost, heating_cost = heating_cost,home_upgrades = home_upgrades, user_home = user_home, average_home = average_home)


@main.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    if form.validate_on_submit():
        msg = Messages(customer_id=customer.id,
                      body =form.message.data, recipient = 'Admin')
        db.session.add(msg)
        db.session.commit()
        flash(('Your message has been sent.'))
        return redirect(url_for('main.overview'))
    return render_template('send_message.html', form=form)

@main.route('/messages')
@login_required
def messages():
    user = User.query.filter_by(id = current_user.id).first()
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    messages = Messages.query.filter_by(customer_id=customer.id, recipient = "Customer")
    return render_template('messages.html', messages=messages, user = user)

@main.route('/customer_info', methods=['GET', 'POST'])
@login_required
def customer_info():
    if request.method == "POST":
        #from new survey
        setPoint = request.form ["setPoint"]
        thermostatNight = request.form ["thermostatNight"]
        # stoveType = request.form["stoveType"]
        heatedGarage = request.form["heatedGarage"]
        # clothesDryerType = request.form["clothesDryerType"]
        # waterHeaterType = request.form["waterHeaterType"]
        # furnaceType = request.form["furnaceType"]
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        survey = customer.survey
        if survey == None:
            new_survey = Survey(
                setPoint = setPoint,
                thermostatNight = thermostatNight,
                # stoveType = stoveType,
                heatedGarage = heatedGarage,
                # clothesDryerType = clothesDryerType,
                # waterHeaterType = waterHeaterType,
                # furnaceType = furnaceType,
                customer_id=customer.id)
            db.session.add(new_survey)
        else:
            survey.setPoint=setPoint
            survey.thermostatNight=thermostatNight
            # survey.stoveType=stoveType
            survey.heatedGarage=heatedGarage
            # survey.clothesDryerType=clothesDryerType
            # survey.waterHeaterType=waterHeaterType
            # survey.furnaceType=furnaceType
        db.session.commit()
        return redirect(url_for('main.overview'))
    else:
        return render_template('survey.html',title='Customer', last_updated=dir_last_updated())


# @main.route('/customer_info', methods=['GET', 'POST'])
# @login_required
# @mobilized(customer_info)
# def customer_info():
#     print('in customer_info')
#     # forms = MyCustomForm() # and then put it into the html --> <!-- {{ form.csrf_token }} -->
#     if request.method == "POST": # if submit button on survey is pressed
#         # receive data here
#         # occupants
#         occupants_a = request.form["occupants_a"]
#         occupants_b = request.form["occupants_b"]
#         occupants_c = request.form["occupants_c"]
#         occupants_d = request.form["occupants_d"]
#         # thermostat

#         # smart thermostat?
#         # cold areas
#         # cold_areas = {
#         #     "livingroom" : request.form["livingroom"],
#         #     "bedroom" : request.form["bedroom"],
#         #     "washroom": request.form["washroom"],
#         #     "Kitchen" : request.form["kitchen"]
#         # }
#         #lvrm1 = request.form["livingroom"]
#         #print(string(request.form["livingroom"]))
#         # A/C

#         # heated garage
#         # DHW
#         # heating
        
#         return redirect(url_for('main.overview'))
#     else: # if need to do survey
#         return render_template("mobile/survey.html")
# #

@main.route('/utility/',methods=['GET', 'POST'])
@login_required
@survey_required
def utility():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    customer_electrical_rate = db.session.query(ElectricalRates).filter(ElectricalRates.customer_id == customer.id).all()
    electrical_rates = ElectricalRates.query.all()

    return render_template('utility.html',title='Utility',customer=customer, last_updated=dir_last_updated())


@main.route('/utilitybills/',methods=['GET', 'POST'])
@login_required
@survey_required
def utility_bills():
    customer = Customer.query.filter_by(user_id=current_user.id).first()

     #db.session.query(ElectricalUsage).filter(ElectricalUsage.customer_id ==
    #current_user.id).order_by(ElectricalUsage.id.desc()).first()
    electrical_rates = ElectricalRates.query.filter(ElectricalRates.total_rate.isnot(None)).all()
    target = os.path.join(app_root, 'static/electrical_folder')
    form = electricPhotoForm(electric_photo='')
    electric_bills = ElectricalUsage.query.order_by(ElectricalUsage.created_date).filter(ElectricalUsage.customer_id == customer.id).first()
    cost = electric_bills.cost
    bill_identified = False
    wrong_page = False



    if not os.path.isdir(target):
        os.makedirs(target)
    if request.method == "POST" and "electrical_photo" in  request.files:
        #savings the photo
        electrical_photo = request.files.get('electrical_photo', None)
        print(electrical_photo)
        file_name = save_picture(electrical_photo,"electrical_folder")

        #first detect text on the bill itself
        target = os.path.join(app_root, 'static/electrical_folder')
        destination = '/'.join([target, file_name])
        electrical_bill_reckognize = detectText(destination)
        #now find a company to apply the proper method
        electrical_company = detect_company(electrical_bill_reckognize)
        #now that company is found, apply method to return values for detecting bill
        #check if detection returns error, if so rename variable to specifify error found
        if electrical_company == 'error':
            flash('Your bill was not recognized, please take another photo', 'danger')
        #if no error, proceed

        else:
        #find city via method in bill detection
            full_detection = detect_electrical_bill(electrical_company,electrical_bill_reckognize)
            electrical_usage = ElectricalUsage(consumption = float(full_detection[0][0]), cost = float(full_detection[2]),
                electrical_file = file_name,customer_id=customer.id)
            db.session.add(electrical_usage)
            db.session.commit()





            found_kwh = float(full_detection[0][0])
            address_found = full_detection[1]
            electricity_charged = float(full_detection[2]) + 0.05*(float(full_detection[2]))
            customer_electrical_rate = float(electricity_charged)/float(found_kwh)
            bill_identified = True
            electric_bills = ElectricalUsage.query.order_by(-ElectricalUsage.id).filter(ElectricalUsage.customer_id == customer.id).limit(5).all()
            print(customer_electrical_rate)
            return render_template('utility_bills.html',title='Utility Bills',form=form,customer=customer,
            bill_provider = electrical_company,
            found_kwh = found_kwh,
            address_found = address_found,
            electricity_charged=electricity_charged,
            wrong_page=wrong_page,
            bill_identified= bill_identified,
            electric_bills=electric_bills,cost = cost,
        customer_electrical_rate=customer_electrical_rate, electrical_rates=electrical_rates,last_updated=dir_last_updated())

    return render_template('utility_bills.html',title='Utility Bills',form=form,customer=customer,
        wrong_page=wrong_page,
        electric_bills=electric_bills,
        bill_identified= bill_identified,cost = cost,
         electrical_rates=electrical_rates,last_updated=dir_last_updated())



@main.route('/appliances', methods = ['GET','POST'])
@login_required
@survey_required
def appliances():
    appliance_found_bool = False
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).all()
    appliance_categories_query =db.session.query(Appliance.category_appliance.distinct().label("appliance_categories"))
    appliance_categories = [row.appliance_categories for row in appliance_categories_query.all()]
    kitchen_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'kitchen',Appliance.customer_id == customer.id).all()
    basement_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'basement',Appliance.customer_id == customer.id).all()
    entertainment_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'entertainment',Appliance.customer_id == customer.id).all()
    misc_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'misc',Appliance.customer_id == customer.id).all()
    model_detect =os.path.join(app_root, 'furnace_not_furnace.model')
    model_eff = os.path.join(app_root, 'pvc_steel.model')
    target = os.path.join(app_root, 'static/appliance_photos/img')
    form = appliancePhotoForm(appliance_photo='')
    furnace=HeatingEquipment.query.filter(HeatingEquipment.customer_id == customer.id).limit(5).all()

    heating_usage = 0
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    x = TMY_Edmonton.query.all()
    # elec_bill = ElectricalUsage.query.filter_by(customer_id=customer.id).first()
    # elec_consumption = elec_bill.consumption
    # elec_cost=elec_bill.cost
    # elec_rate=elec_cost/elec_consumption
    # gas_rate=6.00
    try:
        efficiency = furnace.efficiency*1
    except:
        efficiency = 0.85
        pass
    try:
        furnace_output = furnace.btu_output/947817
    except:
        furnace_output =((building_info.building_feet)*50)/947817
    for row in x:
        current_regress = 1 - (row.dry_bulb_temperature + 45)/(21 +45)
        if current_regress < 0:
            current_regress = 0
        heating_usage = heating_usage+(furnace_output*current_regress*(1/efficiency))




    if not os.path.isdir(target):
        os.makedirs(target)

    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('appliances.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
            appliances=appliances,
            basement_appliances=basement_appliances, appliance_found = appliance_found,entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, heating_usage = heating_usage,filename=file_name , furnace=furnace)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('appliances.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, appliances=appliances,appliance_duplicates=appliance_duplicates,
            basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, filename=file_name)


    if request.method == 'POST' and 'furnace_photo' in request.files:
        furnace_photo = request.files.get('furnace_photo',None)
        target = os.path.join(app_root, 'static/furnace_folder')
        form = FurnaceForm(furnace_photo=furnace_photo)
        if form.validate_on_submit():
            picture_furnace_filename = save_picture(furnace_photo,'furnace_folder')
            destination ='/'.join([target,picture_furnace_filename])
            furnace = HeatingEquipment(
                furnace_file = picture_furnace_filename,
                customer_id = customer.id
            )
            db.session.add(furnace)
            db.session.commit()
            return redirect(url_for('main.appliances'))
        else:
            form = FurnaceForm(furnace_photo='')
        return render_template('appliances.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)

    if request.method == 'POST' and 'dhw_photo' in request.files:
        dhw_photo = request.files.get('dhw_photo',None)
        target = os.path.join(app_root, 'static/dhw_folder')
        form = DhWForm(dhw_photo=dhw_photo)
        if form.validate_on_submit():
            picture_dhw_filename = save_picture(dhw_photo,'dhw_folder')
            destination ='/'.join([target,picture_dhw_filename])
            dhw = DHW(
                dhw_file = picture_dhw_filename,
                customer_id = customer.id
            )
            db.session.add(dhw)
            db.session.commit()
            return redirect(url_for('main.appliances'))
        else:
            form = DhWForm(dhw_photo='')
        return render_template('appliances.html',form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)


    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = request.form['category']
        db.session.commit()
        flash("Added Appliance", 'success')
        return redirect(url_for('main.appliances'))

    else:
        appliance_found_bool=False
        return render_template('appliances.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool, furnace=furnace,heating_usage = heating_usage)

@main.route('/add_appliances', methods = ['GET','POST'])
@login_required
@survey_required
def add_appliances():
    appliance_found_bool = False
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).all()
    appliance_categories_query =db.session.query(Appliance.category_appliance.distinct().label("appliance_categories"))
    appliance_categories = [row.appliance_categories for row in appliance_categories_query.all()]
    kitchen_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'kitchen',Appliance.customer_id == customer.id).all()
    basement_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'basement',Appliance.customer_id == customer.id).all()
    entertainment_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'entertainment',Appliance.customer_id == customer.id).all()
    misc_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'misc',Appliance.customer_id == customer.id).all()
    model_detect =os.path.join(app_root, 'furnace_not_furnace.model')
    model_eff = os.path.join(app_root, 'pvc_steel.model')
    target = os.path.join(app_root, 'static/appliance_photos/img')
    form = appliancePhotoForm(appliance_photo='')
    furnace=HeatingEquipment.query.filter(HeatingEquipment.customer_id == customer.id).limit(5).all()

    heating_usage = 0
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    x = TMY_Edmonton.query.all()
    # elec_bill = ElectricalUsage.query.filter_by(customer_id=customer.id).first()
    # elec_consumption = elec_bill.consumption
    # elec_cost=elec_bill.cost
    # elec_rate=elec_cost/elec_consumption
    # gas_rate=6.00
    try:
        efficiency = furnace.efficiency*1
    except:
        efficiency = 0.85
        pass
    try:
        furnace_output = furnace.btu_output/947817
    except:
        furnace_output =((building_info.building_feet)*50)/947817
    for row in x:
        current_regress = 1 - (row.dry_bulb_temperature + 45)/(21 +45)
        if current_regress < 0:
            current_regress = 0
        heating_usage = heating_usage+(furnace_output*current_regress*(1/efficiency))




    if not os.path.isdir(target):
        os.makedirs(target)

    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('add_appliance.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
            appliances=appliances,
            basement_appliances=basement_appliances, appliance_found = appliance_found,entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, heating_usage = heating_usage,filename=file_name , furnace=furnace)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('add_appliance.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, appliances=appliances,appliance_duplicates=appliance_duplicates,
            basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, filename=file_name)


    if request.method == 'POST' and 'furnace_photo' in request.files:
        furnace_photo = request.files.get('furnace_photo',None)
        target = os.path.join(app_root, 'static/furnace_folder')
        form = FurnaceForm(furnace_photo=furnace_photo)
        if form.validate_on_submit():
            picture_furnace_filename = save_picture(furnace_photo,'furnace_folder')
            destination ='/'.join([target,picture_furnace_filename])
            furnace = HeatingEquipment(
                furnace_file = picture_furnace_filename,
                customer_id = customer.id
            )
            db.session.add(furnace)
            db.session.commit()
            return redirect(url_for('main.appliances'))
        else:
            form = FurnaceForm(furnace_photo='')
        return render_template('add_appliance.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)

    if request.method == 'POST' and 'dhw_photo' in request.files:
        dhw_photo = request.files.get('dhw_photo',None)
        target = os.path.join(app_root, 'static/dhw_folder')
        form = DhWForm(dhw_photo=dhw_photo)
        if form.validate_on_submit():
            picture_dhw_filename = save_picture(dhw_photo,'dhw_folder')
            destination ='/'.join([target,picture_dhw_filename])
            dhw = DHW(
                dhw_file = picture_dhw_filename,
                customer_id = customer.id
            )
            db.session.add(dhw)
            db.session.commit()
            return redirect(url_for('main.appliances'))
        else:
            form = DhWForm(dhw_photo='')
        return render_template('add_appliance.html',form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)


    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = request.form['category']
        db.session.commit()
        flash("Added Appliance", 'success')
        return redirect(url_for('main.appliances'))

    else:
        appliance_found_bool=False
        return render_template('add_appliance.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool, furnace=furnace,heating_usage = heating_usage)

@main.route('/appliance_breakdown', methods = ['GET','POST'])
@login_required
@survey_required
def appliance_breakdown():
    appliance_found_bool = False
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).all()
    appliance_categories_query =db.session.query(Appliance.category_appliance.distinct().label("appliance_categories"))
    appliance_categories = [row.appliance_categories for row in appliance_categories_query.all()]
    kitchen_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'kitchen',Appliance.customer_id == customer.id).all()
    basement_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'basement',Appliance.customer_id == customer.id).all()
    entertainment_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'entertainment',Appliance.customer_id == customer.id).all()
    misc_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'misc',Appliance.customer_id == customer.id).all()
    model_detect =os.path.join(app_root, 'furnace_not_furnace.model')
    model_eff = os.path.join(app_root, 'pvc_steel.model')
    target = os.path.join(app_root, 'static/appliance_photos/img')
    furnace=HeatingEquipment.query.filter(HeatingEquipment.customer_id == customer.id).limit(5).all()

    heating_usage = 0
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    x = TMY_Edmonton.query.all()
    return render_template('appliance_breakdown.html',appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool, furnace=furnace,heating_usage = heating_usage)


@main.route('/compareutilityrates', methods = ['GET','POST'])
@login_required
@survey_required
def compareutilityrates():
    appliance_found_bool = False
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).all()
    appliance_categories_query =db.session.query(Appliance.category_appliance.distinct().label("appliance_categories"))
    appliance_categories = [row.appliance_categories for row in appliance_categories_query.all()]
    kitchen_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'kitchen',Appliance.customer_id == customer.id).all()
    basement_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'basement',Appliance.customer_id == customer.id).all()
    entertainment_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'entertainment',Appliance.customer_id == customer.id).all()
    misc_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'misc',Appliance.customer_id == customer.id).all()
    model_detect =os.path.join(app_root, 'furnace_not_furnace.model')
    model_eff = os.path.join(app_root, 'pvc_steel.model')
    target = os.path.join(app_root, 'static/appliance_photos/img')
    form = appliancePhotoForm(appliance_photo='')
    furnace=HeatingEquipment.query.filter(HeatingEquipment.customer_id == customer.id).limit(5).all()

    heating_usage = 0
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    x = TMY_Edmonton.query.all()
    # elec_bill = ElectricalUsage.query.filter_by(customer_id=customer.id).first()
    # elec_consumption = elec_bill.consumption
    # elec_cost=elec_bill.cost
    # elec_rate=elec_cost/elec_consumption
    # gas_rate=6.00
    try:
        efficiency = furnace.efficiency*1
    except:
        efficiency = 0.85
        pass
    try:
        furnace_output = furnace.btu_output/947817
    except:
        furnace_output =((building_info.building_feet)*50)/947817
    for row in x:
        current_regress = 1 - (row.dry_bulb_temperature + 45)/(21 +45)
        if current_regress < 0:
            current_regress = 0
        heating_usage = heating_usage+(furnace_output*current_regress*(1/efficiency))




    if not os.path.isdir(target):
        os.makedirs(target)

    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('compareutilityrates.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
            appliances=appliances,
            basement_appliances=basement_appliances, appliance_found = appliance_found,entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, heating_usage = heating_usage,filename=file_name , furnace=furnace)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('compareutilityrates.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, appliances=appliances,appliance_duplicates=appliance_duplicates,
            basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, filename=file_name)


    if request.method == 'POST' and 'furnace_photo' in request.files:
        furnace_photo = request.files.get('furnace_photo',None)
        target = os.path.join(app_root, 'static/furnace_folder')
        form = FurnaceForm(furnace_photo=furnace_photo)
        if form.validate_on_submit():
            picture_furnace_filename = save_picture(furnace_photo,'furnace_folder')
            destination ='/'.join([target,picture_furnace_filename])
            furnace = HeatingEquipment(
                furnace_file = picture_furnace_filename,
                customer_id = customer.id
            )
            db.session.add(furnace)
            db.session.commit()
            return redirect(url_for('main.compareutilityrates'))
        else:
            form = FurnaceForm(furnace_photo='')
        return render_template('compareutilityrates.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)

    if request.method == 'POST' and 'dhw_photo' in request.files:
        dhw_photo = request.files.get('dhw_photo',None)
        target = os.path.join(app_root, 'static/dhw_folder')
        form = DhWForm(dhw_photo=dhw_photo)
        if form.validate_on_submit():
            picture_dhw_filename = save_picture(dhw_photo,'dhw_folder')
            destination ='/'.join([target,picture_dhw_filename])
            dhw = DHW(
                dhw_file = picture_dhw_filename,
                customer_id = customer.id
            )
            db.session.add(dhw)
            db.session.commit()
            return redirect(url_for('main.appliances'))
        else:
            form = DhWForm(dhw_photo='')
        return render_template('compareutilityrates.html',form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)


    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = request.form['category']
        db.session.commit()
        flash("Added Appliance", 'success')
        return redirect(url_for('main.compareutilityrates'))

    else:
        appliance_found_bool=False
        return render_template('compareutilityrates.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool, furnace=furnace,heating_usage = heating_usage)




@main.route('/appliancedetails/<int:id>', methods = ['GET','POST'])
@login_required
@survey_required
def appliancedetails(id):
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = Appliance.query.filter_by(id=id).first()
    home_upgrades = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    user_home = [60, 50]
    average_home = [75,62]
    return render_template('appliancedetails.html', appliance = appliance, customer = customer, home_upgrades = home_upgrades, user_home = user_home, average_home = average_home)


@main.route('/appliance_usage/', methods = ['GET','POST'])
@login_required
@survey_required
def appliance_usage():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).limit(4).all()
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    heating_equipment = HeatingEquipment.query.filter_by(customer_id=current_user.id)
    heating_usage = 30.86
    current_regress = 0
    light_usage = 2.16
    appliance_usage = 9.27
    ventilation_usage = 20.03
    dhw_usage = 27.14
    total = heating_usage + light_usage + appliance_usage + ventilation_usage + dhw_usage
    lighting_cost = "$" + str(50)
    appliance_cost = "$" + str(50)
    ventilation_cost = "$" + str(50)
    hot_water_cost = "$" + str(50)
    heating_cost = "$" + str(50)
    return render_template('appliance_usage.html', appliances = appliances, customer = customer,  light_usage=light_usage,dhw_usage=dhw_usage, heating_usage = heating_usage,
        ventilation_usage = ventilation_usage,appliance_usage = appliance_usage,
        lighting_cost = lighting_cost, appliance_cost = appliance_cost, ventilation_cost = ventilation_cost,
        hot_water_cost = hot_water_cost, heating_cost = heating_cost, total = total)

@main.route('/updateappliance', methods = ['GET', 'POST'])
@login_required
@survey_required
def updateappliance():
    appliance_found_bool = False
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        my_data = Appliance.query.get(request.form.get('id'))

        my_data.usage_time = request.form['usage_time']
        my_data.category_appliance = request.form['category']
        db.session.commit()
        flash("updated",'success')

        return redirect(url_for('main.appliances'))



@main.route('/uploadfurnace', methods = ['GET', 'POST'])
def uploadfurnace():
    appliance_found_bool = False
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = furnaceForm(furnace_photo='')
    furnace=HeatingEquipment.query.filter(HeatingEquipment.customer_id == customer.id).limit(5).all()
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).limit(5).all()
    appliance_categories_query =db.session.query(Appliance.category_appliance.distinct().label("appliance_categories"))
    appliance_categories = [row.appliance_categories for row in appliance_categories_query.all()]
    kitchen_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'kitchen',Appliance.customer_id == customer.id).all()
    basement_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'basement',Appliance.customer_id == customer.id).all()
    entertainment_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'entertainment',Appliance.customer_id == customer.id).all()
    misc_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'misc',Appliance.customer_id == customer.id).all()
    model_detect =os.path.join(app_root, 'furnace_not_furnace.model')
    model_eff = os.path.join(app_root, 'pvc_steel.model')
    target = os.path.join(app_root, 'static/furnace_photos/img')
    furnace_found_bool=False

    if request.method == "POST" and "furnace_photo" in  request.files:
        #savings the photo
        furnace_photo = request.files.get('furnace_photo', None)
        file_name = save_picture_appliance(furnace_photo,'furnace_photos/img')
        destination = '/'.join([target, file_name])
        image_array = img_array(destination)
        furnace_detect= is_furnace(image_array)
        if furnace_detect[0] == 'Furnace':
            if furnace_detect[1] < 0.4:
        #if this function is true, then we have not found an appliance
                furnace_not_found_bool=True
                print(furnace_not_found_bool , 'furnace_not_found_bool')
                return render_template('appliances.html',form=form,furnace_found_bool=furnace_found_bool, furnace_not_found_bool=furnace_not_found_bool,
                 customer=customer, filename=file_name, appliance_found=appliance_found)
            else:
                print('furnace found')
                eff_detect = is_pvc(image_array)
                eff_detect = eff_detect[0]
                print(eff_detect)
                if 'PVC' in eff_detect:
                    eff_detect=0.92
                else:
                    eff_detect=0.80
                appliance_found_bool=True
                if eff_detect==0.8:
                    efficiency='low'
                else:
                    efficiency='high'
                try:
                    btu_output=customer.square_footage*50
                except:
                    btu_output = 50000
                    pass
                btu_input= btu_output/(eff_detect)
                furnace_found_bool=True
                appliance_found_bool=False
                type_heating = 'furnace'
                name_plate=''

                print(eff_detect)
                new_furnace = HeatingEquipment(btu_input=btu_input,type_heating=type_heating,btu_output=btu_output,
                    efficiency=eff_detect,
                    unique_photo_id=file_name,
                    furnace_file=file_name,
                    name_plate=name_plate,
                customer_id=customer.id,)
                db.session.add(new_furnace)
                db.session.commit()
                appliance_new=HeatingEquipment.query.order_by(HeatingEquipment.id.desc()).first()





                return render_template('appliances.html', form=form, appliance_new=appliance_new,
                furnace_found_bool=furnace_found_bool,
                filename=file_name, 
                efficiency=efficiency, 
                appliances=appliances,
                basement_appliances=basement_appliances, 
                entertainment_appliances=entertainment_appliances,
                kitchen_appliances=kitchen_appliances, 
                misc_appliances=misc_appliances,
                appliance_found_bool=appliance_found_bool, 
                furnace=furnace)


        else:
            furnace_not_found_bool=True
            print(furnace_not_found_bool,'furnace_not_found_bool')


        #     return render_template('appliances.html', form=form, furnace_not_found_bool=furnace_not_found_bool,furnace_found_bool=furnace_found_bool,
        #         customer=customer, filename=file_name,appliance_found=appliance, appliances=appliances,
        # basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        # kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances,appliance_found_bool=appliance_found_bool, furnace=furnace)
        flash("We see your Furnace, but try taking another photo", 'danger')
        return redirect('/appliances' )

    else:
        furnace_found_bool=False
        print(furnace_found_bool,'furnace_found_bool')
        return render_template('appliances.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,
        furnace_found_bool=furnace_found_bool, furnace=furnace)


@main.route('/deleteappliance/<id>/', methods = ['GET', 'POST'])
@login_required
@survey_required
def deleteappliance(id):
    appliance = Appliance.query.get(id)
    db.session.delete(appliance)
    db.session.commit()
    flash("Deleted Appliance",'success')

    return redirect(request.referrer)




@main.route('/deleteheating/<id>/', methods = ['GET', 'POST'])
@login_required
@survey_required
def deletefurnace(id):
    appliance = HeatingEquipment.query.get(id)
    db.session.delete(appliance)
    db.session.commit()
    flash("Deleted Furnace",'success')

    return redirect('/appliances')


@main.route('/waysToSave/',methods=['GET', 'POST'])
@survey_required
@login_required
def waysToSave():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    return render_template('waysToSave.html',title='Ways To Save',customer=customer, last_updated=dir_last_updated())


@main.route('/request_quote/',methods=['GET','POST'])
@survey_required
@login_required
def request_quote():
    customer = Customer.query.get(current_user.id)
    dhw = DHW.query.filter_by(customer_id=customer.id).first()
    heating_equipment = HeatingEquipment.query.filter_by(customer_id=customer.id).first()
    current_date = datetime.now()
    can_create_quote_heating = not (Quote.query.filter(Quote.customer_id==customer.id,Quote.time_due >= current_date,Quote.quote_type == 'QuoteHeating').count() > 0)
    can_create_quote_dhw = not (Quote.query.filter(Quote.customer_id==customer.id,Quote.time_due >= current_date,Quote.quote_type == 'QuoteDHW').count() > 0)
    return render_template('request_quote.html',title='Request A Quote', customer=customer, dhw=dhw,heating_equipment=heating_equipment, can_create_quote_heating=can_create_quote_heating,can_create_quote_dhw=can_create_quote_dhw, last_updated=dir_last_updated())

@main.route('/request_quote/add_quote',methods=['GET','POST'])
@survey_required
@login_required
def create_quote():
    current_date = datetime.now()
    customer = Customer.query.get(current_user.id)
    if request.method == 'POST':
        quote_type = request.form.get('quote_type')
        can_create_quote = not(Quote.query.filter(Quote.customer_id==customer.id,Quote.time_due >= current_date, Quote.quote_type == quote_type).count() > 0)
        if can_create_quote == True:
            response1 = request.form['response1']
            response2 = request.form['response2']
            video = request.files['video']
            form = QuoteForm(
                quote_type = quote_type,
                response1 = response1,
                response2 = response2,
                video = video
            )
            if form.validate_on_submit():
                city_customer = customer.city
                next_date = current_date + timedelta(days=1)

                video_name = save_video(video,'video')
                new_quote = Quote(
                    quote_type = quote_type,
                    response1 = response1,
                    response2 = response2,
                    time_due = next_date,
                    video_name = video_name,
                    customer_id = customer.id
                    )
                db.session.add(new_quote)
                db.session.commit()
                if quote_type == 'QuoteHeating':
                    companies = Company.query.join(Company.services).filter(Service.name=="Heating & Ventilation & Air Conditioning",Company.services_areas.any(city_customer)).order_by(func.random()).limit(10).all()
                    message = flash('Quote for the Furnace, You should receive an email once the quote is done','success')
                else:
                    companies = Company.query.join(Company.services).filter(Service.name=="Plumbing & Water Heating",Company.services_areas.any(city_customer)).order_by(func.random()).limit(10).all()
                    message = flash('Quote for the DHW, You should receive an email once the quote is done','success')
                for company in companies:
                    new_response_quote = ResponseQuote(
                        quote_id = new_quote.id,
                        quote_type = quote_type,
                        time_due = next_date,
                        company_id = company.id
                    )
                    db.session.add(new_response_quote)
                db.session.commit()
                message
            return redirect(url_for('main.request_quote'))
        else:
            form = QuoteForm(
                quote_type = "",
                response1 = "",
                response2 = "",
                video = "",
            )
    return render_template('request_quote.html',title='Request A Quote',form=form,dhw=dhw,heating_equipment=heating_equipment,can_create_quote=can_create_quote,last_updated=dir_last_updated())

@main.route('/appliance_photo/<filename>')
@login_required
@survey_required
def display_image(filename):
    return redirect(url_for('static', filename='appliance_photos/img/' + filename), code=301)


@main.route('/furnace_photo/<filename>')
@login_required
@survey_required
def display_image_furnace(filename):
    return redirect(url_for('static', filename='furnace_photos/img/' + filename), code=301)


@main.route('/sw.js', methods=['GET'])
def sw():
    return current_app.send_static_file('sw.js')






@main.route('/dhw_photo/<filename>')
@login_required
@survey_required
def display_image_dhw(filename):
    return redirect(url_for('static', filename='dhw_folder' + filename), code=301)





@main.route('/fridge/',methods=['GET', 'POST'])
def fridge():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')

    target = os.path.join(app_root, 'static/appliance_photos/img')
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('fridge.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
             customer=customer, filename=file_name, appliance_found=appliance_found)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('fridge.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, customer=customer, filename=file_name)



    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = 'kitchen'
        db.session.commit()
        flash("Added Appliance", 'success')
        return render_template('fridge.html', form=form, appliance_found=appliance, correctApplianceBoolian=correctApplianceBoolian,
             customer=customer)


    else:
        appliance_found_bool=False
        return render_template('fridge.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)


@main.route('/microwave/',methods=['GET', 'POST'])
def microwave():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')
    target = os.path.join(app_root, 'static/appliance_photos/img')
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('microwave.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
             customer=customer, filename=file_name, appliance_found=appliance_found)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('microwave.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, customer=customer, filename=file_name)



    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = 'kitchen'
        db.session.commit()
        flash("Added Appliance", 'success')
        return render_template('microwave.html', form=form, appliance_found=appliance, correctApplianceBoolian=correctApplianceBoolian,
             customer=customer)


    else:
        appliance_found_bool=False
        return render_template('microwave.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)

@main.route('/stove/',methods=['GET', 'POST'])
def stove():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')

    target = os.path.join(app_root, 'static/appliance_photos/img')
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('stove.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
             customer=customer, filename=file_name, appliance_found=appliance_found)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('stove.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, customer=customer, filename=file_name)



    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = 'kitchen'
        db.session.commit()
        flash("Added Appliance", 'success')
        return render_template('stove.html', form=form, appliance_found=appliance, correctApplianceBoolian=correctApplianceBoolian,
             customer=customer)


    else:
        appliance_found_bool=False
        return render_template('stove.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)


@main.route('/washer/',methods=['GET', 'POST'])
def washer():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')

    target = os.path.join(app_root, 'static/appliance_photos/img')
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('washer.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
             customer=customer, filename=file_name, appliance_found=appliance_found)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('washer.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, customer=customer, filename=file_name)



    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = 'kitchen'
        db.session.commit()
        flash("Added Appliance", 'success')
        return render_template('washer.html', form=form, appliance_found=appliance, correctApplianceBoolian=correctApplianceBoolian,
             customer=customer)


    else:
        appliance_found_bool=False
        return render_template('washer.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)

@main.route('/dryer/',methods=['GET', 'POST'])
def dryer():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')


    target = os.path.join(app_root, 'static/appliance_photos/img')
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('dryer.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
             customer=customer, filename=file_name, appliance_found=appliance_found)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('dryer.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, customer=customer, filename=file_name)



    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = 'kitchen'
        db.session.commit()
        flash("Added Appliance", 'success')
        return render_template('dryer.html', form=form, appliance_found=appliance, correctApplianceBoolian=correctApplianceBoolian,
             customer=customer)


    else:
        appliance_found_bool=False
        return render_template('dryer.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)


@main.route('/tank/',methods=['GET', 'POST'])
def tank():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    target = os.path.join(app_root, 'static/appliance_photos/img')
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('tank.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
             customer=customer, filename=file_name, appliance_found=appliance_found)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('tank.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, customer=customer, filename=file_name)



    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = request.form['category']
        db.session.commit()
        flash("Added Appliance", 'success')
        return redirect(url_for('main.tank'))


    else:
        appliance_found_bool=False
        return render_template('tank.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)



@main.route('/furnace/',methods=['GET', 'POST'])
def furnace():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')
    appliance_not_found_bool=False
    appliance_found=''

    target = os.path.join(app_root, 'static/appliance_photos/img')
    model_detect =os.path.join(app_root, 'furnace_not_furnace.model')
    model_eff = os.path.join(app_root, 'pvc_steel.model')
    furnace_not_found=False
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        image_array = img_array(destination)
        furnace_detect= is_furnace(image_array)

        if furnace_detect[0] == 'Furnace':
            if furnace_detect[1] < 0.4:
                print('furnace_found,take a better photo')
        #if this function is true, then we have not found an appliance
                appliance_found == 'Furnace'
                appliance_not_found_bool=True
                print(appliance_found)
                return render_template('furnace.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
                 customer=customer, filename=file_name, appliance_found=appliance_found)
            else:
                print('furnace found')
                eff_detect = is_pvc(image_array)
                eff_detect = eff_detect[0]
                print(eff_detect)
                if 'PVC' in eff_detect:
                    eff_detect=0.95
                else:
                    eff_detect=0.80
                appliance_found_bool=True
                if eff_detect==0.8:
                    efficiency='low'
                else:
                    efficiency='high'
                btu_input=100

                btu_output=btu_input*eff_detect
                appliance_found_bool=True
                print(eff_detect)
                new_furnace = HeatingEquipment(btu_input=btu_input,btu_output=btu_output,efficiency=eff_detect,
                customer_id=customer.id,)
                db.session.add(new_furnace)
                db.session.commit()
                appliance_new=HeatingEquipment.query.order_by(HeatingEquipment.id.desc()).first()

                return render_template('furnace.html', form=form, appliance_new=appliance_new, appliance_found=appliance,
                appliance_found_bool=appliance_found_bool,
                customer=customer, filename=file_name, efficiency=efficiency)


        else:
            #this is the appliance name is an appliance is found

            appliance_not_found_bool=True
            furnace_not_found = True



            return render_template('furnace.html', form=form, appliance_not_found_bool=appliance_not_found_bool,furnace_not_found=furnace_not_found,
                customer=customer, filename=file_name)




    else:
        appliance_found_bool=False
        return render_template('furnace.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)


@main.route('/other/',methods=['GET', 'POST'])
def other():

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    target = os.path.join(app_root, 'static/appliance_photos/img')
    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('other.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
             customer=customer, filename=file_name, appliance_found=appliance_found)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('other.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, customer=customer, filename=file_name)



    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = request.form['category']
        db.session.commit()
        flash("Added Appliance", 'success')
        return redirect(url_for('main.other'))


    else:
        appliance_found_bool=False
        return render_template('other.html', form=form,appliance_found=appliance, customer=customer,appliance_found_bool=appliance_found_bool)

def save_video(form_video,location):
    random_hex = secrets.token_hex(8)
    file_extension = os.path.splitext(form_video.filename)[1]
    video_filename = random_hex + file_extension
    video_path = os.path.join(app_root,'static/'+location,video_filename)
    form_video.save(video_path)
    return video_filename


@main.route('/m_addbill/',methods=['GET', 'POST'])
def m_addbill():
    session["upgrade_package"] = []
    target = os.path.join(app_root, 'static/electrical_folder') # maybe move to S3
    form = electricPhotoForm(electric_photo='')
    if not os.path.isdir(target):
        os.makedirs(target)
    if request.method == "POST" and "electrical_photo" in  request.files:
        #saving the photo
        electrical_photo = request.files.get('electrical_photo', None)

        file_name = save_picture(electrical_photo,"electrical_folder")
        #first detect text on the bill itself
        target = os.path.join(app_root, 'static/electrical_folder')
        destination = '/'.join([target, file_name])
        electrical_bill_reckognize = detectText(destination)
        #now find a company to apply the proper method
        electrical_company = detect_company(electrical_bill_reckognize)
        #now that company is found, apply method to return values for detecting bill
        #check if detection returns error, if so rename variable to specifify error found

        if electrical_company == 'error':
            flash('Your bill was not recognized, please take another photo', 'danger')

        #if no error, proceed
        else:
            # save to database
            full_detection = detect_electrical_bill(electrical_company,electrical_bill_reckognize)
          
            session["electric_consumption"] = float(full_detection[0][0]) # this doesnt give the city!!!!!! i need the city
            session["address"] = full_detection[1]
            session["city"] = 'sedgewick' #full_detection[3] not ready some bills it gives numbers 
            session["province"] = "alberta"
            session["bill"] = float(full_detection[2])
            session["electricity_charged"] = float(full_detection[2]) + 0.05*(float(full_detection[2]))
            session["customer_electrical_rate"] = float(session["electricity_charged"])/float(session["electric_consumption"])
            session["e_rates"] = [] # id of the best 3 rates in the city

            # add some saftey checks here so that there is no crash later
            # make suer no NoneTypes are passed on 
            # maybe add a 'Confirm my information" screen

            # Bill comparison
            e_consumption = session["electric_consumption"]

            
            if (session["city"] != "sedgewick"):
                e_rates = ElectricalRates.query.filter_by(city=session["city"]).order_by(total_rate).limit(3).all() # might need to do rate comparison in a separate function when total_rate column is removed

            else:
                e_rates = ElectricalRates.query.filter_by(city=session["city"]).all()
                
                '''
                best_rates = []
                best_rates += e_rates[:3]
                for r in e_rates[3:]:
                    a = calculate_total_bill(r, e_consumption, True)
                    if (a < calculate_total_bill(best_rates[0], e_consumption, True)):
                        best_rates = [r] + best_rates[:2]
                    elif (a < calculate_total_bill(best_rates[1], e_consumption, True)):
                        best_rates = [best_rates[0]] + [r] + [best_rates[1]]
                    elif (a < calculate_total_bill(best_rates[2], e_consumption, True)):
                        best_rates = best_rates[:2] = [r]
                e_rates = best_rates # i think this is suppose to be the best 3 rates in our database?
                '''
            for i in range(len(e_rates) - 1,-1,-1):
                session["e_rates"] += [(e_rates[i].id)]

            return redirect(url_for('main.m_utility_costs'))

    return render_template("mobile/m_comparison.html", form=form)


# Currently has a special case for sedgewick due to db data issues.
def calculate_total_bill(rate, found_kwh, is_sedgewick):
    """Calculates the dollar amount of a bill given an electricity rate and kwh usage."""   
    if (is_sedgewick):
        b = ((((rate.variable_distribution + rate.varible_transmission+rate.balancing_pool_rate_rider+rate.per_kwh_rate_rider+rate.retailer_charge)/100)*found_kwh+(rate.local_access_fee+rate.retail_admin_fee)+(rate.fixed_distribution *30))+((((rate.variable_distribution + rate.varible_transmission+rate.balancing_pool_rate_rider+rate.per_kwh_rate_rider+rate.retailer_charge)/100)*found_kwh+(rate.local_access_fee+rate.retail_admin_fee)+(rate.fixed_distribution *30))*0.05))
        return round(b, 2)
    else:
        return rate.total_rate * found_kwh / 100


# TODO move me somewhere else.
class _upgrade_card:
    # all attributes can be string because they will only be read in the template
    def __init__(self, id, title, savings, cost, img_file="upgrade_default", link="", is_upgrade=True):
        self.id = id
        self.title = str(title)
        self.savings = str(savings)
        self.cost = cost
        self.img_file = url_for('static',filename=img_file+'.png')
        self.link = str(link)
        self.is_upgrade = is_upgrade # needs to be bool


class _rate_card:
    def __init__(self, _id, retailer, rate, pricing):
        self.id = _id
        self.retailer = retailer
        self.effective_rate = rate
        self.pricing = pricing
        self.img_file = url_for('static',filename=self.retailer+'.png')


# TODO move the source data to db and update fetch algorithm.
def read_upgrades_csv(appliance_wattage, electrical_rate): # electrical_rate is the best rate found in the area
    """Reads data source upgrades_data.csv and fetches data for display."""

    ret = []
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    file_name = absolute_path + f"/static/upgrades_data.csv"
    with open(file_name, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            _id = row["id"]
            _t = row["title"]
            _c = 0 if (row["cost"] == '-1') else row["cost"]
            # savings calculations
            _w = float(row["wattage"])
            upgrade_key = "default"
            # tell which upgrade we doing -- TODO put this data in db and create enum and use switch case
            if ('fridge' in _t.lower()):
                upgrade_key = 'fridge'
            elif ('washer' in _t.lower()):
                upgrade_key = 'washer'
            elif ('dryer' in _t.lower()):
                upgrade_key = 'dryer'
            elif ('led lights' in _t.lower()):
                upgrade_key = 'lights'
            elif ('led christmas lights' in _t.lower()):
                upgrade_key = 'xmas_lights'

            # calculate difference in wattage
            _s = round(((appliance_wattage[upgrade_key] - _w)/1000) * 30 * 24 * electrical_rate / 100, 2)

            u = _upgrade_card(id=_id,
                              title=_t,
                              savings=_s,
                              cost=_c,
                              link=row["link"])
            ret.append(u)
    return ret


# used as ajax call for keeping track of picked upgrades (for estimations) -- stored in session["upgrade_package"]
@main.route('/bg_upgrade_package_append/', methods=['POST'])
def bg_upgrade_package_append():
    if (request.form["checked"] == 'true'):
        session["upgrade_package"] += [request.form["card_id"]] # assumes session["upgrade_package"] exists
    elif (request.form["checked"] == 'false'):
        a = session["upgrade_package"] # idk why this has to be roundabout
        a.remove(request.form["card_id"])
        session["upgrade_package"] = a
    return "Done"

################################################################################################################
#mobile views
#################################################################

#this has been moved to the bottom ln 1885
#@main.route('/m_menu/')
#def m_menu():
#    return render_template("mobile/m_menu.html")

@main.route('/m_utility_costs/', methods=["GET", "POST"])
def m_utility_costs():
    if request.method == "POST":
        session["rate_details_id"] = request.form["redirect_id"]
        return redirect(url_for('main.m_rate_details'))
    
    e_consumption = session["electric_consumption"]

    e_rates = ElectricalRates.query.filter_by(city=session["city"]).all()

    e_rates_cards = []
    for rate in e_rates:
        if (rate.total_rate is None):
            effective_rate = round((((((rate.variable_distribution + rate.varible_transmission+rate.balancing_pool_rate_rider+rate.per_kwh_rate_rider+rate.retailer_charge)/100)*e_consumption+(rate.local_access_fee+rate.retail_admin_fee)+(rate.fixed_distribution *30))+((((rate.variable_distribution + rate.varible_transmission+rate.balancing_pool_rate_rider+rate.per_kwh_rate_rider+rate.retailer_charge)/100)*e_consumption+(rate.local_access_fee+rate.retail_admin_fee)+(rate.fixed_distribution *30))*0.05))/e_consumption),2)
        else:
            effective_rate = rate.total_rate
        retailer = str(rate.retailer)
        pricing = str(rate.pricing)
        e_rates_cards.append(_rate_card(rate.id, retailer, effective_rate, pricing))

    e_rates = sorted(e_rates_cards, key=operator.attrgetter('effective_rate'))

    return render_template("mobile/m_utility_costs.html", e_rates=e_rates_cards,
                                                         address=session["address"],
                                                         city=session["city"],
                                                         province=session["province"])
    
    
@main.route('/m_utility_costs/rate_details', methods=["GET","POST"])
def m_rate_details():
    # display stuff for rate details. what do we show? #probably need this to calculate some upgrades 
    rate = ElectricalRates.query.filter_by(id=session["rate_details_id"]).first() #rate detials is not in db
    savings = 12.34 # TODO calculate me
    bill_total = 0 # TODO calculate me
    contract_length = 1 # TODO calculate me
    
    rate_data = {
        "retailer" : rate.retailer,
        "title" : rate.plan_details,
        "kwh_rate" : rate.retailer_charge,
        "admin_fee" : rate.retail_admin_fee,
        "contract_length" : contract_length,
        "early_exit_fee" : 1,
        "contract_remaining" : 1,
        "bill_total" : bill_total,
        "savings" : savings,
        "img_file" : url_for('static', filename=rate.retailer+".png")
    }
    
    user_rate_data = {  # TODO fill me in -- this is for comparison with user's current plan
        
    }
    
    return render_template("mobile/m_rate_details.html", data=rate_data,
                                                        user_rate=user_rate_data)
#@main.route('/')
@main.route('/m_overview/',methods=['GET', 'POST'])
@login_required
@type_required
@survey_required
def m_overview():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    issues = db.session.query(IssueStatic).filter(IssueStatic.address==customer.address).all()
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).limit(4).all()
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    heating_equipment = HeatingEquipment.query.filter_by(customer_id=customer.id)
    current_weather = EdmontonWeather.query.order_by(EdmontonWeather.id.desc()).first()
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=edmonton&appid=b543e04dda3e7a9ada2c9f3cd28e6db6')
    r = r.json()
    current_temp= float((r["main"]["temp"])-273.15)
    current_condition = r['weather'][0]['main']
    temperature = int((r["main"]["temp"])-273.15)
    icon = r['weather'][0]['icon']
    heating_usage = 0
    current_regress = 0
    x = TMY_Edmonton.query.all()
    elec_bill = ElectricalUsage.query.filter_by(customer_id=customer.id).first()
    elec_consumption = elec_bill.consumption
    elec_cost=elec_bill.cost
    elec_rate=elec_cost/elec_consumption
    gas_rate=6.00
    try:
        efficiency = heating_equipment.efficiency*1
    except:
        efficiency = 0.85
        pass
    try:
        furnace_output = heating_equipment.btu_output/947817
    except:
        furnace_output =((building_info.building_feet)*50)/947817
    current_regress = 0
    light_usage = 2.16
    appliance_usage = 9.27
    ventilation_usage = 0.2
    dhw_usage = 27
    for row in x:
        current_regress = 1 - (row.dry_bulb_temperature + 45)/(21 +45)
        if current_regress < 0:
            current_regress = 0
        heating_usage = heating_usage+(furnace_output*current_regress*(1/efficiency))

    return render_template('mobile/m_overview.html',title='m_Overview',customer=customer,appliances=appliances,issues=issues,
        light_usage=light_usage,dhw_usage=dhw_usage, heating_usage = heating_usage,
        ventilation_usage = ventilation_usage,appliance_usage = appliance_usage,
        last_updated=dir_last_updated())


@main.route('/m_home_comparison/',methods=['GET', 'POST'])
def m_home_comparison():
    home_info = {
        "address" : session["address"],
        "city" : session["city"].capitalize(),
        "province" : "AB" 
    }

    #adding a bill detection section to this area from billutility

    customer = Customer.query.filter_by(user_id=current_user.id).first()

     #db.session.query(ElectricalUsage).filter(ElectricalUsage.customer_id ==
    #current_user.id).order_by(ElectricalUsage.id.desc()).first()
    electrical_rates = ElectricalRates.query.all()
    target = os.path.join(app_root, 'static/electrical_folder')
    form = electricPhotoForm(electric_photo='')
    electric_bills = ElectricalUsage.query.order_by(-ElectricalUsage.id).filter(ElectricalUsage.customer_id == customer.id).limit(5).all()
    bill_identified = False
    wrong_page = False



    if not os.path.isdir(target):
        os.makedirs(target)

    if request.method == "POST" and "electrical_photo" in  request.files:
        #savings the photo
        electrical_photo = request.files.get('electrical_photo', None)

        file_name = save_picture(electrical_photo,"electrical_folder")
        #first detect text on the bill itself
        target = os.path.join(app_root, 'static/electrical_folder')
        destination = '/'.join([target, file_name])
        electrical_bill_reckognize = detectText(destination)
        #now find a company to apply the proper method
        electrical_company = detect_company(electrical_bill_reckognize)
        #now that company is found, apply method to return values for detecting bill
        #check if detection returns error, if so rename variable to specifify error found

        if electrical_company == 'error':
            flash('Your bill was not recognized, please take another photo', 'danger')
        #if no error, proceed

        else:
        #find city via method in bill detection
            full_detection = detect_electrical_bill(electrical_company,electrical_bill_reckognize)
            electrical_usage = ElectricalUsage(consumption = float(full_detection[0][0]), cost = float(full_detection[2]),
                electrical_file = file_name,customer_id=customer.id)
            db.session.add(electrical_usage)
            db.session.commit()





            found_kwh = float(full_detection[0][0])
            address_found = full_detection[1]
            electricity_charged = float(full_detection[2]) + 0.05*(float(full_detection[2]))
            customer_electrical_rate = float(electricity_charged)/float(found_kwh)
            bill_identified = True
            electric_bills = ElectricalUsage.query.order_by(-ElectricalUsage.id).filter(ElectricalUsage.customer_id == customer.id).limit(5).all()
            print(customer_electrical_rate)
            return render_template('mobile/m_home_comparison.html',title='Utility Bills',form=form,customer=customer,
            bill_provider = electrical_company,
            found_kwh = found_kwh,
            address_found = address_found,
            electricity_charged=electricity_charged,
            wrong_page=wrong_page,
            bill_identified= bill_identified,
            electric_bills=electric_bills,
            customer_electrical_rate=customer_electrical_rate, 
            electrical_rates=electrical_rates,
            ast_updated=dir_last_updated(),
            home_info = home_info)

    return render_template('mobile/m_home_comparison.html',title='Utility Bills',form=form,customer=customer,
        wrong_page=wrong_page,
        electric_bills=electric_bills,
        bill_identified= bill_identified,
        electrical_rates=electrical_rates,
        last_updated=dir_last_updated(), 
        home_info = home_info)
    




def m_upgrades():
    
    #if request.method == "POST":
    #     session["upgrade_details_id"] = request.form["upgrade_details_id"] upgrade details 
    #     return redirect(url_for('main.m_upgrade_details'))

    # customers energy consumption in kWh
    
    e_consumption = session["electric_consumption"]
    customer_bill = session["bill"]
    _is_sedgewick = True if session["city"] == "sedgewick" else False
    best_rate = ElectricalRates.query.filter_by(id=session["e_rates"][-1]).first() 

    # appliance assumptions, what are the real estimations? -- TODO put in the real numbers
    appliance_wattage = {
        "fridge" : 100,
        "washer" : 100,
        "dryer" : 100,
        "lights" : 100,
        "xmas_lights" : 0,
        "default" : 0
    }
    _total_rate = calculate_total_bill(best_rate,1,_is_sedgewick)
    upgrades = read_upgrades_csv(appliance_wattage, _total_rate) # TODO from a big list of upgrades, pick only handful that saves the most

    

    
    # important to fix this. should grab data from database insteadof fillinf session
    if request.method == "POST":
        session["upgrade_details_id"] = request.form["upgrade_details_id"]
        u_id = int(session["upgrade_details_id"]) -1
        session["upgrade_details_title"] = upgrades[u_id].title
        session["upgrade_details_savings"] = upgrades[u_id].savings
        return redirect(url_for('main.m_upgrade_details'))

    return render_template("mobile/m_upgrades.html", e_consumption=e_consumption,
                                                 upgrades=upgrades,
                                                 upgrade_package=session["upgrade_package"],
                                                 address=session["address"],
                                                 city=session["city"],
                                                 province=session["province"])


@main.route('/m_upgrades/upgrade_details', methods=["GET","POST"])
def m_upgrade_details():
    upgrades = []
    
    # need to put the data into database
    
    # # this is temporary implementation of getting data. get the upgrades into database asap
    
    title = session["upgrade_details_title"]
    desc = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur metus lorem, volutpat 
            quis aliquam vel, pulvinar non turpis. Sed vitae vehicula mi. Phasellus eu volutpat."""
    todo_list = ['Say hello','to my little friend']
    savings = session["upgrade_details_savings"] # how to calculate?
    
    upgrade_data = {
        "title" : title,
        "savings" : str(savings),
        "desc" : desc,
        "todo_list" : todo_list,
        "upgrade_category" : "constant_use_appliances"
    }
    return render_template("mobile/m_upgrade_details.html", data=upgrade_data)


# move this to articles blueprint?
@main.route('/articles/constant_use_appliances', methods=["GET"])
def a_articles_window():
    return render_template("articles/a_const_appliances.html")


@main.route('/m_appliances', methods = ['GET','POST'])
@login_required
@survey_required
def m_appliances():
    appliance_found_bool = False
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    appliance = ''
    form = ApplianceForm(appliance_photo='')
    appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).limit(5).all()
    appliance_categories_query =db.session.query(Appliance.category_appliance.distinct().label("appliance_categories"))
    appliance_categories = [row.appliance_categories for row in appliance_categories_query.all()]
    kitchen_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'kitchen',Appliance.customer_id == customer.id).all()
    basement_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'basement',Appliance.customer_id == customer.id).all()
    entertainment_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'entertainment',Appliance.customer_id == customer.id).all()
    misc_appliances = db.session.query(Appliance).filter(Appliance.category_appliance == 'misc',Appliance.customer_id == customer.id).all()
    model_detect =os.path.join(app_root, 'furnace_not_furnace.model')
    model_eff = os.path.join(app_root, 'pvc_steel.model')
    target = os.path.join(app_root, 'static/appliance_photos/img')
    form = appliancePhotoForm(appliance_photo='')
    furnace=HeatingEquipment.query.filter(HeatingEquipment.customer_id == customer.id).limit(5).all()

    heating_usage = 0
    building_info = Customer.query.filter_by(user_id=current_user.id).first()
    x = TMY_Edmonton.query.all()
    # elec_bill = ElectricalUsage.query.filter_by(customer_id=customer.id).first()
    # elec_consumption = elec_bill.consumption
    # elec_cost=elec_bill.cost
    # elec_rate=elec_cost/elec_consumption
    # gas_rate=6.00
    try:
        efficiency = furnace.efficiency*1
    except:
        efficiency = 0.85
        pass
    try:
        furnace_output = furnace.btu_output/947817
    except:
        furnace_output =((building_info.building_feet)*50)/947817
    for row in x:
        current_regress = 1 - (row.dry_bulb_temperature + 45)/(21 +45)
        if current_regress < 0:
            current_regress = 0
        heating_usage = heating_usage+(furnace_output*current_regress*(1/efficiency))




    if not os.path.isdir(target):
        os.makedirs(target)

    if request.method == "POST" and "appliance_photo" in  request.files:
        #savings the photo
        appliance_photo = request.files.get('appliance_photo', None)
        file_name = save_picture_appliance(appliance_photo,'appliance_photos/img/')
        destination = '/'.join([target, file_name])
        appliance_name_aws= aws_rek(destination)
        appliances_static_query= ApplianceStatic.query.all()
        #this is the function matching appliances
        appliance_list_static = []

        for row in appliances_static_query:
            appliance_list_static = closeMatches(appliance_name_aws[0],row.appliance_name.lower()) + appliance_list_static
        filtered_dictionary = dict((k, appliance_name_aws[1][k]) for k in [x.lower() for x in appliance_list_static] if k in appliance_name_aws[1])
        #if this function is true, then we have not found an appliance
        if len(appliance_list_static) == 0:
            appliance_found = closeMatches(appliance_name_aws[0],row.appliance_name.lower())
            appliance_not_found_bool=True
            appliance_found=appliance_name_aws[0]
            return render_template('mobile/m_appliances.html',form=form, appliance_not_found_bool=appliance_not_found_bool,
            appliances=appliances,
            basement_appliances=basement_appliances, appliance_found = appliance_found,entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, heating_usage = heating_usage,filename=file_name , furnace=furnace)
        else:
            #this is the appliance name is an appliance is found
            static_appliance_match = max(filtered_dictionary)
            #after appliance is found
            appliance_query = ApplianceStatic.query.filter_by(appliance_name=static_appliance_match).first()
            appliance_name = appliance_query.appliance_name
            appliance_type = appliance_query.category
            appliance_type_static = appliance_query.appliance_name
            rated_power = appliance_query.power
            usage_time = 1
            category_appliance = 'kitchen'
            #cost = (int(rated_power)/1000)*0.11*(int(usage_time))*4
            appliance_name = appliance_name.title()
            appliance_duplicates=Appliance.query.filter(Appliance.appliance_type==appliance_type_static,Appliance.customer_id == customer.id).all()
            print(appliance_duplicates)
            appliance_found_bool=True

            new_appliance = Appliance(appliance_name=appliance_name,appliance_type=appliance_type_static,rated_power=rated_power,photo_id=file_name,
                customer_id=customer.id,
                usage_time=usage_time,category_appliance=category_appliance)
            db.session.add(new_appliance)
            db.session.commit()
            appliance_new=Appliance.query.order_by(Appliance.id.desc()).first()

            return render_template('mobile/m_appliances.html', form=form, appliance_new=appliance_new, appliance_found=appliance, appliance_found_bool=appliance_found_bool,
            appliance_type_static=appliance_type_static, appliances=appliances,appliance_duplicates=appliance_duplicates,
            basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
            kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer, filename=file_name)


    if request.method == 'POST' and 'furnace_photo' in request.files:
        furnace_photo = request.files.get('furnace_photo',None)
        target = os.path.join(app_root, 'static/furnace_folder')
        form = FurnaceForm(furnace_photo=furnace_photo)
        if form.validate_on_submit():
            picture_furnace_filename = save_picture(furnace_photo,'furnace_folder')
            destination ='/'.join([target,picture_furnace_filename])
            furnace = HeatingEquipment(
                furnace_file = picture_furnace_filename,
                customer_id = customer.id
            )
            db.session.add(furnace)
            db.session.commit()
            return redirect(url_for('main.m_appliances'))
        else:
            form = FurnaceForm(furnace_photo='')
        return render_template('mobile/m_appliances.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)

    if request.method == 'POST' and 'dhw_photo' in request.files:
        dhw_photo = request.files.get('dhw_photo',None)
        target = os.path.join(app_root, 'static/dhw_folder')
        form = DhWForm(dhw_photo=dhw_photo)
        if form.validate_on_submit():
            picture_dhw_filename = save_picture(dhw_photo,'dhw_folder')
            destination ='/'.join([target,picture_dhw_filename])
            dhw = DHW(
                dhw_file = picture_dhw_filename,
                customer_id = customer.id
            )
            db.session.add(dhw)
            db.session.commit()
            return redirect(url_for('main.appliances'))
        else:
            form = DhWForm(dhw_photo='')
        return render_template('mobile/m_appliances.html',form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool)


    if request.method == "POST" and "usage_time_new" in  request.form:
        finalSumbit = request.files.get('finalSumbit')
        correctApplianceBoolian=True
        my_data=Appliance.query.order_by(Appliance.id.desc()).first()
        my_data.usage_time = request.form['usage_time_new']
        my_data.category_appliance = request.form['category']
        db.session.commit()
        flash("Added Appliance", 'success')
        return redirect(url_for('main.m_appliances'))

    else:
        appliance_found_bool=False
        return render_template('mobile/m_appliances.html', form=form,appliance_found=appliance, appliances=appliances,
        basement_appliances=basement_appliances, entertainment_appliances=entertainment_appliances,
        kitchen_appliances=kitchen_appliances, misc_appliances=misc_appliances, customer=customer,appliance_found_bool=appliance_found_bool, furnace=furnace,heating_usage = heating_usage)



#--------------------------------------------
#-dummy app views so app is ready to present-
#--------------------------------------------

#@main.route('/')
@main.route('/m_menu/')
def m_menu():
    return render_template("mobile/m_menu.html")

@main.route('/m_home_menu/')
def m_home_menu():
    return render_template("mobile/m_home_menu.html")

#expanding main home goes to the congrats page 

@main.route('/m_comparisonpage/')
def m_comparisonpage():
    return render_template("mobile/m_comparisonpage.html")

@main.route('/m_effciencyoverview/')
def m_effciencyoverview():
    return render_template("mobile/m_effciencyoverview.html")

@main.route('/m_community_benchmark')
def m_community_benchmark():
    #shoudl get a comunity rank
    rank= 27 
    outof = 256
    #effciency index
    EI = 87
    return render_template("mobile/m_community_benchmark.html", rank=rank, outof=outof, EI=EI)

@main.route('/m_improve_envolope')
def m_impove_envolope(): 
    return render_template("mobile/m_improve_envolope.html")


@main.route('/m_survey')
def m_survey():
    return render_template("mobile/survey.html")

 
@main.route('/m_componentsandupgrades')
def m_componentsandupgrades():
    return render_template("mobile/survey.html")


def m_gas_upgrades():
    potential_rank = 18
    potential_savings = 48.82
    return render_template('mobile/m_gas_upgrades.html', potential_rank=potential_rank, potential_savings=potential_savings)


def m_elec_upgrades():
    return render_template('mobile/m_elec_upgrades.html')

 
def m_home_upgrades():
    return render_template('mobile/m_home_upgrades.html')



@main.route('/m_my_home/')
def m_my_home():
    return render_template('mobile/m_my_home.html')

@main.route('/m_contact_us/')
def m_contact_us():
    return render_template('mobile/m_contact_us.html')

@main.route('/m_util_bill_photo/')
def m_util_bill_photo():
    return render_template('mobile/m_util_bill_photo.html')

@main.route('/m_my_info/')
def m_my_info():
    #this need users electricity, gas and water usage and efficency 
    #will also need comparison data to show you the user can improve 
    #need close by data to then make charts for simple comparison 

    #thses values will be bassed to the histogram for what they do 
    #will need to sort and calculate some info before it is then passed to the html 
    #these values are precentage numbers to say how high the column will be 
    comparison_sorted_electrical = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    comparison_sorted_gas = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    comparison_sorted_water = [10,12,13,15,25,46,51,55,56,45,38,15,5]

    #this is the customer info to put into the histogram. 
    #first number is the percentage hight 
    #second is the percentage left it should be (figure out how to calculate this)
    '''
    these are precentage numbers to calculate where they user lands in comparison to its 13 other users around them
            1%
            7.69230769231%
            15.3846153846%
            23.07692308%
            30.76923077%
            38.46153846%
            46.15384615%
            53.84615384%
            61.53846153%
            69.23076922%
            76.92307691%
            84.6153846%
            92.30769229%
    '''
    user_info_elec = [68, 61.53846153]
    user_info_gas = [24, 25]
    user_info_water = [47, 34]


    #will have to calculate the average usage and then convert that into a precentage hight for the histogram
    average_info_elec = [62,46.15384615]
    average_info_gas = [67,63.53846153]
    average_info_water = [59,69.23076922]

    return render_template('mobile/m_my_info.html', comparison_sorted_electrical=comparison_sorted_electrical,
                                                    comparison_sorted_gas=comparison_sorted_gas,
                                                    comparison_sorted_water=comparison_sorted_water,
                                                    user_info_elec=user_info_elec,
                                                    user_info_gas=user_info_gas,
                                                    user_info_water=user_info_water,
                                                    average_info_elec=average_info_elec,
                                                    average_info_gas=average_info_gas,
                                                    average_info_water=average_info_water)


@main.route('/m_components_menu/')
def m_components_menu():
    return render_template('mobile/m_components_menu.html')

@main.route('/m_savings/')
def m_savings():
    #this will show the savings of the people and where they can save more 

    #thses values will be bassed to the histogram for what they do 
    #will need to sort and calculate some info before it is then passed to the html 
    #these values are precentage numbers to say how high the column will be 
    comparison_bsavings = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    comparison_opsavings = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    

    #this is the customer info to put into the histogram. 
    #first number is the percentage hight 
    #second is the percentage left it should be (figure out how to calculate this)
    '''
    these are precentage numbers to calculate where they user lands in comparison to its 13 other users around them
            1%
            7.69230769231%
            15.3846153846%
            23.07692308%
            30.76923077%
            38.46153846%
            46.15384615%
            53.84615384%
            61.53846153%
            69.23076922%
            76.92307691%
            84.6153846%
            92.30769229%
    '''
    user_bsaving = [60, 55]
    user_opsaving = [24, 25]
    


    #will have to calculate the average usage and then convert that into a precentage hight for the histogram
    potential_bsaving = [75,60]
    potential_opsaving = [67,62.53846153]
    

    return render_template('mobile/m_savings.html', comparison_bsavings=comparison_bsavings,
                                                    comparison_opsavings=comparison_opsavings,
                                                    user_bsaving=user_bsaving,
                                                    user_opsaving=user_opsaving,
                                                    potential_bsaving=potential_bsaving,
                                                    potential_opsaving=potential_opsaving)


@main.route('/m_upgrades/')
def m_upgrades():
    #this will show the savings of the people and where they can save more 

    #thses values will be bassed to the histogram for what they do 
    #will need to sort and calculate some info before it is then passed to the html 
    #these values are precentage numbers to say how high the column will be 
    gas_upgrades = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    envelope_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    electrical_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    

    #this is the customer info to put into the histogram. 
    #first number is the percentage hight 
    #second is the percentage left it should be (figure out how to calculate this)
    '''
    these are precentage numbers to calculate where they user lands in comparison to its 13 other users around them
            1%
            7.69230769231%
            15.3846153846%
            23.07692308%
            30.76923077%
            38.46153846%
            46.15384615%
            53.84615384%
            61.53846153%
            69.23076922%
            76.92307691%
            84.6153846%
            92.30769229%
    '''
    user_gas = [60, 55]
    user_envelope = [24, 25]
    user_electrical = [24, 25]
    


    #will have to calculate the average usage and then convert that into a precentage hight for the histogram
    potential_gas = [75,60]
    potential_envelope = [67,62.53846153]
    potential_electrical = [67,62.53846153]
    

    return render_template('mobile/m_upgrades.html',gas_upgrades=gas_upgrades,
                                                    envelope_upgrades=envelope_upgrades,
                                                    electrical_upgrades=electrical_upgrades,
                                                    user_gas=user_gas,
                                                    user_envelope=user_envelope,
                                                    user_electrical=user_electrical,
                                                    potential_gas=potential_gas,
                                                    potential_envelope=potential_envelope,
                                                    potential_electrical=potential_electrical)



@main.route('/m_coming_soon/')
def m_coming_soon():
    return render_template('mobile/m_coming_soon.html')

@main.route('/m_energy_plan/')
def m_energy_plan():
    return render_template('mobile/m_energy_plan.html')

@main.route('/m_plan_comparison/')
def m_plan_comparison():
    return render_template('mobile/m_plan_comparison.html')

@main.route('/m_gas_upgrades/')
def m_gas_upgrades():
    gas_upgrades = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    envelope_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    electrical_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    

    #this is the customer info to put into the histogram. 
    #first number is the percentage hight 
    #second is the percentage left it should be (figure out how to calculate this)
    '''
    these are precentage numbers to calculate where they user lands in comparison to its 13 other users around them
            1%
            7.69230769231%
            15.3846153846%
            23.07692308%
            30.76923077%
            38.46153846%
            46.15384615%
            53.84615384%
            61.53846153%
            69.23076922%
            76.92307691%
            84.6153846%
            92.30769229%
    '''
    user_gas = [60, 55]
    user_envelope = [24, 25]
    user_electrical = [24, 25]
    


    #will have to calculate the average usage and then convert that into a precentage hight for the histogram
    potential_gas = [75,60]
    potential_envelope = [67,62.53846153]
    potential_electrical = [67,62.53846153]
    

    return render_template('mobile/m_gas_upgrades.html',gas_upgrades=gas_upgrades,
                                                    envelope_upgrades=envelope_upgrades,
                                                    electrical_upgrades=electrical_upgrades,
                                                    user_gas=user_gas,
                                                    user_envelope=user_envelope,
                                                    user_electrical=user_electrical,
                                                    potential_gas=potential_gas,
                                                    potential_envelope=potential_envelope,
                                                    potential_electrical=potential_electrical)

@main.route('/m_furnace_comparison/', methods=["GET","POST"])
def m_furnace_comparison():
    #This function will get top 2 furnaces and then 3 runners up.
    # it will show details of the top 5 furnaces then the user will click one
    #once user clicks a buton it will bring them to a more comparison page where they can see details about upgrading furnace
    #these 2 functions will repleat for every appliace/aspect of a house. 



    #important values for a furnace at first glance
        #name
        #efficeiency
        #monthley cost
    
    user_furnace = ["York", 65, 7.31]
    #     [ name , efficiency, monthly price, inital cost]
    top1 = ["Lennox 5000", 86, 5.96, 196.59]
    top2 = ["Napoleon 9700", 84, 6.55, 230.55]
    if request.method =='POST':
        if request.form['top'] == 'top1':
            return render_template('mobile/m_furance_comparison_details.html')

    elif request.method == 'GET':
        return render_template('mobile/m_furnace_comparison.html', user_furnace=user_furnace,
                                                                    top1=top1,
                                                                    top2=top2)

import ast
@main.route('/m_furnace_comparison_details/',methods=["GET"])
def m_furnace_comparison_details():
    #get more details form the database when it is ready
    furnaces = request.args.get("comp")
    fern = ast.literal_eval(furnaces)
    user_furnace=fern[0] 
    comp_furnace=fern[1]
    # These lists are from the last function they are formatted as 
    # User_furnace=['name', efficiency, monthly cost]
    # to compare we will need more comparison stats such as 
    #   inital cost
    #   monthly cost 
    #   yearly cost
    #   lifespan cost
    #   potential savings. 
    #   need efficient value for the chart
    #   calculate the position on the chart

    # these values are for testing only will need to calculate the full details 
    # simpler to just have a extra list of 2 values to place the 2 bars on the graph

    #user_furnace = ["York", 65, 7.31]
    user_efficiency = [45, 55]
    user_month_cost = [60, 55]
    user_init_cost = [60, 40]
    #              [ name , efficiency, monthly price, inital cost]
    #comp_furnace = ["Lennox 5000", 86, 5.96, 196.59]
    comp_efficiency = [60, 65]
    comp_month_cost = [35,35]
    comp_init_cost = [50, 80]

    savings = round(user_furnace[2] - comp_furnace[2], 2)

    #these are values for efficient furnaces to compare for the graphs
    efficient_furnaces = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    #efficient_av = np.mean(efficient_furnaces )
    efficient_av = 65
    monthly_cost = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    #monthly_cost_av = np.mean( monthly_cost) this is a percentage would need to multiply it by the normal
    monthly_cost_av = 6.70
    init_cost = [4,12,20,33,46,50,60,66,40,30,20,15,10] 
    #init_cost_av = np.mean(init_cost)
    init_cost_av = 400.00

    # this has to be calculated 
    potential_savings = 196.95

    return render_template('mobile/m_furnace_comparison_details.html',user_furnace=user_furnace,
                                                                        user_efficiency=user_efficiency,
                                                                        user_init_cost=user_init_cost,
                                                                        user_month_cost=user_month_cost,
                                                                        comp_efficiency = comp_efficiency,
                                                                        comp_furnace=comp_furnace,
                                                                        comp_month_cost=comp_month_cost,
                                                                        comp_init_cost = comp_init_cost,
                                                                        monthly_cost=monthly_cost,
                                                                        monthly_cost_av=monthly_cost_av,
                                                                        efficient_furnaces=efficient_furnaces,
                                                                        efficient_av = efficient_av,
                                                                        init_cost = init_cost,
                                                                        init_cost_av = init_cost_av,
                                                                        potential_savings=potential_savings,
                                                                        savings=savings
                                                                        )

@main.route('/m_smartthermostat_comparison/', methods=["GET","POST"])
def m_smartthermostat_comparison():
    #This function will get top 2 furnaces and then 3 runners up.
    # it will show details of the top 5 furnaces then the user will click one
    #once user clicks a buton it will bring them to a more comparison page where they can see details about upgrading furnace
    #these 2 functions will repleat for every appliace/aspect of a house. 



    #important values for a furnace at first glance
        #name
        #efficeiency
        #monthley cost
    
    user_thermostat = ["old", 65, 7.31]
    #     [ name , efficiency, monthly price, inital cost]
    top1 = ["Eccobee", 86, 5.96, 196.59]
    top2 = ["Nest", 84, 6.55, 230.55]
    if request.method =='POST':
        if request.form['top'] == 'top1':
            return render_template('mobile/m_furance_comparison_details.html')

    elif request.method == 'GET':
        return render_template('mobile/m_smartthermostat_comparison.html', user_thermostat=user_thermostat,
                                                                    top1=top1,
                                                                    top2=top2)

@main.route('/m_smartthermostat_comparison_details/',methods=["GET"])
def m_smartthermostat_comparison_details():
    #get more details form the database when it is ready
    furnaces = request.args.get("comp")
    fern = ast.literal_eval(furnaces)
    user_furnace=fern[0] 
    comp_furnace=fern[1]
    
    # These lists are from the last function they are formatted as 
    # User_furnace=['name', efficiency, monthly cost]
    # to compare we will need more comparison stats such as 
    #   inital cost
    #   monthly cost 
    #   yearly cost
    #   lifespan cost
    #   potential savings. 
    #   need efficient value for the chart
    #   calculate the position on the chart

    # these values are for testing only will need to calculate the full details 
    # simpler to just have a extra list of 2 values to place the 2 bars on the graph

    #user_furnace = ["York", 65, 7.31]
    user_efficiency = [45, 55]
    user_month_cost = [60, 55]
    user_init_cost = [60, 40]
    #              [ name , efficiency, monthly price, inital cost]
    #comp_furnace = ["Lennox 5000", 86, 5.96, 196.59]
    comp_efficiency = [60, 65]
    comp_month_cost = [35,35]
    comp_init_cost = [50, 80]

    savings = round(user_furnace[2] - comp_furnace[2], 2)

    #these are values for efficient furnaces to compare for the graphs
    efficient_thermostat = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    #efficient_av = np.mean(efficient_furnaces )
    efficient_av = 65
    monthly_cost = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    #monthly_cost_av = np.mean( monthly_cost) this is a percentage would need to multiply it by the normal
    monthly_cost_av = 6.70
    init_cost = [4,12,20,33,46,50,60,66,40,30,20,15,10] 
    #init_cost_av = np.mean(init_cost)
    init_cost_av = 400.00

    # this has to be calculated 
    potential_savings = 196.95

    return render_template('mobile/m_smartthermostat_comparison_details.html',user_furnace=user_furnace,
                                                                        user_efficiency=user_efficiency,
                                                                        user_init_cost=user_init_cost,
                                                                        user_month_cost=user_month_cost,
                                                                        comp_efficiency = comp_efficiency,
                                                                        comp_furnace=comp_furnace,
                                                                        comp_month_cost=comp_month_cost,
                                                                        comp_init_cost = comp_init_cost,
                                                                        monthly_cost=monthly_cost,
                                                                        monthly_cost_av=monthly_cost_av,
                                                                        efficient_thermostat=efficient_thermostat,
                                                                        efficient_av = efficient_av,
                                                                        init_cost = init_cost,
                                                                        init_cost_av = init_cost_av,
                                                                        potential_savings=potential_savings,
                                                                        savings=savings
                                                                        )
    

@main.route('/m_house_upgrades/')
def m_house_upgrades():
    gas_upgrades = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    envelope_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    electrical_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    

    #this is the customer info to put into the histogram. 
    #first number is the percentage hight 
    #second is the percentage left it should be (figure out how to calculate this)
    '''
    these are precentage numbers to calculate where they user lands in comparison to its 13 other users around them
            1%
            7.69230769231%
            15.3846153846%
            23.07692308%
            30.76923077%
            38.46153846%
            46.15384615%
            53.84615384%
            61.53846153%
            69.23076922%
            76.92307691%
            84.6153846%
            92.30769229%
    '''
    user_gas = [60, 55]
    user_envelope = [24, 25]
    user_electrical = [24, 25]
    


    #will have to calculate the average usage and then convert that into a precentage hight for the histogram
    potential_gas = [75,60]
    potential_envelope = [67,62.53846153]
    potential_electrical = [67,62.53846153]
    

    return render_template('mobile/m_house_upgrades.html',gas_upgrades=gas_upgrades,
                                                    envelope_upgrades=envelope_upgrades,
                                                    electrical_upgrades=electrical_upgrades,
                                                    user_gas=user_gas,
                                                    user_envelope=user_envelope,
                                                    user_electrical=user_electrical,
                                                    potential_gas=potential_gas,
                                                    potential_envelope=potential_envelope,
                                                    potential_electrical=potential_electrical) 


@main.route('/m_windows_comparison/', methods=["GET","POST"])
def m_windows_comparison():
    #This function will get top 2 furnaces and then 3 runners up.
    # it will show details of the top 5 furnaces then the user will click one
    #once user clicks a buton it will bring them to a more comparison page where they can see details about upgrading furnace
    #these 2 functions will repleat for every appliace/aspect of a house. 



    #how to compare windows? this is not final same as furnace
    
    user_furnace = ["York", 65, 7.31]
    #     [ name , efficiency, monthly price, inital cost]
    top1 = ["Anderson Windows", 86, 5.96, 196.59]
    top2 = ["Jeld-Wen", 84, 6.55, 230.55]
    if request.method =='POST':
        if request.form['top'] == 'top1':
            return render_template('mobile/m_windows_comparison_details.html')

    elif request.method == 'GET':
        return render_template('mobile/m_windows_comparison.html', user_furnace=user_furnace,
                                                                    top1=top1,
                                                                    top2=top2)
    

@main.route('/m_windows_comparison_details/',methods=["GET"])
def m_windows_comparison_details():
    #get more details form the database when it is ready
    furnaces = request.args.get("comp")
    fern = ast.literal_eval(furnaces)
    user_furnace=fern[0] 
    comp_furnace=fern[1]
    
    # These lists are from the last function they are formatted as 
    # User_furnace=['name', efficiency, monthly cost]
    # to compare we will need more comparison stats such as 
    #   inital cost
    #   monthly cost 
    #   yearly cost
    #   lifespan cost
    #   potential savings. 
    #   need efficient value for the chart
    #   calculate the position on the chart

    # these values are for testing only will need to calculate the full details 
    # simpler to just have a extra list of 2 values to place the 2 bars on the graph

    #user_furnace = ["York", 65, 7.31]
    user_efficiency = [45, 55]
    user_month_cost = [60, 55]
    user_init_cost = [60, 40]
    #              [ name , efficiency, monthly price, inital cost]
    #comp_furnace = ["Lennox 5000", 86, 5.96, 196.59]
    comp_efficiency = [60, 65]
    comp_month_cost = [35,35]
    comp_init_cost = [50, 80]

    savings = round(user_furnace[2] - comp_furnace[2], 2)

    #these are values for efficient furnaces to compare for the graphs
    efficient_thermostat = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    #efficient_av = np.mean(efficient_furnaces )
    efficient_av = 65
    monthly_cost = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    #monthly_cost_av = np.mean( monthly_cost) this is a percentage would need to multiply it by the normal
    monthly_cost_av = 6.70
    init_cost = [4,12,20,33,46,50,60,66,40,30,20,15,10] 
    #init_cost_av = np.mean(init_cost)
    init_cost_av = 400.00

    # this has to be calculated 
    potential_savings = 196.95

    return render_template('mobile/m_windows_comparison_details.html',user_furnace=user_furnace,
                                                                        user_efficiency=user_efficiency,
                                                                        user_init_cost=user_init_cost,
                                                                        user_month_cost=user_month_cost,
                                                                        comp_efficiency = comp_efficiency,
                                                                        comp_furnace=comp_furnace,
                                                                        comp_month_cost=comp_month_cost,
                                                                        comp_init_cost = comp_init_cost,
                                                                        monthly_cost=monthly_cost,
                                                                        monthly_cost_av=monthly_cost_av,
                                                                        efficient_thermostat=efficient_thermostat,
                                                                        efficient_av = efficient_av,
                                                                        init_cost = init_cost,
                                                                        init_cost_av = init_cost_av,
                                                                        potential_savings=potential_savings,
                                                                        savings=savings
                                                                        )
@main.route('/m_elec_upgrades/')
def m_elec_upgrades():
    gas_upgrades = [10,23,30,33,40,50,60,66,56,40,39,34,29]
    envelope_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    electrical_upgrades = [4,12,20,33,46,50,60,66,40,30,20,15,10]
    

    #this is the customer info to put into the histogram. 
    #first number is the percentage hight 
    #second is the percentage left it should be (figure out how to calculate this)
    '''
    these are precentage numbers to calculate where they user lands in comparison to its 13 other users around them
            1%
            7.69230769231%
            15.3846153846%
            23.07692308%
            30.76923077%
            38.46153846%
            46.15384615%
            53.84615384%
            61.53846153%
            69.23076922%
            76.92307691%
            84.6153846%
            92.30769229%
    '''
    user_gas = [60, 55]
    user_envelope = [24, 25]
    user_electrical = [24, 25]
    


    #will have to calculate the average usage and then convert that into a precentage hight for the histogram
    potential_gas = [75,60]
    potential_envelope = [67,62.53846153]
    potential_electrical = [67,62.53846153]
    

    return render_template('mobile/m_elec_upgrades.html',gas_upgrades=gas_upgrades,
                                                    envelope_upgrades=envelope_upgrades,
                                                    electrical_upgrades=electrical_upgrades,
                                                    user_gas=user_gas,
                                                    user_envelope=user_envelope,
                                                    user_electrical=user_electrical,
                                                    potential_gas=potential_gas,
                                                    potential_envelope=potential_envelope,
                                                    potential_electrical=potential_electrical)
    
