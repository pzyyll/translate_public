# -*- coding:utf-8 -*-
# @Date: "2024-02-23"
# @Description: translate api client


from utils import path_helper, get_flask_env

from ts_common.api.proxy_api import ProxyAPIs
from ts_common.external_libs.pyhelper.utils.config import Config
from ts_common.external_libs.pyhelper.singleton import ABCSingletonMeta


class GlobalTranslateAPI(ProxyAPIs, metaclass=ABCSingletonMeta):
    def init(self, conf):
        conf = Config(path_helper.get_path(get_flask_env("TS_CONFIG_FILE", "config.json")))
        super().init(conf)


translate_api = GlobalTranslateAPI()