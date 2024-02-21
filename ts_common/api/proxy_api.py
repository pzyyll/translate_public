# -*- coding:utf-8 -*-
# @Date: "2024-02-15"
# @Description: APIs Proxy

import logging
from collections import OrderedDict

from .base_api import ProxyAwareTranslateAPI, TranslateError
from .google_api import GoogleAPI
from .baidu_api import BaiduAPI


class ApiTypeContext(object):
    def __init__(self, api, api_type):
        self.api_type = api_type
        self.api = api

    def __enter__(self):
        self.api.set_api_type(self.api_type)
        return self.api

    def __exit__(self, exc_type, exc_value, traceback):
        self.api.set_api_type(None)


class ProxyAPIs(ProxyAwareTranslateAPI):
    GOOGLE = 'google'
    BAIDU = 'baidu'
    
    API_TYPE = OrderedDict({
        GOOGLE: GoogleAPI,
        BAIDU: BaiduAPI
    })

    @property
    def _default_api(self):
        return self._apis.get(self.api_type, None)

    def init(self, conf):
        super(ProxyAPIs, self).init(conf)
        self._apis = OrderedDict({})
        self.last_translate_api_type = None
        for api_type, api_class in self.API_TYPE.items():
            self._apis[api_type] = api_class(conf.get(api_type, {}))

    def set_api_type(self, api_type=None):
        super(ProxyAPIs, self).set_api_type(None)
        if api_type and api_type not in self._apis:
            raise ValueError('Invalid API type.')

    def api_type_context(self, api_type):
        from contextlib import nullcontext
        return ApiTypeContext(self, api_type) if api_type else nullcontext()

    def _detect_language(self, text, **kwargs):
        if self._default_api:
            try:
                return self._default_api.detect_language(text, **kwargs)
            except Exception as exc:
                raise TranslateError('Default API failed to detect language.') from exc

        for _, api in self._apis.items():
            try:
                return api.detect_language(text, **kwargs)
            except Exception as exc:
                logging.warning(f'API {api} failed to detect language: {exc}')
                continue
        raise TranslateError('All APIs failed to detect language.')

    def _translate_text(self, text, to_lang=None, **kwargs):
        if self._default_api:
            try:
                return self._default_api.translate_text(text, to_lang, **kwargs)
            except Exception as exc:
                raise TranslateError('Default API failed to translate text.') from exc

        for api_type, api in self._apis.items():
            try:
                reusult = api.translate_text(text, to_lang, **kwargs)
                self.last_translate_api_type = api_type
                return reusult
            except Exception as e:
                logging.warning(f'API {api} failed to translate text: {e}')
                continue
        raise TranslateError('All APIs failed to translate text.')

    def _list_languages(self, display_language_code=None):
        if self._default_api:
            try:
                return self._default_api.list_languages(display_language_code)
            except Exception as exc:
                raise TranslateError('Default API failed to list languages.') from exc

        for api in self._apis.items():
            try:
                return api.list_languages(display_language_code)
            except Exception as e:
                logging.warning(f'API {api} failed to list languages: {e}')
                continue
        raise TranslateError('All APIs failed to list languages.')
