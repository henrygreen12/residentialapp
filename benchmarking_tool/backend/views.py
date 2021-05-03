import math
from sqlalchemy import desc
from flask import Blueprint,render_template,request,redirect,url_for,flash, abort
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
from sqlalchemy import and_
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

backend = Blueprint('backend',__name__,template_folder='templates', url_prefix='/backend')
app_root = Path(__file__).parents[1]

@backend.route('/testadmin' , methods = ['GET', 'POST'])
@login_required
def testadmin():
    users = db.session.query(User).all()
    if(current_user.is_authenticated and current_user.is_admin()):
        return render_template('admintest.html', users = users)
    else:
        abort(403)

@backend.route('/admincustomer/<int:id>' , methods = ['GET', 'POST'])
@login_required
def admincustomer(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        customer = Customer.query.filter_by(user_id=id).first()
        user = User.query.filter_by(id = id).first()
        appliances = Appliance.query.order_by(Appliance.id).filter(Appliance.customer_id == customer.id).all()
        heating_equipments = HeatingEquipment.query.order_by(HeatingEquipment.id).filter(HeatingEquipment.customer_id == customer.id).all()
        dhws = DHW.query.order_by(DHW.id).filter(DHW.customer_id == customer.id).all()
        return render_template('adminoverview.html',appliances = appliances, customer = customer, user = user, heating_equipments = heating_equipments, dhws = dhws)

    else:
        abort(403)

@backend.route('/adminbills/<int:id>' , methods = ['GET', 'POST'])
@login_required
def adminbills(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        customer = Customer.query.filter_by(user_id=id).first()
        user = User.query.filter_by(id = id).first()
        appliances = Appliance.query.order_by(-Appliance.id).filter(Appliance.customer_id == customer.id).all()
        electrical_usages = ElectricalUsage.query.filter_by(customer_id = customer.id).all()
        gas_usages = GasUsage.query.filter_by(customer_id = customer.id).all()
        water_usages = WaterUsage.query.filter_by(customer_id = customer.id).all()
        return render_template('adminbills.html',appliances = appliances, customer = customer, user = user, electrical_usages = electrical_usages, gas_usages = gas_usages, water_usages = water_usages)

    else:
        abort(403)


@backend.route('/messages/<int:id>')
@login_required
def messages(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        customer = Customer.query.filter_by(user_id=id).first()
        messages = Messages.query.filter_by(customer_id=customer.id, recipient = 'Admin')
        return render_template('adminmessages.html', messages=messages, user = user)
    else:
        abort(403)


@backend.route('/send_message/<int:id>', methods = ['GET', 'POST'])
@login_required
def send_message(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        form = MessageForm()
        customer = Customer.query.filter_by(user_id=id).first()
        if form.validate_on_submit():
            msg = Messages(customer_id=customer.id,
                          body =form.message.data, recipient = 'Customer')
            db.session.add(msg)
            db.session.commit()
            flash(('Your message has been sent.'))
            return redirect(url_for('backend.testadmin'))
        return render_template('adminsendmessage.html', form=form)

    else:
        abort(403)


@backend.route('/recommendations/<int:id>', methods = ['GET', 'POST'])
@login_required
def recommendations(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        customer = Customer.query.filter_by(user_id=id).first()
        appliances = RecommendedAppliance.query.filter_by(customer_id=customer.id).all()
        heatingequipments = RecommendedHeatingEquipment.query.filter_by(customer_id=customer.id).all()
        dhws = RecommendedDHW.query.filter_by(customer_id=customer.id).all()
        return render_template('recommendations.html', customer=customer, user = user, appliances = appliances, heatingequipments = heatingequipments, dhws = dhws)
    else:
        abort(403)


@backend.route('/recommendAppliance/<int:id>', methods = ['GET', 'POST'])
@login_required
def recommendAppliance(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        customer = Customer.query.filter_by(user_id=id).first()
        form = RecommendApplianceForm()

        if request.method == 'POST':
            appliance_name = request.form["appliance_name"]
            appliance_type = request.form["appliance_type"]
            rated_power = request.form["rated_power"]
            reason = request.form["reason"]
            new_recommendation = RecommendedAppliance(appliance_name = appliance_name, appliance_type = appliance_type, rated_power = rated_power, reason = reason, customer_id = customer.id)
            try:
                db.session.add(new_recommendation)
                db.session.commit()
                return redirect(url_for('backend.recommendations', id = user.id))
            except:
                return "There was a problem adding the client to the system"
        else:
            return render_template('recommendappliance.html', customer=customer, user = user,  form = form)
    else:
        abort(403)

@backend.route('/recommendHeatingEquipment/<int:id>', methods = ['GET', 'POST'])
@login_required
def recommendHeatingEquipment(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        customer = Customer.query.filter_by(user_id=id).first()
        form = RecommendHeatingEquipmentForm()
        
        if request.method == 'POST':
            btu_input = request.form["btu_input"]
            btu_output = request.form["btu_output"]
            efficiency = request.form["efficiency"]
            type_heating = request.form["type_heating"]
            name_plate = request.form["name_plate"]
            reason = request.form["reason"]
            new_recommendation = RecommendedAppliance(btu_input = btu_input, btu_output = btu_output, efficiency = efficiency, type_heating = type_heating, name_plate = name_plate, reason = reason, customer_id = customer.id)
            try:
                db.session.add(new_recommendation)
                db.session.commit()
                return redirect("url_for('backend.recommendations', id = user.id)")
            except:
                return "There was a problem adding the client to the system"
        else:
            return render_template('recommendHeatingEquipment.html', customer=customer, user = user,  form = form)
    else:
        abort(403)

@backend.route('/recommendDHW/<int:id>', methods = ['GET', 'POST'])
@login_required
def recommendDHW(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        customer = Customer.query.filter_by(user_id=id).first()
        form = RecommendDHWForm()
        
        if request.method == 'POST':
            btu_output = request.form["btu_output"]
            volume = request.form["volume"]
            name_plate = request.form["name_plate"]
            reason = request.form["reason"]
            new_recommendation = RecommendedAppliance( form = form, btu_output = btu_output, volume = volume, name_plate = name_plate, reason = reason, customer_id = customer.id)
            try:
                db.session.add(new_recommendation)
                db.session.commit()
                return redirect("url_for('backend.recommendations', id = user.id)")
            except:
                return "There was a problem adding the client to the system"
        else:
            return render_template('recommendDHW.html', customer=customer, user = user)
    else:
        abort(403)


@backend.route('/furnacecsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def furnacecsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Efficiency"
        title = "Furnaces"
        if request.method == 'POST':
            efficiency = request.form["searchbar"]
            float(efficiency)    
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Heating & Cooling/ENERGY_STAR_Certified_Furnaces.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            df["EfficiencyAFUE"] =  pd.to_numeric(df["EfficiencyAFUE"], downcast="float")
            df.query('EfficiencyAFUE > @efficiency', inplace = True)
            df = df.sort_values(by='EfficiencyAFUE', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Heating & Cooling/ENERGY_STAR_Certified_Furnaces.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
       
    else:
        abort(403)


@backend.route('/roofcsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def roofcsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Initial Emissivity"
        title = "Roofs"
        if request.method == 'POST':
            initialEmissivity = request.form["searchbar"] 
            float(initialEmissivity)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Building Products/ENERGY_STAR_Certified_Roof_Products.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            df["InitialEmissivity"] =  pd.to_numeric(df["InitialEmissivity"], downcast="float")

            df.query('InitialEmissivity > @initialEmissivity', inplace = True)
            df = df.sort_values(by='InitialEmissivity', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Building Products/ENERGY_STAR_Certified_Roof_Products.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)

@backend.route('/windowcsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def windowcsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "U-Factor Min"
        title = "Windows"
        if request.method == 'POST':
            ufactormin = request.form["searchbar"] 
            float(ufactormin)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Building Products/ME_Windows.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            print(df.columns)
            df["MinUFactor"] =  pd.to_numeric(df["MinUFactor"], downcast="float")
            df.query('MinUFactor > @ufactormin', inplace = True)
            df = df.sort_values(by='MinUFactor', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Building Products/ME_Windows.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)



@backend.route('/waterheatercsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def waterheatercsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Electric Usage at 125°F"
        title = "Water Heaters"
        if request.method == 'POST':
            electricalusage = request.form["searchbar"] 
            float(electricalusage)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Water Heater/ENERGY_STAR_Certified_Water_Heaters.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            df.columns =[column.replace("°", "") for column in df.columns]
            print(df.columns)
            df["ElectricUsageat125FoutlettempkWhyr"] =  pd.to_numeric(df["ElectricUsageat125FoutlettempkWhyr"], downcast="float")
            df.query('ElectricUsageat125FoutlettempkWhyr > @electricalusage', inplace = True)
            df = df.sort_values(by='ElectricUsageat125FoutlettempkWhyr', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Water Heater/ENERGY_STAR_Certified_Water_Heaters.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)


@backend.route('/lightbulbscsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def lightbulbscsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Efficacy"
        title = "Light Bulbs"
        if request.method == 'POST':
            efficacy = request.form["searchbar"] 
            float(efficacy)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Lighting & Fans/ENERGY_STAR_Certified__Light_Bulbs_Version_2.0.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            print(df.columns)
            df["Efficacylumenswatt"] =  pd.to_numeric(df["Efficacylumenswatt"], downcast="float")
            df.query('Efficacylumenswatt > @efficacy', inplace = True)
            df = df.sort_values(by='Efficacylumenswatt', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Lighting & Fans/ENERGY_STAR_Certified__Light_Bulbs_Version_2.0.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)

@backend.route('/lightfixturescsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def lightfixturescsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Efficacy"
        title = "Light Fixtures"
        if request.method == 'POST':
            efficacy = request.form["searchbar"] 
            float(efficacy)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Lighting & Fans/ENERGY_STAR_Certified_Light_Fixtures.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            print(df.columns)
            df["EnergyEfficiencyMeasuredattheSourcelumensWatt"] =  pd.to_numeric(df["EnergyEfficiencyMeasuredattheSourcelumensWatt"], downcast="float")
            df.query('EnergyEfficiencyMeasuredattheSourcelumensWatt > @efficacy', inplace = True)
            df = df.sort_values(by='EnergyEfficiencyMeasuredattheSourcelumensWatt', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Lighting & Fans/ENERGY_STAR_Certified_Light_Fixtures.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)

@backend.route('/ceilinfanscsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def ceilinfanscsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Efficacy"
        title = "Ceiling Fan"
        if request.method == 'POST':
            efficacy = request.form["searchbar"] 
            float(efficacy)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Lighting & Fans/ENERGY_STAR_Certified_Ceiling_Fans.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            print(df.columns)
            df["CeilingFanEfficiencyCFMW"] =  pd.to_numeric(df["CeilingFanEfficiencyCFMW"], downcast="float")
            df.query('CeilingFanEfficiencyCFMW > @efficacy', inplace = True)
            df = df.sort_values(by='CeilingFanEfficiencyCFMW', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Lighting & Fans/ENERGY_STAR_Certified_Ceiling_Fans.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)

@backend.route('/fridgecsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def fridgecsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Annual Energy Use"
        title = "Refrigerators"
        if request.method == 'POST':
            anualenergyuse = request.form["searchbar"] 
            float(anualenergyuse)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Appliances/ENERGY_STAR_Certified_Residential_Refrigerators.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            print(df.columns)
            df["AnnualEnergyUsekWhyr"] =  pd.to_numeric(df["AnnualEnergyUsekWhyr"], downcast="float")
            df.query('AnnualEnergyUsekWhyr > @anualenergyuse', inplace = True)
            df = df.sort_values(by='AnnualEnergyUsekWhyr', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Appliances/ENERGY_STAR_Certified_Residential_Refrigerators.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)


@backend.route('/washingcsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def washingcsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Annual Energy Use"
        title = "Washing Machine"
        if request.method == 'POST':
            anualenergyuse = request.form["searchbar"] 
            float(anualenergyuse)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Appliances/ENERGY_STAR_Certified_Residential_Clothes_Washers.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            print(df.columns)
            df["AnnualEnergyUsekWhyr"] =  pd.to_numeric(df["AnnualEnergyUsekWhyr"], downcast="float")
            df.query('AnnualEnergyUsekWhyr > @anualenergyuse', inplace = True)
            df = df.sort_values(by='AnnualEnergyUsekWhyr', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Appliances/ENERGY_STAR_Certified_Residential_Clothes_Washers.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)


@backend.route('/dryercsv/<int:id>', methods = ['GET', 'POST'])
@login_required
def dryercsv(id):
    if(current_user.is_authenticated and current_user.is_admin()):
        user = User.query.filter_by(id = id).first()
        search_bar = "Annual Energy Use"
        title = "Dryer"
        if request.method == 'POST':
            anualenergyuse = request.form["searchbar"] 
            float(anualenergyuse)
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Appliances/ENERGY_STAR_Certified_Residential_Clothes_Washers.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            df.columns =[column.replace("(", "") for column in df.columns]
            df.columns =[column.replace(")", "") for column in df.columns]
            df.columns =[column.replace("-", "") for column in df.columns]
            df.columns =[column.replace("/", "") for column in df.columns]
            df.columns =[column.replace(".", "") for column in df.columns]
            df.columns =[column.replace(" ", "") for column in df.columns]
            print(df.columns)
            df["AnnualEnergyUsekWhyr"] =  pd.to_numeric(df["AnnualEnergyUsekWhyr"], downcast="float")
            df.query('AnnualEnergyUsekWhyr > @anualenergyuse', inplace = True)
            df = df.sort_values(by='AnnualEnergyUsekWhyr', ascending=False)
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user, search_bar = search_bar)
        else:
            if sys.version_info[0] < 3: 
                from StringIO import StringIO # Python 2.x
            else:
                from io import StringIO # Python 3.x

            client = boto3.client('s3', aws_access_key_id='AKIAJTBSYYO6TBXCX6EA',
                    aws_secret_access_key='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')

            bucket_name = 'energystarapi'

            object_key = 'Appliances/ENERGY_STAR_Certified_Residential_Clothes_Washers.csv'
            csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
            body = csv_obj['Body']
            csv_string = body.read().decode('utf-8')

            df = pd.read_csv(StringIO(csv_string))
            return render_template('testcsv.html',title = title, tables=[df.to_html(classes='data')],titles=df.columns.values,user = user,search_bar = search_bar)
       
    else:
        abort(403)

