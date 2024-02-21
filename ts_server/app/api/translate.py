# -*- coding:utf-8 -*-
# @Date: "2024-02-17"
# @Description: api routes

import logging

from http import HTTPStatus
from flask import request, make_response, jsonify

from utils import path_helper, get_flask_env

from ts_common.api.proxy_api import ProxyAPIs
from ts_common.external_libs.pyhelper.utils.config import Config
from ts_common.external_libs.pyhelper.singleton import singleton

from app.api import api
from app.admin.auth_check import jwt_check

logger = logging.getLogger(__name__)
gl_config = Config(path_helper.get_path(get_flask_env("TS_CONFIG_FILE", "config.json")))


@singleton
class GlobalProxyAPIs(ProxyAPIs):
    pass


gl_proxy_apis = GlobalProxyAPIs(gl_config)


@api.route('/translate', methods=['POST'])
def handle_translate_request():
    from google.protobuf import json_format
    from ts_common.proto.translate_pb2 import TranslateTextRequest

    requestMsg = json_format.ParseDict(request.get_json(), TranslateTextRequest())
    logger.debug("requestMsg: %s", requestMsg)
    if jwt_check(requestMsg.token, requestMsg.user) is False:
        return jsonify({'code': HTTPStatus.UNAUTHORIZED, 'msg': 'Token is not valid.'}), HTTPStatus.UNAUTHORIZED
    if not requestMsg.data:
        return jsonify({'code': HTTPStatus.BAD_REQUEST, 'msg': 'Invalid request data.'}), HTTPStatus.BAD_REQUEST
    api_type = requestMsg.data.api_type

    try:
        with gl_proxy_apis.api_type_context(api_type):
            result = gl_proxy_apis.translate_text(requestMsg.data.text, requestMsg.data.target_lang_code)
            logger.debug("result: %s", result)
            response_body = {
                'code': HTTPStatus.OK,
                'result': result,
                **({'from_api_type': gl_proxy_apis.last_translate_api_type} if not api_type else {})
            }
            return jsonify(response_body), HTTPStatus.OK
    except Exception as e:
        logger.error("handle_translate_request error: %s", e)
        return jsonify({
            'code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'msg': 'Server error.'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
