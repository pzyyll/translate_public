# -*- coding:utf-8 -*-
# @Date: "2024-02-19"
# @Description: auth check

import jwt
import time
import logging

logger = logging.getLogger(__name__)

def jwt_encode(user_name):
    from run import app
    payload = {
        'user': user_name,
        'ts': time.time()
    }
    return jwt.encode(payload, app.config.get('SECRET_KEY', '123456'), algorithm='HS256')

def jwt_check(token):
    from run import app
    from app.models import User
    try:
        token_decode = jwt.decode(token, app.config.get('SECRET_KEY', '123456'), algorithms='HS256')
        user_name = token_decode['user']
    except Exception as e:
        logger.error('jwt_check error: %s|%s', str(e), token)
        return False
    return User.query.filter_by(username=user_name).first() is not None
