# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: app

import config

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_admin import Admin


db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


admin_view = Admin(name='Dashboard', template_mode='bootstrap4')


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    Session(app)

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # register blueprints
    from app.login import login_bp
    from app.index import index_bp
    app.register_blueprint(login_bp)
    app.register_blueprint(index_bp)

    from app.api import api
    app.register_blueprint(api)
    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.models import User
    from app.views import TsAdminIndexView, UserAdmin
    admin_view.init_app(app, index_view=TsAdminIndexView())
    admin_view.add_view(UserAdmin(User, db.session))

    return app

