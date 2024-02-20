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


path_helper = PathHelper(__file__)
conf = Config(path_helper.get_path('../conf/dev_ts_svr.conf'))

google_api = GoogleAPIV3()
google_api.init(conf['google'])

def test_google_api_v3():
    print(google_api.translate_text('hello', 'zh'))


if __name__ == '__main__':
    test_google_api_v3()