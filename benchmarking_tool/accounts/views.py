import os
from pathlib import Path
import secrets
from flask import Blueprint,request,render_template,redirect,flash,url_for,current_app
from flask_login import login_user, current_user, logout_user, login_required
from ..forms import *
from ..helper import *
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from benchmarking_tool import app
from benchmarking_tool.methods import *
from benchmarking_tool.decorators import *
from dotenv import load_dotenv
from sqlalchemy import or_
from benchmarking_tool.image_reckognition.bill_detection import *
from benchmarking_tool.image_reckognition.bill_detection import detect_electrical_bill
from benchmarking_tool.methods import *
from benchmarking_tool.methods import *
from difflib import get_close_matches
import re
load_dotenv()
from ..forms import *

accounts = Blueprint('accounts',__name__,template_folder='templates', url_prefix='/accounts')

bcrypt = Bcrypt()
mail = Mail()
app_root = Path(__file__).parents[1]

@accounts.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.overview'))
    if request.method == "POST":
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        # location = request.form['location']
        # gas_bill = request.files['gas_photo_bill']
        electrical_bill = request.files['electrical_photo_bill']
        # gas_address = request.form['gas_address']
        electrical_address = request.form['electrical_address']
        form = RegistrationForm(
            email=email,
            phone_numer=phone_number,
            password=password,
            confirm_password=confirm_password,
            # location = location,
            # gas_bill = gas_address,
            electrical_address = electrical_address
        )
        if form.validate_on_submit():
            possible_addresses = []
            possible_cities = []
            # use text reckognition to pull text off bill initially and saving photos
            # if gas_bill:
            #     gas_picture = save_picture(gas_bill,"gas_folder")
            #     gas_bill_reckognize = detectText(gas_bill)





            if electrical_bill:
                electrical_picture = save_picture(electrical_bill,"electrical_folder")
                #first detect text on the bill itself
                target = os.path.join(app_root, 'static/electrical_folder')
                destination = '/'.join([target, electrical_picture])
                electrical_bill_reckognize = detectText(destination)
                #now find a company to apply the proper method
                electrcial_company = detect_company(electrical_bill_reckognize)
                #now that company is found, apply method to return values for detecting bill
                #check if detection returns error, if so rename variable to specifify error found

                if electrcial_company == 'error':
                    flash('Your bill was not reckognized, please take another photo', 'danger')
                #if no error, proceed


                else:
                    #find city via method in bill detection
                    full_detection = detect_electrical_bill(electrcial_company,electrical_bill_reckognize)
                    #find city via method in bill detection
                    city_found = full_detection[3]
                    city_query = City.query.all()
                    for row in city_query:
                        possible_cities = get_close_matches(city_found, [row.city], 1, 0.5) + possible_cities


                    #use matching functions in methods to match approximate city on bill, it should have at least 80% match to succeed
                    city_match = closeMatches(city_found,possible_cities)
                    if len(city_match) == 0:
                        flash('')
                    #now that we have a city matched, find the address found and match that as well
                    customer_city_query = db.session.query(Customer).filter(Customer.city == 'sedgewick').all()
                    #using searching algorithm to find possible address and clossest address match
                    for row in customer_city_query:
                        # we are first finding relative close matches
                        possible_addresses = get_close_matches(full_detection[1], [row.address], 1, 0.6) + possible_addresses
                    #we then find absolute 90% match of the address, as we have already found the city, this will return absolute closest match
                    print(full_detection[1])
                    print(possible_addresses)
                    address_found = get_close_matches(full_detection[1],possible_addresses,1,0.65)
                    #we check to see if address was not found with a close match
                    if len(address_found) == 0:
                        flash('Your address was not found in our system', 'danger')
                    else:
                    # since difflib returns list, we need to take address out of the list

                        address_found = address_found[0]

                        electrical_address = address_found
                customer = Customer.query.filter((Customer.address == electrical_address)).first()
                role = Role.query.filter_by(name='User').first()
                if (customer == None):
                    flash('We found your address, but it was not in the database', 'danger')
                else:
                    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                    user = User(
                        email=form.email.data,
                        phone_number=form.phone_number.data,
                        password=hashed_password,
                        role_id=role.id)
                    electrical_usage = ElectricalUsage(consumption = float(full_detection[0][0]), cost = float(full_detection[2]),electrical_file = electrical_picture,customer=customer)

                    user.customer = customer
                    db.session.add(user)
                    db.session.add(electrical_usage)
                    db.session.commit()
                    login_user(user)
                    return redirect(url_for('main.overview'))
    else:
        form = RegistrationForm(
            email="",
            first_name="",
            last_name="",
            password="",
            confirm_password="",
            # gas_bill = "",
            electrical_bill = ""
        )
    return render_template('register.html', title='Register', form=form, last_updated=dir_last_updated())

# Route for the user to login
@accounts.route('/login', methods=['GET', 'POST'])
def login():
    print("in login")
    if current_user.is_authenticated:
        return redirect(url_for('main.overview'))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        form = LoginForm(
            email=email,
            password=password
        )
        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            role_user = user.role.name
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                next_page = request.args.get('next')
                flash(f"Welcome {email}", 'success')
                if role_user == 'User':
                    customer = user.customer
                    survey = customer.survey
                    if survey == None:
                        return redirect(url_for('main.customer_info'))
                    else:
                        return redirect(next_page) if next_page else redirect(url_for('main.overview'))
                else:
                    return redirect(next_page) if next_page else redirect(url_for('main.overview'))
            else:
                flash(
                    f"Login Unsuccessful,Please check your email and Password!", 'danger')
                return redirect(url_for('accounts.login'))
    else:
        form = LoginForm(email="")
    return render_template('login.html', title='Login', form=form,last_updated=dir_last_updated())

# route for the user to logout
@accounts.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('accounts.login'))

# route for the user to request a new password
@accounts.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.overview'))
    if request.method == 'POST':
        email = request.form["email"]
        form = RequestResetForm(email=email)
        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            send_reset_email(user)
            flash(
                'An email has been sent with instructions to reset your password', 'info')
            return redirect(url_for('accounts.login'))
    else:
        form = RequestResetForm(email='')
    return render_template('reset_request.html', title='Reset Password', form=form)

# route for the user to reset his password
@accounts.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.overview'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('accounts.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f"Thank You. Your Password has been updated.You can now log in", 'success')
        return redirect(url_for('accounts.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

# route for updating the user account
@accounts.route('/update_user', methods=['GET', 'POST'])
@survey_required
@login_required
def update_user():
    if request.method == 'POST':
        email = request.form["email"]
        current_password = request.form['current_password']
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        form = UpdateAccountForm(email=email,current_password=current_password,
                new_password=new_password,confirm_password=confirm_password)
        if form.validate_on_submit():
            if bcrypt.check_password_hash(current_user.password, current_password):
                hashed_password = bcrypt.generate_password_hash(
                    new_password).decode('utf-8')
                current_user.email = form.email.data
                current_user.password = hashed_password
                db.session.commit()
                flash(f"Thank You. Your Account has been updated.", 'success')
                return redirect(url_for('main.overview'))
    else:
        form = UpdateAccountForm(email=current_user.email, current_password="",
            new_password="",confirm_password="")
    return render_template("user_update.html",title='Update Account', form=form,last_updated=dir_last_updated())


# function to send email
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='server@pollen.one',
                  recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link :
{url_for('accounts.reset_token',token=token,_external=True)}
    If you didn't make the request, please ignore this email
    '''
    mail.send(msg)


def save_picture(form_picture,location):
	random_hex = secrets.token_hex(8)
	file_extension = os.path.splitext(form_picture.filename)[1]
	picture_filename = random_hex + file_extension
	picture_path = os.path.join(app_root,'static/'+location,picture_filename)
	form_picture.save(picture_path)
	return picture_filename

@accounts.route('/check_address',methods=['POST'])
def check_address():
    if 'gas_photo_bill' in request.files:
        picture = request.files['gas_photo_bill']
    if 'electrical_photo_bill' in request.files:
        picture = request.files['electrical_photo_bill']
    image = save_picture(picture,'temp_folder')
    address = detect_address(image,'temp_folder')
    if (address == None):
        return {'success': False,'address': None}
    else:
        return {'success': True,'address': address[0]}


@accounts.route('/sw.js', methods=['GET'])
def sw():
    return current_app.send_static_file('sw.js')

@accounts.route('/offline.html', methods=['GET'])
def offline():
    return render_template('offline.html', title='offline', last_updated=dir_last_updated())


