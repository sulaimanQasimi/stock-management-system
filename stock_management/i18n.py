import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings

SUPPORTED_LANGUAGES = ('en', 'fa', 'ps')
RTL_LANGUAGES = {'fa', 'ps'}
APP_LANGUAGE_DIRS = ('authorization', 'stock_app', 'finance')


def normalize_language(language):
    code = (language or 'en').split('-')[0].lower()
    return code if code in SUPPORTED_LANGUAGES else 'en'


@lru_cache(maxsize=None)
def load_translations(language):
    language = normalize_language(language)
    translations = {}

    for app_name in APP_LANGUAGE_DIRS:
        path = Path(settings.BASE_DIR) / app_name / 'lang' / f'{language}.json'
        if path.exists():
            with path.open(encoding='utf-8') as file:
                translations.update(json.load(file))

    return translations


def get_language_payload(request):
    requested = request.GET.get('lang') or request.session.get('language') or request.COOKIES.get('language')
    language = normalize_language(requested)
    request.session['language'] = language

    return {
        'language': language,
        'direction': 'rtl' if language in RTL_LANGUAGES else 'ltr',
        'translations': load_translations(language),
        'available': [
            {'code': 'en', 'label': 'English'},
            {'code': 'fa', 'label': 'دری'},
            {'code': 'ps', 'label': 'پښتو'},
        ],
    }
