# -*- coding:utf-8 -*-
# @Date: "2024-02-15"
# @Description: APIs Proxy

from collections import OrderedDict

from .base_api import BaseAPI, TranslateError
from .google_api import GoogleAPI
from .baidu_api import BaiduAPI


class ProxyAPIs(BaseAPI):
    GOOGLE = 'google'
    BAIDU = 'baidu'
    AUTO = 'auto'
    
    API_TYPE = OrderedDict({
        GOOGLE: GoogleAPI,
        BAIDU: BaiduAPI
    })

    def __init__(self, conf):
        super(ProxyAPIs, self).__init__(conf)
        self._apis = OrderedDict({})
        self._default_api = None
        self.init(conf)

    def init(self, conf):
        self._apis.clear()
        for api_type, api_class in self.API_TYPE.items():
            self._apis[api_type] = api_class(conf)

    def set_api_type(self, api_type=None):
        if not api_type and self._default_api:
            self._default_api = None
            return
        
        if api_type not in self._apis:
            return

        if api_type in self._apis:
            self._default_api = self._apis[api_type]

    def _detect_language(self, text):
        if self._default_api:
            try:
                return self._default_api.detect_language(text)
            except Exception as exc:
                raise TranslateError('Default API failed to detect language.') from exc

        for _, api in self._apis.items():
            try:
                return api.detect_language(text)
            except Exception:
                continue
        raise TranslateError('All APIs failed to detect language.')

    def _translate(self, data=None):
        if self._default_api:
            try:
                return self._default_api.translate(data)
            except Exception as exc:
                raise TranslateError('Default API failed to translate text.') from exc

        for _, api in self._apis.items():
            try:
                return api.translate(data)
            except Exception:
                continue
        raise TranslateError('All APIs failed to translate text.')

    def _list_languages(self):
        if self._default_api:
            try:
                return self._default_api.list_languages()
            except Exception as exc:
                raise TranslateError('Default API failed to list languages.') from exc

        for api in self._apis.items():
            try:
                return api.list_languages()
            except Exception:
                continue
        raise TranslateError('All APIs failed to list languages.')
