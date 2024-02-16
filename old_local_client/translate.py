# -*- coding:utf-8 -*-
# @Date: "2022-10-25"
# @Description: "translate"
# https://github.com/googleapis/python-translate/blob/HEAD/samples/snippets/snippets.py


import socket
import codecs
import functools
import logging
import sys
import os

import socks
import click

from mako.template import Template
from api.google_api import GoogleAPI
from api.baidu_api import BaiduAPI
from libs.common.utils.path_helper import PathHelper
from libs.common.utils.config import load_config


kPath = PathHelper(__file__)
kConfig = {}   # load_config(kPath.get_path("config.json"))

logging.basicConfig(filename=kPath.get_path("output.log"), encoding='utf-8', level=logging.DEBUG)

kProtoTypes = {
    'socks5': socks.SOCKS5,
    'socks4': socks.SOCKS4,
    'http': socks.HTTP,
}


def except_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            print("error: ", e)
    return wrapper


def init_proxy(proxy):
    import re
    pattern = r"((?P<proto>\w+)://)?(?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})(:(?P<port>\d+))?"
    if not (m := re.match(pattern, proxy)):
        raise Exception(f'invalid proxy: {proxy}')
    proto = m.group('proto')
    ip = m.group('ip')
    port = m.group('port')
    if proto in kProtoTypes:
        socks.set_default_proxy(kProtoTypes[proto], ip, int(port))
    else:
        raise Exception(f'unsupported proxy protocol: {proto}')
    socket.socket = socks.socksocket


_translate_client = None  # GoogleAPI(kConfig)


@click.group()
# @click.pass_context
@click.option('--config', default="config.json", help='config file')
@click.option('--api', default='google', help='support "google", "baidu"')
@click.option('--proxy', default='', help='proxy, e.g. socks5://127.0.0.1:1081')
def cli(config, api, proxy):
    global kConfig
    global _translate_client
    kConfig = load_config(kPath.get_path(config))

    if proxy := proxy or kConfig.get('proxy', ''):
        init_proxy(proxy)

    _translate_api = {
        'google': GoogleAPI(kConfig),
        'baidu': BaiduAPI(kConfig),
    }
    if api not in _translate_api:
        raise Exception(f'unsupported api: {api}')

    _translate_client = _translate_api.get(api)


@cli.command()
@click.option('--text')
@click.option('--target', default=None, help="translate target language")
@click.option('--model', default=None, help="translate ai model e.g. \"nmt\"")
@click.option(
    '--print_format',
    default="{input}\n{translate}",
    help="print format-string. {input|translate|html}")
# @click.pass_context
@except_log
def translate(text, target, model, print_format):
    # print('translate', text, target, model, type(print_format))
    logging.info('translate %s %s %s %s', text, target, model, print_format)
    data = {
        "from": "auto",
        "to": target or "auto",
        "model": model,
        "text": text
    }

    result = _translate_client.translate(data)
    if print_format == "html":
        htmlfile = kPath.get_path("resources/index.html")
        if not kPath.is_local_path(htmlfile):
            htmlfile = kPath.get_resource_path("resources/index.html")
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


def _test():
    print(getattr(sys, '_MEIPASS', None))
    print(os.path.abspath(os.path.dirname(__file__)))

    print(kPath.exec_path)
    if getattr(sys, 'frozen', False):
        print(sys.executable)

    print(sys.argv)
    print(os.getcwd())
    print(kPath.get_cwd_path(''))


@cli.command()
def test():
    _test()

if __name__ == "__main__":
    cli()
