# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: test

import unittest
import openpyxl

from api.baidu_api import BaiduAPI
from libs.common.utils.config import load_config


class TestApi(unittest.TestCase):
    pass
    # def setUp(self):
    #     self.conf = load_config('config.json')
    #     self.baidu_api = BaiduAPI(self.conf)

    # def test_baidu_api(self):
    #     text = '你好'
    #     result = self.baidu_api.translate(text)
    #     self.assertEqual(result, 'Hello')

    # def test_baidu_api_detect(self):
    #     text = '你好'
    #     result = self.baidu_api.detect_language(text)
    #     self.assertEqual(result, 'zh')

