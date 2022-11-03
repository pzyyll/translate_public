# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: base api

import abc


class TranslateError(Exception):
    pass


class BaseAPI(abc.ABC):
    def __init__(self, conf):
        pass

    @abc.abstractmethod
    def detect_language(self, text):
        pass

    @abc.abstractmethod
    def translate(self, data=None):
        """_summary_
        Args:
            data (_type_, optional): _description_. Defaults to None
        Returns:
            _type_: _description_
            {'input': "你好", 'translate': "hello"}
        """
        pass

    @abc.abstractmethod
    def list_languages(self):
        pass
