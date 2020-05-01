"""Tłumaczy posty za pomocą zewnętrznego API"""
import json

import requests
from flask import current_app
from flask_babel import _


def translate(text, source_lang, dest_lang):
    """
    API odpowiedzialne za tłumaczenie - MS TRANSLATION
    :param text: str
    :param source_lang: str
    :param dest_lang: str
    :return: json (str z przetłumaczonym tekstem)
    """
    if source_lang:
        lang = '{}-{}'.format(source_lang, dest_lang)
    else:
        lang = dest_lang
    path = 'https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&text={}&lang={}'.format(current_app.config[
                                                                                                       'TRANSLATOR_KEY'],
                                                                                                   text, lang)
    if 'TRANSLATOR_KEY' not in current_app.config or not current_app.config['TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    r = requests.get(path)
    if r.status_code != 200:
        return _('Error: The translation service failed.')
    return json.loads(r.content.decode('utf-8-sig'))['text'][0]
