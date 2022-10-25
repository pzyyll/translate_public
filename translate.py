# -*- coding:utf-8 -*-
# @Date: "2022-10-25"
# @Description: "translate"
# https://github.com/googleapis/python-translate/blob/HEAD/samples/snippets/snippets.py


from os import environ
from google.cloud import translate_v2 as _translate
from libs.common.singleton import Singleton
from libs.common.utils.path_helper import PathHelper

import click
import json

kPath = PathHelper(__file__)


class Translate(Singleton):
    def __init__(self, *args, **kwargs):
        self.init_auth()
        self.project_id = environ.get("PROJECT_ID", "")
        self.parent = f"projects/{self.project_id}"
        self.client = _translate.Client()

    def init_auth(self):
        with open(kPath.get_path("config.json"), "r") as f:
            config_data = json.load(f)
            environ["GOOGLE_APPLICATION_CREDENTIALS"] = config_data.get("auth_key", "")
            environ["PROJECT_ID"] = config_data.get("project_id", "")

    def translate(self, text, target_language_code, **kwargs):
        """Translates text into the target language.
        Target must be an ISO 639-1 language code.
        See https://g.co/cloud/translate/v2/translate-reference#supported_languages
        """
        import six
    
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        # print(u"Text: {}".format(result["input"]))
        # print(u"Translation: {}".format(result["translatedText"]))
        # print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
        return self.client.translate(text, target_language=target_language_code, **kwargs)

    def translate_with_model(self, text, target_language_code, model="nmt"):
        return self.translate_text(text, target_language_code, model=model)

    def list_languages(self):
        """Lists all available languages."""
        for language in self.client.get_languages():
            print(u"{name} ({language})".format(**language))

    def detect_language(self, text):
        """Detects the text's language."""
        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = self.client.detect_language(text)
        return result.get("language", None)


@click.group()
# @click.pass_context
def cli(**kwargs):
    pass

@cli.command()
@click.option('--text')
@click.option('--target', default=None, help="translate target language")
@click.option('--model', default=None, help="translate ai model e.g. \"nmt\"")
# @click.pass_context
def translate(text, target, model):
    # print('translate', text, target, model)
    if not target:
        detect_lang = Translate().detect_language(text)
        target = 'en' if 'zh' in detect_lang else 'zh-CN'
    result = Translate().translate(text, target, model=model)
    print(result['input'])
    print(result['translatedText'])

@cli.command()
def list_languages():
    Translate().list_languages()

if __name__ == "__main__":
    cli()