Django 1.11+
------------

In `settings.py`, add a `loader` to `TEMPLATES` like so:

.. code:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'templates')
            ],
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                # PyPugJS part:
                'loaders': [
                    ('pypugjs.ext.django.Loader', (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ))
                ],
                'builtins': [
                    'pypugjs.ext.django.templatetags',
                ],
            },
        },
    ]

In case you want to use Djangos translation feature add the following call to settings.py
(Note: only .pug files are supported)

.. code:: python

    from pypugjs.ext.django.compiler import enable_pug_translations

    enable_pug_translations()

The PyPugJS template loader features the built in Django functionality of caching templates
when ``DEBUG=False`` and re-reading from file system when ``DEBUG=True``. This means that unlike with PyJade and other templating engines, you *should not* wrap PyPugJS's template loader in Django's caching loader. If you do, you may see unrendered templates in some places. (Background in `#44 <https://github.com/kakulukia/pypugjs/issues/44>`_.)

Jinja2
------

Install the jinja2 lib

.. code:: shell

    pip install jinja2


In your code add the pug extension like this:

.. code:: python

    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader('.'),
        extensions=['pypugjs.ext.jinja.PyPugJSExtension']
    )

    template = env.get_template('test.pug')
    print(template.render(name="World"))

While test.pug looks like this:

.. code:: pug

    .foo Hello {{ name }}!


Mako
----

Just add  ``pypugjs.ext.mako.preprocessor`` as preprocessor

.. code:: python

    from pypugjs.ext.mako import preprocessor as mako_preprocessor
    mako.template.Template(haml_source,
        preprocessor=mako_preprocessor
    )


Flask
-----

Just add  `pypugjs.ext.jinja.PyPugJSExtension` as extension to the environment of the app

.. code:: python

    app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

Have a look at a lil example here: https://github.com/kakulukia/pypugjs/tree/master/examples/flask

Pyramid
-------

Adjust your "your_project/__init__.py" and add the following line somewhere to in the main() function

.. code:: python

    config.include('pypugjs.ext.pyramid')


Tornado Templates
-----------------

Append this after importing tornado.template

.. code:: python

    from tornado import template
    from pypugjs.ext.tornado import patch_tornado
    patch_tornado()

    (...)
