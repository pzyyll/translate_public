# -*- coding:utf-8 -*-
# @Date: "2024-02-15"
# @Description: a client for the translation server

import codecs
import functools
import logging

from urllib.parse import urljoin
import requests

import click

from mako.template import Template
from ts_common.api.base_api import BaseAPI
from ts_common.external_libs.pyhelper.utils.path_helper import PathHelper
from ts_common.external_libs.pyhelper.utils.config import Config


class QueryCmd(object):
    TRANSLATE = 'translate'
    TRANSLATE_HTML = 'translate_html'
    LIST_LANGUAGES = 'list_languages'


kPath = PathHelper(__file__)


def except_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            print("error: ", e)
    return wrapper


class TranslateClient(BaseAPI):
    def init(self, conf):
        super(TranslateClient, self).init(conf)
        self._user = conf.get('user', None)
        self._identify_key = conf.get('identify_key', None)
        self._url = conf.get('url', None)
        self._log_level = conf.get('log_level', 'DEBUG')
        self._log_file = conf.get('log_file', kPath.get_path('./ts_client.log'))

    def _detect_language(self, text):
        pass

    def _list_languages(self):
        pass

    def _translate(self, data=None):
        post_data = {
            "data": data,
            "user": self._user,
            "sign": "123456",
        }
        rsp = requests.post(urljoin(self._url, QueryCmd.TRANSLATE), json=post_data, timeout=10)
        return rsp.json().get('result', {})


_translate_client = TranslateClient({}) 


@click.group()
@click.option('--proxy', default='', help='proxy, e.g. socks5://127.0.0.1:1081')
@click.option('--config', default="ts_client.conf", help='config file')
def cli(proxy, config):
    conf = Config(kPath.get_path(config))
    logging.basicConfig(
        filename=kPath.get_path(conf.get('log_file', './ts_client.log')),
        encoding='utf-8',
        level=conf.get('log_level', 'DEBUG')
    )

    _translate_client.init(conf)


@cli.command()
@click.option('--text')
@click.option('--target', default=None, help="translate target language")
@click.option('--model', default=None, help="translate ai model e.g. \"nmt\"")
@click.option(
    '--print_format',
    default="{input}\n{translate}",
    help="print format-string. {input|translate|html}")
@click.option('--api', default='auto', help='support "auto", "google", "baidu"')
@except_log
def translate(text, target, model, print_format, api):
    # print('translate', text, target, model, type(print_format))
    logging.info('translate %s %s %s %s', text, target, model, print_format)
    data = {
        "from": "auto",
        "to": target or "auto",
        "model": model,
        "text": text,
        'api': api
    }

    result = _translate_client.translate(data)
    if print_format == "html":
        htmlfile = kPath.get_resource_path("./resources/index.html")
        tmp = Template(filename=htmlfile)
        print(tmp.render(input=result['input'], translate=result['translate']))
    else:
        print(
            codecs.decode(print_format, "unicode_escape").format(
                input=result['input'], translate=result['translate']))


@cli.command()
@except_log
def list_languages():
    _translate_client.list_languages()


if __name__ == "__main__":
    cli()
