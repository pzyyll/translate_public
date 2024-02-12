# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: baidu translate api

import random
import hashlib
import requests
from .base_api import BaseAPI

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
API_HOST = 'https://fanyi-api.baidu.com/api/trans/vip/'
DETECT = 'language'
TRANSLATE = 'translate'


class BaiduAPI(BaseAPI):
    def __init__(self, conf):
        baidu_data = conf.get('baidu', {})
        self.app_id = baidu_data.get('app_id', '')
        self.auth_key = baidu_data.get('auth_key', '')

    def _make_sign(self, query, salt):
        sign = self.app_id + query + str(salt) + self.auth_key
        return hashlib.md5(sign.encode('utf-8')).hexdigest()

    def _make_salt(self):
        return random.randint(0xffff, 0xffffffff)

    def detect_language(self, text):
        salt = self._make_salt()
        sign = self._make_sign(text, salt)
        params = {'appid': self.app_id, 'q': text, 'salt': salt, 'sign': sign}
        url = API_HOST + DETECT
        r = requests.post(url, params=params, headers=HEADERS, timeout=10)
        result = r.json()
        return None if result.get('error_code') else result.get('data').get('src')

    def translate(self, data=None):
        data = data or {}
        text = data.get('text', '')

        from_language = data.get('from', 'auto')
        to_language = data.get('to', 'auto')
        if to_language == 'auto':
            src_language = self.detect_language(text)
            to_language = 'en' if src_language == 'zh' else 'zh'

        salt = self._make_salt()
        sign = self._make_sign(text, salt)
        url_params = {
            'appid': self.app_id,
            'q': text,
            'from': from_language,
            'to': to_language,
            'salt': salt, 'sign': sign
        }
        url = API_HOST + TRANSLATE
        r = requests.post(url, params=url_params, headers=HEADERS, timeout=10)
        result = r.json()
        if result.get('error_code'):
            # print('translate error: {}'.format(result.get('error_msg')))
            return None
        translate_text = '\n'.join([trans.get('dst') for trans in result.get('trans_result')])
        return {'input': text, 'translate': translate_text}

    def list_languages(self):
        print('baidu api not support list language')
        return None


if __name__ == '__main__':
    conf = {
        "baidu": {
            "app_id": "123456789",
            "auth_key": "███████████████████████████"
        }
    }
    client = BaiduAPI(conf)
    print(client.detect_language('Hello World! This is 1st paragraph.\nThis is 2nd paragraph.'))
    print(client.translate('Hello World! This is 1st paragraph.\nThis is 2nd paragraph.'))
    print(client.translate('你好，世界！这是第一段。\n这是第二段。'))
