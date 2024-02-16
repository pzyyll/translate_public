# -*- coding:utf-8 -*-
# @Date: "2024-02-15"
# @Description: a test client for the translation server

import requests


def test_post():
    url = 'http://127.0.0.1:5000/translate'
    data = {
        "from": "auto",
        "to": "zh",
        "model": "nmt",
        "text": "hello yes, this is a test. 你好，这是一个测试。",
        "api": "google"
    }
    post_data = {
        "data": data,
        "user": "test",
        "sign": "123456",
    }
    response = requests.post(url, json=post_data)
    print(response.text)


if __name__ == '__main__':
    test_post()
