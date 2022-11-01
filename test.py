# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: test

import unittest

from api.baidu_api import BaiduApiClient
from libs.common.utils.config import load_config


class TestApi(unittest.TestCase):
    def setUp(self):
        self.conf = load_config('config.json')
        self.baidu_api = BaiduApiClient(self.conf)

    def test_baidu_api(self):
        text = '你好'
        result = self.baidu_api.translate(text)
        self.assertEqual(result, 'Hello')


if __name__ == '__main__':
    unittest.main()
