from __future__ import print_function

import six
from django.template import Engine
from nose import with_setup

import pypugjs
import pypugjs.ext.html
from pypugjs.exceptions import CurrentlyNotSupported

processors = {}
jinja_env = None


def teardown_func():
    pass


try:
    from jinja2 import Environment, FileSystemLoader
    from pypugjs.ext.jinja import PyPugJSExtension

    jinja_env = Environment(
        extensions=[PyPugJSExtension], loader=FileSystemLoader('cases/')
    )

    def jinja_process(src, filename):
        global jinja_env
        template = jinja_env.get_template(filename)
        return template.render()

    processors['Jinja2'] = jinja_process
except ImportError:
    pass

# Test jinja2 with custom variable syntax: "{%#.-.** variable **.-.#%}"
try:
    from jinja2 import Environment, FileSystemLoader
    from pypugjs.ext.jinja import PyPugJSExtension

    jinja_env = Environment(
        extensions=[PyPugJSExtension],
        loader=FileSystemLoader('cases/'),
        variable_start_string="{%#.-.**",
        variable_end_string="**.-.#%}",
    )

    def jinja_process_variable_start_string(src, filename):
        global jinja_env
        template = jinja_env.get_template(filename)
        return template.render()

    processors['Jinja2-variable_start_string'] = jinja_process_variable_start_string
except ImportError:
    pass

try:
    import tornado.template
    from pypugjs.ext.tornado import patch_tornado

    patch_tornado()

    loader = tornado.template.Loader('cases/')

    def tornado_process(src, filename):
        global loader, tornado
        template = tornado.template.Template(src, name='_.pug', loader=loader)
        generated = template.generate(missing=None)
        if isinstance(generated, six.binary_type):
            generated = generated.decode("utf-8")
        return generated

    processors['Tornado'] = tornado_process
except ImportError:
    pass

# django tests
##################################################################################
try:
    import django
    from django.conf import settings

    if django.VERSION >= (1, 8, 0):
        config = {
            'TEMPLATES': [
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': ["cases/"],
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                        'loaders': [
                            (
                                'pypugjs.ext.django.Loader',
                                (
                                    'django.template.loaders.filesystem.Loader',
                                    'django.template.loaders.app_directories.Loader',
                                ),
                            )
                        ],
                    },
                }
            ]
        }
        if django.VERSION >= (1, 9, 0):
            config['TEMPLATES'][0]['OPTIONS']['builtins'] = [
                'pypugjs.ext.django.templatetags'
            ]
    else:
        config = {
            'TEMPLATE_DIRS': ("cases/",),
            'TEMPLATE_LOADERS': (
                (
                    'pypugjs.ext.django.Loader',
                    (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
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
            Engine.get_default(), config['TEMPLATES'][0]['OPTIONS']['loaders']
        )

        t = loader.get_template(filename)
        ctx = django.template.Context()
        return t.render(ctx)

    processors['Django'] = django_process
except ImportError:
    raise

try:
    import pypugjs.ext.mako
    import mako.template
    from mako.lookup import TemplateLookup

    dirlookup = TemplateLookup(
        directories=['cases/'], preprocessor=pypugjs.ext.mako.preprocessor
    )

    def mako_process(src, filename):
        t = mako.template.Template(
            src,
            lookup=dirlookup,
            preprocessor=pypugjs.ext.mako.preprocessor,
            default_filters=['decode.utf8'],
        )
        return t.render()

    processors['Mako'] = mako_process

except ImportError:
    pass


def setup_func():
    global jinja_env, processors


def html_process(src, filename):
    return pypugjs.ext.html.process_pugjs(src, basedir='cases')


processors['Html'] = html_process


def run_case(case, process):
    import codecs

    global processors
    processor = processors[process]
    with codecs.open('cases/%s.pug' % case, encoding='utf-8') as pugjs_file:
        pugjs_src = pugjs_file.read()
        if isinstance(pugjs_src, six.binary_type):
            pugjs_src = pugjs_src.decode('utf-8')
        pugjs_file.close()

    with codecs.open('cases/%s.html' % case, encoding='utf-8') as html_file:
        html_src = html_file.read().strip('\n')
        if isinstance(html_src, six.binary_type):
            html_src = html_src.decode('utf-8')
        html_file.close()
    try:
        processed_pugjs = processor(pugjs_src, '%s.pug' % case).strip('\n')
        print('PROCESSED (' + str(len(processed_pugjs)) + ' chars)\n' + processed_pugjs)
        print('\nEXPECTED (' + str(len(html_src)) + ' chars)\n' + html_src)
        assert processed_pugjs == html_src

    except CurrentlyNotSupported:
        pass


exclusions = {
    # its a pity - the html compiler has the better results for mixins (indentation) but
    # has to be excluded to not "break" the other tests with their false results (bad expected indentation)
    'Html': {
        'mixins',
        'mixin.blocks',
        'layout',
        'unicode',
        'attrs.object',
        'include_mixin',
        'included_top_level',
        'included_nested_level',
    },
    'Mako': {
        'layout',
        'include_mixin',
        'included_top_level',
        'included_nested_level',
        'include-nested-include',
    },
    'Tornado': {
        'layout', 'include_mixin',
        'include-nested-include',
        'included_top_level',
        'included_nested_level',
    },
    'Jinja2': {
        'layout',
        'included_top_level',
        'included_nested_level',
    },
    'Jinja2-variable_start_string': {
        'layout',
        'included_top_level',
        'included_nested_level',
    },
    'Django': {
        'layout',
        'included_top_level',
        'included_nested_level',
    },
}


@with_setup(setup_func, teardown_func)
def test_case_generator():
    global processors

    import os

    for dirname, dirnames, filenames in os.walk('cases/'):
        # raise Exception(filenames)
        filenames = filter(lambda x: x.endswith('.pug'), filenames)
        filenames = list(map(lambda x: x.replace('.pug', ''), filenames))
        for processor in processors.keys():
            for filename in filenames:
                if filename not in exclusions[processor]:
                    yield run_case, filename, processor
