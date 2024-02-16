# -*- coding:utf-8 -*-
# @Date: "2024-02-15"
# @Description: A simple translation server

import os
import sys
import logging

from flask import Flask, request

from ts_common.external_libs.pyhelper.utils.path_helper import PathHelper
from ts_common.external_libs.pyhelper.utils.config import load_config
from ts_common.api.proxy_api import ProxyAPIs


LOG_FILE = os.environ.get('TS_LOG_FILE', 'output.log')
LOG_LEVEL = os.environ.get('TS_LOG_LEVEL', 'DEBUG')

app = Flask(__name__)

gl_path_helper = PathHelper()
logging.basicConfig(filename=gl_path_helper.get_path(LOG_FILE), encoding='utf-8', level=LOG_LEVEL)

gl_config = load_config(gl_path_helper.get_path(os.environ.get("TS_CONFIG_FILE", "config.json")))
gl_proxy_apis = ProxyAPIs(gl_config)


def _check_auth(user, sign):
    # Check the user and sign
    # ...
    return True

@app.route('/translate', methods=['POST'])
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


@app.route('/', methods=['GET'])
def root_default_request():
    return 'Hello, World!' + str(os.environ.get('TS_LIBS'))


if __name__ == '__main__':
    app.run(debug=True)
