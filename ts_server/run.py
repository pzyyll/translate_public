# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: run

import os

import app.admin

from ts_common.external_libs.pyhelper.utils.logging_helper import init_logging
from utils import path_helper

from app import app


LOG_FILE = os.environ.get('TS_LOG_FILE', 'output.log')
LOG_LEVEL = os.environ.get('TS_LOG_LEVEL', 'DEBUG')

init_logging(LOG_FILE, LOG_LEVEL)
path_helper.set_exec_file(__file__)

if __name__ == '__main__':
    app.run(debug=True)