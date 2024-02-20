# -*- coding:utf-8 -*-
# @Date: "2024-02-17"
# @Description: flask app routes

import logging

from flask import render_template
from app.index import index_bp
from app import limiter

from flask_login import login_required

logger = logging.getLogger(__name__)


@index_bp.route('/', methods=['GET'])
@login_required
def root_default_request():
    return render_template('base.html')


@index_bp.route('/translate', methods=['GET'])
@login_required
def translate_request():
    return render_template('translate.html')


@index_bp.route('/translate/process_text', methods=['POST'])
@login_required
@limiter.limit("2 per second")
def translate_process_text():
    from flask import request, jsonify
    from app.api.translate import gl_proxy_apis
    data = request.json
    text = data.get('text', '')
    # 这里可以加入你想要的任何处理逻辑
    try:
        result = gl_proxy_apis.translate_text(text)
        processed_text = result.get('translate_text') or text
        logger.debug('processed_text: %s', result)
    except Exception as exc:
        processed_text = text
        logger.debug('processed_text err: %s', str(exc))
    return jsonify({'processed_text': processed_text})
