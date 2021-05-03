from functools import wraps
from flask import g,request,redirect, url_for ,flash,render_template
from flask_login import current_user
from .models import *
from .forms import *

def survey_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        survey = Survey.query.filter_by(customer_id=customer.id).first()
        print(survey)
        if survey == None :
            flash(f"Sorry but you need to fill up the survey first","danger")
            return redirect(url_for('main.customer_info'))
        return f(*args,**kwargs)
    return decorated_function


def type_required(f):
	@wraps(f)
	def decorated_function(*args,**kwargs):
		if current_user.role.name == 'Contractor':
			return redirect(url_for('fitters.home'))
		else:
			return f(*args,**kwargs)
	return decorated_function
