# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: utils for flask app

import os
from ts_common.external_libs.pyhelper.utils.path_helper import PathHelper

path_helper = PathHelper()

def get_flask_env(name, default=None):
    return os.environ.get(name, default)