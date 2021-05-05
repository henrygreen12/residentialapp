from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import Form, StringField, PasswordField, BooleanField, IntegerField ,SelectField, FieldList, FormField, HiddenField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import *
from flask_login import current_user

##################################################################
# Everything here is related to a simple user
##################################################################
class RegistrationForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(min=4,max=30)])
	phone_number = StringField('Phone Number', validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])

	gas_bill = FileField('Upload your gas bill',validators=[FileAllowed(['jpg','jpeg','pdf','png','HEIC','HEIF'])])
	electrical_bill = FileField('Upload your electrical bill',validators=[FileAllowed(['jpg','jpeg','pdf','png','HEIC','HEIF'])])
	gas_address = HiddenField('Gas Address')
	electrical_address = HiddenField('Electrical Address')

	def validate_email(self,email):
		email = User.query.filter_by(email=email.data).first()
		if email:
			raise ValidationError('That email is taken, please choose another one ')

#This the form for login a user
class LoginForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(min=4,max=30)])
	password = PasswordField('Password',validators=[DataRequired()])

#This is the form for the reset password page

class RequestResetForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(min=4,max=30)] )

	def validate_email(self,email):
		email = User.query.filter_by(email=email.data).first()
		if email is None:
			raise ValidationError('There is no account with that email. You need to register ')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password',validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])


class CustomerForm(FlaskForm):
	phone_number = StringField('Phone Number', validators=[DataRequired()])
	square_footage = IntegerField('Square Footage', validators=[DataRequired()])
	occupants = IntegerField('Occupants', validators=[DataRequired()])
	hours = IntegerField('Hours', validators=[DataRequired()])

class UpdateAccountForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(min=4,max=30)])
	current_password = PasswordField('Current Password',validators=[DataRequired()])
	new_password = PasswordField('New Password',
							validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
							validators=[DataRequired(),EqualTo('new_password')])

	def validate_email(self,email):
		if email.data != current_user.email:
			email = User.query.filter_by(email=email.data).first()
			if email:
				raise ValidationError('That email is taken, please choose another one ')


class WindowForm(Form):
    length = IntegerField('length', validators=[DataRequired()])
    height = IntegerField('height', validators=[DataRequired()])
    location = SelectField('location', choices=[('First Floor', 'First Floor'), (
        'Main Floor', 'Main Floor'), ('Basement', 'Basement')], validators=[DataRequired()])
    room_type = SelectField('room_type', choices=[('Kitchen', 'Kitchen'), ('Living Room', 'Living Room'), (
        'Bedroom', 'Bedroom'), ('Bathroom', 'Bathroom')], validators=[DataRequired()])


class WindowsForm(FlaskForm):
    windows = FieldList(
        FormField(WindowForm)
    )


#this is form to upload a photo to verify appliances
# class ApplianceForm(FlaskForm):
# 	appliance_photo = FileField('Add Appliance Photo',validators=[FileAllowed(['jpg','jpeg','png'])])
# 	submit_photo = SubmitField('submit')

# class ApplianceModal(FlaskForm):
# 	usage_time = IntegerField('usage_time', validators=[DataRequired()])
# 	category = SelectField('location', choices=[('Kitchen','Basement','Misc','Entertainment')], validators=[DataRequired()])
# 	submitModal = SubmitField('submit')


class appliancePhotoForm(FlaskForm):
	appliance_photo = FileField('Add Appliance Photo',validators=[FileAllowed(['jpg','jpeg','png']),FileRequired()]  )
	submit_photo = SubmitField('submit')

class furnaceForm(FlaskForm):
    furnace_photo = FileField('Add Appliance Photo',validators=[FileAllowed(['jpg','jpeg','png']),FileRequired()]  )
    submit_furnace_photo = SubmitField('submit')

class applianceDetailsForm(FlaskForm):
	usage_time = IntegerField('usage_time', validators=[DataRequired()])
	category = SelectField('location', choices=[('Kitchen','Basement','Misc','Entertainment')], validators=[DataRequired()])
	submitDetails = SubmitField('submit')

class ApplianceForm(FlaskForm):
    appliancePhoto = FormField(appliancePhotoForm)
    applianceDetails = FormField(applianceDetailsForm)


class electricPhotoForm(FlaskForm):
	electric_photo = FileField('Add Electric Photo',validators=[FileAllowed(['jpg','jpeg','png']),FileRequired()]  )
	submit_photo = SubmitField('submit')
	submitModal = SubmitField('submit')


class TypeUserForm(FlaskForm):
	type_user = SelectField('type_user', choices=[('User', 'User'), ('Contractor', 'Contractor')], validators=[DataRequired()])



class DhWForm(FlaskForm):
	dhw_photo = FileField('Upload A Picture of your Domestic Hot Water',validators=[FileAllowed(['jpg','jpeg','pdf','png','HEIC','HEIF'])])

class QuoteForm(FlaskForm):
	quote_type = HiddenField('Quote Type')
	response1 = StringField('Response 1', validators=[DataRequired()])
	response2 = StringField('Response 2', validators=[DataRequired()])
	video = FileField('Upload a video of your furnace',validators=[FileAllowed(['3gp','avi','mov','mp4','mxf','mts','m2ts'])])

##################################################################
# Everything here is related to a contractor
##################################################################

class RegistrationContractorForm(FlaskForm):
	first_name = StringField('First Name', validators=[DataRequired(),Length(min=2,max=20)])
	last_name = StringField('Last Name', validators=[DataRequired(),Length(min=2,max=20)])
	phone_number = StringField('Phone Number', validators=[DataRequired()])
	email = StringField('Email',validators=[DataRequired(),Length(min=4,max=30)])
	password = PasswordField('Password',
							validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
							validators=[DataRequired(),EqualTo('password')])
	# location = StringField('Location', validators=[DataRequired(),Length(min=2,max=20)])
	code = PasswordField('Code')

class UpdateContractorAccountForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(min=4,max=30)])
    current_password = PasswordField('Current Password',validators=[DataRequired()])
    new_password = PasswordField('New Password',
							validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
							validators=[DataRequired(),EqualTo('new_password')])

    def validate_email(self,email):
	    if email.data != current_user.email:
		    email = User.query.filter_by(email=email.data).first()
		    if email:
			    raise ValidationError('That email is taken, please choose another one ')


class ResponseQuoteForm(FlaskForm):
	price = FloatField('Price',validators=[DataRequired()])

class MessageForm(FlaskForm):
    message = TextAreaField((u'Message'), validators=[
    DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(('Submit'))

class RecommendApplianceForm(FlaskForm):
	appliance_name = StringField('Appliance Name', validators=[DataRequired()])
	appliance_type = StringField('Appliance Type', validators=[DataRequired()])
	rated_power = StringField('Rated Power', validators=[DataRequired()])
	reason = TextAreaField((u'Reason'), validators=[DataRequired(), Length(min=0, max=140)])

class RecommendHeatingEquipmentForm(FlaskForm):
	btu_input = StringField('BTU Input', validators=[DataRequired()])
	btu_output = StringField('BTU Output', validators=[DataRequired()])
	efficiency = StringField('Efficiency', validators=[DataRequired()])
	type_heating = StringField('Type Heating', validators=[DataRequired()])
	name_plate = StringField('Name Plate', validators=[DataRequired()])
	reason = TextAreaField((u'Reason'), validators=[DataRequired(), Length(min=0, max=140)])

class RecommendDHWForm(FlaskForm):
	name_plate = StringField('Name Plate', validators=[DataRequired()])
	btu_output = StringField('BTU Output', validators=[DataRequired()])
	volume = StringField('Volume', validators=[DataRequired()])
	reason = TextAreaField((u'Reason'), validators=[DataRequired(), Length(min=0, max=140)])

