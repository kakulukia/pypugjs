from django.utils import translation
from django.utils.translation import template

from pypugjs.ext.django.compiler import enable_pug_translations


def test_pug_translation_is_extracted():
    original_templatize = template.templatize
    try:
        enable_pug_translations()
        result = translation.templatize(
            'p {% trans "Hello from Pug" %}', origin="example.pug"
        )
    finally:
        template.templatize = original_templatize

    assert "gettext(u'Hello from Pug')" in result
