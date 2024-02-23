# -*- coding:utf-8 -*-
# @Date: "2024-02-22"
# @Description: test proxy worker

import sys
import os
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ts_common'))


from concurrent.futures import ProcessPoolExecutor

import logging

logging.basicConfig(level=logging.DEBUG, format="(%(threadName)-10s) %(thread)d %(message)s", filename='test.log', filemode='w')



class ProxyWorkerPoolManage(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.process_pools = []
        return cls._instance

    def add_process_pool(self, max_workers=1, *args, **kwargs):
        process_pool = ProcessPoolExecutor(max_workers=max_workers, *args, **kwargs)
        self.process_pools.append(process_pool)
        return process_pool

    def shutdown(self, wait=True):
        for process_pool in self.process_pools:
            process_pool.shutdown(wait=wait)
        self.process_pools = []

    
from ts_common.api.google_api_v3 import GoogleAPIV3
from ts_common.api.base_api import BaseTranslateAPI
from ts_common.external_libs.pyhelper.utils.proxy_helper import Proxy, ProxyWorkerPool
from ts_common.external_libs.pyhelper.utils.config import Config
from ts_common.external_libs.pyhelper.utils.path_helper import PathHelper

from ts_common.api.google_api_v3 import GoogleAPIV3
from ts_common.api.baidu_api import BaiduAPI

path_helper = PathHelper(__file__)
conf = Config(path_helper.get_path('../conf/ts_translate_api.conf'))

from ts_common.external_libs.pyhelper.singleton import ABCSingletonMeta


class GlobalGoobleAPI(GoogleAPIV3, metaclass=ABCSingletonMeta):
    pass

from ts_common.api.proxy_api import TranslateAPIProxyExecutor

if __name__ == "__main__":
    google_api = TranslateAPIProxyExecutor.create("socks5://127.0.0.1:10808", GlobalGoobleAPI, conf.get('google', {}))
    baidu_api = BaiduAPI(conf.get('baidu', {}))

    def translate_text(text, to_lang=None, **kwargs):
        for api in [google_api, baidu_api]:
            try:
                return api.translate_text(text, to_lang, **kwargs)
            except Exception as e:
                print(f'API {api} failed to translate text: {e}')
                continue

    def translate(text, to_lang=None, **kwargs):
        print(translate_text(text, to_lang, **kwargs))

    import threading
    thread1 = threading.Thread(target=translate, args=("hello",))
    thread2 = threading.Thread(target=translate, args=("hi",))
    thread3 = threading.Thread(target=translate, args=("how are you",))
    thread4 = threading.Thread(target=translate, args=("你好呵呵",))

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    import socket
    print(socket.socket)