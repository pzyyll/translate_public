# -*- coding:utf-8 -*-
# @Date: "2024-02-17"
# @Description: api routes

import logging

from flask import request

from utils import path_helper, get_flask_env

from ts_common.api.proxy_api import ProxyAPIs
from ts_common.external_libs.pyhelper.utils.config import Config

from app.api import api

logger = logging.getLogger(__name__)
gl_config = Config(path_helper.get_path(get_flask_env("TS_CONFIG_FILE", "config.json")))
gl_proxy_apis = ProxyAPIs(gl_config)
logger.debug('gl_proxy_apis: %s', gl_proxy_apis)


def _check_auth(user, sign):
    return True


@api.route('/translate', methods=['POST'])
def handle_translate_request():
    request_data = request.get_json()  # Get the JSON data from the request

    user = request_data.get('user')
    sign = request_data.get('sign')
    if _check_auth(user, sign) is False:
        return {'code': 401}

    data = request_data.get('data')
    if not data:
        return {'code': 400, 'message': 'Invalid request data.'}

    try:
        if data.get('api') in gl_proxy_apis.API_TYPE:
            gl_proxy_apis.set_api_type(data['api'])
        # Process the data as needed
        result = gl_proxy_apis.translate(data)
        return {'code': 200, 'result': result}
    finally:
        gl_proxy_apis.set_api_type()