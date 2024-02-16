# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: base api

import abc
import socks
import socket


class TranslateError(Exception):
    pass


class Proxy(object):
    PROTO_TYPE = {
        'socks5': socks.SOCKS5,
        'socks4': socks.SOCKS4,
        'http': socks.HTTP,
    }

    def __init__(self, proxy) -> None:
        self.proxy = proxy
        self._tmp_socket = None

    def init_proxy(self):
        if not self.proxy:
            return
        import re
        pattern = r"((?P<proto>\w+)://)?(?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})(:(?P<port>\d+))?"
        if not (m := re.match(pattern, self.proxy)):
            raise Exception(f'invalid proxy: {self.proxy}')
        proto = m.group('proto')
        ip = m.group('ip')
        port = m.group('port')
        if proto in self.PROTO_TYPE:
            socks.set_default_proxy(self.PROTO_TYPE[proto], ip, int(port))
        else:
            raise Exception(f'unsupported proxy protocol: {proto}')
        self._tmp_socket = socket.socket
        socket.socket = socks.socksocket

    def __enter__(self):
        if self.proxy:
            self.init_proxy()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.proxy and self._tmp_socket:
            socket.socket = self._tmp_socket
            self.proxy = None
            self._tmp_socket = None


class BaseAPI(abc.ABC):
    API_TYPE = "BASE_API"

    def __init__(self, conf):
        self.proxy = None

    def init(self, conf):
        pass

    def set_api_type(self, api_type=None):
        pass

    def detect_language(self, text):
        with Proxy(self.proxy):
            return self._detect_language(text)

    @abc.abstractmethod
    def _detect_language(self, text):
        pass

    def translate(self, data=None):
        with Proxy(self.proxy):
            return self._translate(data)

    @abc.abstractmethod
    def _translate(self, data=None):
        """_summary_
        Args:
            data: {key, optional}
            各自翻译API需要的参数，如：
                from: [auto, zh, en, ...],
                to: [auto, zh, en, ...],
                model: [nmt, base, ...],
                text: "你好",
                [todo other]: custom data,
            e.g:
            data = {
                "from": "auto",
                "to": "zh",
                "model": "nmt",
                "text": "hello"
            }
        Returns:
            _type_: _description_
            {'input': "你好", 'translate': "hello"}
        """
        pass

    def list_languages(self):
        with Proxy(self.proxy):
            return self._list_languages()

    @abc.abstractmethod
    def _list_languages(self):
        pass
