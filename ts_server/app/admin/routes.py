# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: flask admin

import jwt
import logging
import time

from flask_login import login_required
from app.admin import admin_bp
from app import app, db
from app.models import User

logger = logging.getLogger(__name__)


def jwt_encode(user_name):
    payload = {
        'user': user_name,
        'ts': time.time()
    }
    return jwt.encode(payload, app.config.get('SECRET_KEY', '123456'), algorithm='HS256')

def jwt_check(token):
    try:
        token_decode = jwt.decode(token, app.config.get('SECRET_KEY', '123456'), algorithms='HS256')
        user_name = token_decode['user']
    except Exception as e:
        logger.error('jwt_check error: %s|%s', str(e), token)
        return False
    return User.query.filter_by(username=user_name).first() is not None

@admin_bp.route('/get_token/<user_name>', methods=['GET', 'POST'])
@login_required
def get_token(user_name):
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