# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: baidu translate api

import random
import hashlib
import requests
from base_api import BaseApi

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
API_HOST = 'https://fanyi-api.baidu.com/api/trans/vip/'
DETECT = 'language'
TRANSLATE = 'translate'


class BaiduApiClient(BaseApi):
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
        r = requests.post(url, params=params, headers=HEADERS)
        result = r.json()
        return None if result.get('error_code') else result.get('data').get('src')

    def translate(self, text, params=None):
        params = params or {}
        from_language = params.get('from', 'auto')
        to_language = params.get('to', 'auto')
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
        r = requests.post(url, params=url_params, headers=HEADERS)
        result = r.json()
        if result.get('error_code'):
            # print('translate error: {}'.format(result.get('error_msg')))
            return None
        return '\n'.join([trans.get('dst') for trans in result.get('trans_result')])

    def list_language(self):
        return super().list_language()


if __name__ == '__main__':
    conf = {
        "baidu": {
            "app_id": "20200829000554481",
            "auth_key": "l1zd7pWC4ABUdIBooRv6"
        }
    }
    client = BaiduApiClient(conf)
    print(client.detect_language('Hello World! This is 1st paragraph.\nThis is 2nd paragraph.'))
    print(client.translate('Hello World! This is 1st paragraph.\nThis is 2nd paragraph.'))
    print(client.translate('你好，世界！这是第一段。\n这是第二段。'))
