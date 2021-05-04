import math
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user, current_user, logout_user, login_required
from models import *
from flask_bcrypt import Bcrypt
import requests
from helper import *
from benchmarking_tool.forms import *
from benchmarking_tool.decorators import *
from benchmarking_tool.methods import *
import secrets
from PIL import Image
from difflib import get_close_matches


fitters = Blueprint('fitters',__name__,template_folder='templates', url_prefix='/fitters')

bcrypt = Bcrypt()


@fitters.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('fitters.home'))
    if request.method == "POST":
        email = request.form["email"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone_number = request.form['phone_number']
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        code = request.form["code"]
        form = RegistrationContractorForm(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number = phone_number,
            password=password,
            confirm_password=confirm_password,
            code = code,
        )
        if form.validate_on_submit():
            company = Company.query.filter_by(code=code).first()
            role = Role.query.filter_by(name='Contractor').first()
            if company == None:
                flash('You put the wrong code to register, please contact your company', 'danger')
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                user = User(
                    email = email,
                    first_name = form.first_name.data,
                    last_name = form.last_name.data,
                    password = hashed_password,
                    role_id = role.id
                )
                contractor = Contractor(
                    phone_number = form.phone_number.data,
                    company_id = company.id
                )
                user.contractor = contractor
                db.session.add(user)
                db.session.add(contractor)
                db.session.commit()
                return redirect(url_for('accounts.login'))
    else:
        form = RegistrationContractorForm(
            email="",
            first_name="",
            last_name="",
            password="",
            confirm_password="",
            code="",
        )
    return render_template('contractor_register.html', title='Register', form=form, last_updated=dir_last_updated())

@fitters.route('/update_user', methods=['GET', 'POST'])
@login_required
def update_user():
    if request.method == 'POST':
        email = request.form["email"]
        current_password = request.form['current_password']
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        form = UpdateContractorAccountForm(email=email,current_password=current_password,
                new_password=new_password,confirm_password=confirm_password)
        if form.validate_on_submit():
            if bcrypt.check_password_hash(current_user.password, current_password):
                hashed_password = bcrypt.generate_password_hash(
                    new_password).decode('utf-8')
                current_user.email = form.email.data
                current_user.password = hashed_password
                db.session.commit()
                flash(f"Thank You. Your Account has been updated.", 'success')
                return redirect(url_for('fitters.home'))
    else:
        form = UpdateContractorAccountForm(email=current_user.email, current_password="",
            new_password="",confirm_password="")
    return render_template("contractor_user_update.html",title='Update Account', form=form,last_updated=dir_last_updated())

@fitters.route('/respond_quote/<id>/',methods=['GET','POST'])
@login_required
def respond_quote(id):
    contractor = Contractor.query.filter_by(user_id=current_user.id).first()
    response_quote =  ResponseQuote.query.get(id)
    quote = Quote.query.get(response_quote.quote_id)
    if request.method == 'POST':
        price = request.form["price"]
        form = ResponseQuoteForm(price=price)
        if form.validate_on_submit():
            response_quote.price = price
            response_quote.contractor_id = contractor.id
            db.session.commit()
            flash('Price added and Quote sent ! Thank you','success')
            return redirect(url_for('fitters.home'))
    else:
        form = ResponseQuoteForm(price='')
    return render_template('quote.html', title='Home',contractor=contractor,quote=quote,response_quote=response_quote,form=form,last_updated=dir_last_updated())


@fitters.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    contractor = Contractor.query.filter_by(user_id=current_user.id).first()
    current_date = datetime.now()
    response_quote_list = ResponseQuote.query.filter(ResponseQuote.time_due >= current_date,ResponseQuote.company_id==contractor.company_id).all()
    return render_template('contractor_home.html', title='Home',contractor=contractor,response_quote_list= response_quote_list,last_updated=dir_last_updated())


@fitters.route('/check_company',methods=['GET','POST'])
def check_company():
    code = request.form['code']
    company = Company.query.filter_by(code=code).first()
    if (company == None):
        return {'success': False}
    else:
        return {'success': True}
