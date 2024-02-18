# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: app

import config

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(config)

# csrf = CSRFProtect(app)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# register blueprints
from app.login import login_bp
from app.index import index_bp
app.register_blueprint(login_bp)
app.register_blueprint(index_bp)

from app.api import api
app.register_blueprint(api)
from app.admin import admin_bp
app.register_blueprint(admin_bp)

with app.app_context():
    db.create_all()

    from app.models import User
    if User.query.filter_by(username="test").first() is None:
        print("create test user")
        user = User(username="test")
        user.set_passwd("test")
        db.session.add(user)
        db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

