# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: google translate api


class GoogleApi(object):
    def __init__(self, conf):
        google_data = conf.get('google', {})
        self.api_key = google_data.get('api_key', '')
        self.api_url = google_data.get('api_url', '')