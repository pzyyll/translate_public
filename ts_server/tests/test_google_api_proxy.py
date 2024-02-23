# -*- coding:utf-8 -*-
# @Date: "2024-02-20"
# @Description: google translate api


import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ts_common'))


from ts_common.api.google_api_v3 import GoogleAPIV3
from ts_common.external_libs.pyhelper.utils.config import Config
from ts_common.external_libs.pyhelper.utils.path_helper import PathHelper
from ts_common.external_libs.pyhelper.utils.proxy_helper import Proxy

path_helper = PathHelper(__file__)
conf = Config(path_helper.get_path('../conf/ts_translate_api.conf'))

google_api = GoogleAPIV3()
google_api.init(conf['google'])

def test_google_api_v3():
    result = google_api.translate_text('hello')

    assert result.get('translate_text') == "你好"

def test_google_api_with_proxy():
    with Proxy('socks5://127.0.0.1:10808'):
        result = google_api.translate_text('hello', timeout=30)
    assert result.get('translate_text') == "你好"


if __name__ == '__main__':
    # test_google_api_v3()
    test_google_api_with_proxy()