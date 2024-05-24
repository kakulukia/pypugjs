PyPugJS |PyPiPackage| |BuildStatus| |Coverage|
===================================================

.. |PyPiPackage| image:: https://badge.fury.io/py/pypugjs.svg
   :target: https://badge.fury.io/py/pypugjs

.. |BuildStatus| image:: https://github.com/kakulukia/pypugjs/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/kakulukia/pypugjs/actions/workflows/tests.yml

.. |Coverage| image:: https://codecov.io/gh/kakulukia/pypugjs/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/kakulukia/pypugjs

**PyPugJS is a fork of** `PyJade <http://github.com/syrusakbary/pyjade>`_
**with the name Jade changed to** `PugJS <https://github.com/pugjs/pug>`_.

**Additional disclaimer:** Since the original pypugjs died i took the liberty to keep it alive, because
since starting to work with the jade compiler for node I hate writing HTML and want to continue using it in my Django projects.
I will keep the existing non Django stuff inside the project, but I cannot support anything other since I'm not actively using
it nor will be in the foreseeable future. Tornado, Mako etc. support will be welcome tho!

PyPugJS is a high performance port of PugJS for python, that converts any .pug source into different
Template-languages (Django, Jinja2, Mako or Tornado).

UTILITIES
=========
To simply output the conversion to your console::

    pypugjs [-c django|jinja|mako|tornado] input.pug [output.html]

INSTALLATION
============

To install pypugjs::

    pip install pypugjs

Now simply **name your templates with a `.pug` extension** and this PugJS compiler
will do the rest.  Any templates with other extensions will not be compiled
with the pypugjs compiler.

`Framework specific installation instructions <docs/installation.rst>`_

Syntax
======

Generally the same as the PugJS Node module (except of cases and several other features, which are not implemented)
https://github.com/pugjs/pug/blob/master/README.md


Example
-------

This code

.. code:: pug

    !!! 5
    html(lang="en")
      head
        title= pageTitle
        script(type='text/javascript').
          if (foo) {
             bar()
          }
      body
        h1.title PugJS - node template engine
        #container
          if youAreUsingPugJS
            p You are amazing
          else
            p Get on it!


Converts to

.. code:: html

    <!DOCTYPE html>
    <html lang="en">
      <head>
        <title>{{pageTitle}}</title>
        <script type='text/javascript'>
          if (foo) {
             bar()
          }
        </script>
      </head>
      <body>
        <h1 class="title">PugJS - node template engine</h1>
        <div id="container">
          {%if youAreUsingPugJS%}
            <p>You are amazing</p>
          {%else%}
            <p>Get on it!</p>
          {%endif%}
        </div>
      </body>
    </html>

Convert existing templates online with the `HTML2Jade converter <http://www.html2jade.org/>`_.


Register filters
================

If you want to register a function as a filter, you only have to
decorate the function with ``pypugjs.register_filter("filter_name")``

.. code:: python

    import pypugjs

    @pypugjs.register_filter('capitalize')
    def capitalize(text, ast):
      return text.capitalize()


Notable Features
===================

Adding conditional classes:

.. code:: pug

    a(class={'active-class': True, 'another': False})

Define mixins like this *mixins/foo.pug*:

.. code:: pug

    mixin foo(data)
      .foo {{ data }}

And use them in your templates like this:

.. code:: pug

    include mixins/foo.pug

    div
      +foo(data)


*Mixins might not work, depending on the used Framework.
The following have been reported as broken:*

* Django (v4.2)


TESTING
=======

To start the testsuite, start the following commands::

    make init
    make test

TODOs and BUGS
==============
See: https://github.com/kakulukia/pypugjs/issues

`ChangeLog <docs/HISTORY.rst>`_
