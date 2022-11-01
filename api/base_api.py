# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: base api


class BaseApi(object):
    def __init__(self, conf):
        pass

    def detect_language(self, text):
        pass

    def translate(self, text, params=None):
        pass

    def list_language(self):
        pass