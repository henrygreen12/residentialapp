from flask import Blueprint
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user, current_user, logout_user, login_required
from ..models import *
 
admin = Admin(name='admin')

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('accounts.login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_admin


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Customer, db.session))
admin.add_view(MyModelView(DHW, db.session))
admin.add_view(MyModelView(EdmontonWeather,db.session))
admin.add_view(MyModelView(ElectricalEquipment, db.session))
admin.add_view(MyModelView(ElectricalUsage, db.session))
admin.add_view(MyModelView(GasUsage, db.session))
admin.add_view(MyModelView(HeatingEquipment, db.session))
admin.add_view(MyModelView(Occupancy, db.session))
admin.add_view(MyModelView(WaterUsage, db.session))
admin.add_view(MyModelView(Survey, db.session))
admin.add_view(MyModelView(ApplianceCompanies, db.session))
admin.add_view(MyModelView(ApplianceStatic, db.session))
admin.add_view(MyModelView(Company, db.session))
admin.add_view(MyModelView(Contractor, db.session))
admin.add_view(MyModelView(Service, db.session))
admin.add_view(MyModelView(Quote, db.session))
admin.add_view(MyModelView(ResponseQuote, db.session))

