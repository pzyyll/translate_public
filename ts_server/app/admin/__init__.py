# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: flask admin

from flask import Blueprint
from flask_admin import Admin
from app.views import TsAdminIndexView, UserAdmin
from app import app, db
from app.models import User


admin_bp = Blueprint('admin_view', __name__, url_prefix='/admin')
admin_view = Admin(name='Dashboard', template_mode='bootstrap4')


with app.app_context():
    admin_view.init_app(app, index_view=TsAdminIndexView())
    admin_view.add_view(UserAdmin(User, db.session))

from app.admin import routes
