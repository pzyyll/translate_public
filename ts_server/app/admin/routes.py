# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: flask admin

import logging

from flask_login import login_required
from app.admin import admin_bp
from app.models import User

logger = logging.getLogger(__name__)


@admin_bp.route('/get_token/<user_name>', methods=['GET', 'POST'])
@login_required
def get_token(user_name):
    from app.admin import jwt_encode
    if User.query.filter_by(username=user_name).first() is None:
        return 'user not found'
    try:
        token = jwt_encode(user_name)
    except Exception as e:
        return 'error: '+str(e)
    return 'get_token:'+token

@admin_bp.route('/add_user/<user_name>/<passwd>', methods=['GET', 'POST'])
@login_required
def add_user(user_name, passwd):
    if User.query.filter_by(username=user_name).first() is not None:
        return 'user exists'
    user = User(username=user_name)
    user.set_passwd(passwd)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return 'error: '+str(e)
    return 'add_user success'