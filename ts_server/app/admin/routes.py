# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: flask admin

import logging

from flask_login import login_required
from app.admin import admin_bp

logger = logging.getLogger(__name__)


@admin_bp.route('/get_token/<user_name>', methods=['GET', 'POST'])
@login_required
def get_token(user_name):
    from app.admin import jwt_encode
    from app.admin.db import db
    if not db.query_user_by_name(username=user_name):
        return 'user not found'
    try:
        token = jwt_encode(user_name)
    except Exception as e:
        return 'error: '+str(e)
    return 'get_token:'+token

@admin_bp.route('/add_user/<user_name>/<passwd>', methods=['GET', 'POST'])
@login_required
def add_user(user_name, passwd):
    from app.admin.db import db
    try:
        db.add_user(user_name, passwd)
    except Exception as e:
        return 'error: '+str(e)
    return 'add_user success'