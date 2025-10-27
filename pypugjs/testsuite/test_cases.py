from __future__ import print_function

import re
import difflib
from pathlib import Path

import pypugjs
import pypugjs.ext.html
import pytest
import six
from django.template import Engine
from pypugjs.exceptions import CurrentlyNotSupported

processors = {}
jinja_env = None


try:
    from jinja2 import Environment, FileSystemLoader
    from pypugjs.ext.jinja import PyPugJSExtension

    jinja_env = Environment(
        extensions=[PyPugJSExtension],
        loader=FileSystemLoader(str(Path(__file__).parent / "cases")),
    )

    def jinja_process(src, filename):
        template = jinja_env.get_template(filename)
        return template.render()

    processors["Jinja2"] = jinja_process
except ImportError:
    pass

# Test jinja2 with custom variable syntax: "{%#.-.** variable **.-.#%}"
try:
    from jinja2 import Environment, FileSystemLoader
    from pypugjs.ext.jinja import PyPugJSExtension

    jinja_env = Environment(
        extensions=[PyPugJSExtension],
        loader=FileSystemLoader(str(Path(__file__).parent / "cases")),
        variable_start_string="{%#.-.**",
        variable_end_string="**.-.#%}",
    )

    def jinja_process_variable_start_string(src, filename):
        template = jinja_env.get_template(filename)
        return template.render()

    processors["Jinja2-variable_start_string"] = jinja_process_variable_start_string
except ImportError:
    pass

try:
    import tornado.template
    from pypugjs.ext.tornado import patch_tornado

    patch_tornado()

    loader = tornado.template.Loader(str(Path(__file__).parent / "cases"))

    def tornado_process(src, filename):
        template = tornado.template.Template(src, name="_.pug", loader=loader)
        generated = template.generate(missing=None)
        if isinstance(generated, six.binary_type):
            generated = generated.decode("utf-8")
        return generated

    processors["Tornado"] = tornado_process
except ImportError:
    pass

# django tests
##################################################################################
try:
    import django
    from django.conf import settings

    if django.VERSION >= (1, 8, 0):
        config = {
            "TEMPLATES": [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [str(Path(__file__).parent / "cases")],
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                        "loaders": [
                            (
                                "pypugjs.ext.django.Loader",
                                (
                                    "django.template.loaders.filesystem.Loader",
                                    "django.template.loaders.app_directories.Loader",
                                ),
                            )
                        ],
                    },
                }
            ]
        }
        if django.VERSION >= (1, 9, 0):
            config["TEMPLATES"][0]["OPTIONS"]["builtins"] = [
                "pypugjs.ext.django.templatetags"
            ]
    else:
        config = {
            "TEMPLATE_DIRS": ("cases/",),
            "TEMPLATE_LOADERS": (
                (
                    "pypugjs.ext.django.Loader",
                    (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ),
                ),
            ),
        }

    settings.configure(**config)

    if django.VERSION >= (1, 7, 0):
        django.setup()

    from pypugjs.ext.django import Loader

    def django_process(src, filename):
        # actually use the django loader to get the sources
        loader = Loader(
            Engine.get_default(), config["TEMPLATES"][0]["OPTIONS"]["loaders"]
        )

        t = loader.get_template(filename)
        ctx = django.template.Context()
        return t.render(ctx)

    processors["Django"] = django_process
except ImportError:
    raise

try:
    import mako.template
    import pypugjs.ext.mako
    from mako.lookup import TemplateLookup

    dirlookup = TemplateLookup(
        directories=[str(Path(__file__).parent / "cases")],
        preprocessor=pypugjs.ext.mako.preprocessor,
    )

    def mako_process(src, filename):
        t = mako.template.Template(
            src,
            lookup=dirlookup,
            preprocessor=pypugjs.ext.mako.preprocessor,
            default_filters=["decode.utf8"],
        )
        return t.render()

    processors["Mako"] = mako_process

except ImportError:
    pass


def html_process(src, filename):
    return pypugjs.ext.html.process_pugjs(
        src, basedir=str(Path(__file__).parent / "cases")
    )


processors["Html"] = html_process


def run_case(case, process):
    import codecs

    processor = processors[process]
    with codecs.open(
        str(Path(__file__).parent / "cases/%s.pug") % case, encoding="utf-8"
    ) as pugjs_file:
        pugjs_src = pugjs_file.read()
        if isinstance(pugjs_src, six.binary_type):
            pugjs_src = pugjs_src.decode("utf-8")
        pugjs_file.close()

    with codecs.open(
        str(Path(__file__).parent / "cases/%s.html") % case, encoding="utf-8"
    ) as html_file:
        html_src = html_file.read().strip("\n")
        if isinstance(html_src, six.binary_type):
            html_src = html_src.decode("utf-8")
        html_file.close()
    try:
        processed_pugjs = processor(pugjs_src, "%s.pug" % case).strip("\n")

        if processed_pugjs != html_src:
            RED_BG = "\x1b[41m"    # expected-only segments (missing in output)
            GREEN_BG = "\x1b[42m"  # output-only segments (extra vs expected)
            RESET = "\x1b[0m"

            def merged_colored_text(a, b):
                sm = difflib.SequenceMatcher(None, a, b)
                parts = []
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag == 'equal':
                        parts.append(a[i1:i2])
                    elif tag == 'delete':
                        parts.append(RED_BG + a[i1:i2] + RESET)
                    elif tag == 'insert':
                        parts.append(GREEN_BG + b[j1:j2] + RESET)
                    elif tag == 'replace':
                        parts.append(RED_BG + a[i1:i2] + RESET)
                        parts.append(GREEN_BG + b[j1:j2] + RESET)
                return ''.join(parts)

            print(
                "\nDiff (" + str(len(html_src)) + " chars expected - "
                + str(len(processed_pugjs)) + " chars rendered)"
            )
            print("================== EXPECTED / RENDERED ==================\n")
            print(merged_colored_text(html_src, processed_pugjs))

        assert processed_pugjs == html_src

    except CurrentlyNotSupported:
        pass


exclusions = {
    # its a pity - the html compiler has the better results for mixins (indentation) but
    # has to be excluded to not "break" the other tests with their false results (bad expected indentation)
    "Html": {
        "mixins",
        "mixin.blocks",
        "layout",
        "unicode",
        "attrs.object",
        "include_mixin",
        "included_top_level",
        "included_nested_level",
    },
    "Mako": {
        "layout",
        "include_mixin",
        "included_top_level",
        "included_nested_level",
        "include-nested-include",
    },
    "Tornado": {
        "layout",
        "include_mixin",
        "include-nested-include",
        "included_top_level",
        "included_nested_level",
    },
    "Jinja2": {
        "layout",
        "included_top_level",
        "included_nested_level",
    },
    "Jinja2-variable_start_string": {
        "layout",
        "included_top_level",
        "included_nested_level",
    },
    "Django": {
        "layout",
        "included_top_level",
        "included_nested_level",
    },
}


def build_parameters():

    test_cases = []

    for processor in processors.keys():
        for path in (Path(__file__).parent / "cases").glob("*.pug"):
            case = re.sub(r"\.pug", "", path.name)
            if case not in exclusions[processor]:
                test_cases.append((case, processor))

    return test_cases


@pytest.mark.parametrize("case, processor", build_parameters())
def test_engines(case, processor):
    run_case(case, processor)
