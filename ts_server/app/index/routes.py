# -*- coding:utf-8 -*-
# @Date: "2024-02-17"
# @Description: flask app routes

from flask import render_template
from app.index import index_bp

from flask_login import login_required

@index_bp.route('/', methods=['GET'])
@login_required
def root_default_request():
    return render_template('base.html')
