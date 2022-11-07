# -*- coding:utf-8 -*-
# @Date: "2022-11-01"
# @Description: google translate api


from os import environ
from google.cloud import translate_v2 as _translate

import six
import html
import logging


class GoogleAPI(object):
    def __init__(self, conf):
        google_data = conf.get('google', {})
        self.project_id = google_data.get('project_id', '')
        self.auth_key = google_data.get('auth_key', '')
        self.parent = f"projects/{self.project_id}"

        self.init_auth()
        self.client = _translate.Client()

    def init_auth(self):
        environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.auth_key
        environ["PROJECT_ID"] = self.project_id

    def translate(self, data=None):
        """Translates text into the target language.
        Target must be an ISO 639-1 language code.
        See https://g.co/cloud/translate/v2/translate-reference#supported_languages
        """
        data = data or {}
        text = data.get("text", "")
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

        from_language = data.get('from', 'auto')
        if from_language == 'auto':
            from_language = self.detect_language(text)
        target_language_code = data.get('to', 'auto')
        if target_language_code == 'auto':
            target_language_code = 'en' if 'zh' in from_language else 'zh'

        params = {
            "source_language": from_language,
            "target_language": target_language_code,
            "model": data.get('model', None)
        }

        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        # print(u"Text: {}".format(result["input"]))
        # print(u"Translation: {}".format(result["translatedText"]))
        # print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
        logging.debug(f'text: {text}, params: {params}')
        result = self.client.translate(text, **params)
        input_text = result.get("input", "")
        translated_text = html.unescape(result.get('translatedText'))
        return {'input': input_text, 'translate': translated_text}

    def list_languages(self):
        """Lists all available languages."""
        result = self.client.get_languages()
        for language in self.client.get_languages():
            print(u"{name} ({language})".format(**language))
        return result

    def detect_language(self, text):
        """Detects the text's language."""
        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = self.client.detect_language(text)
        return result.get("language", None)
