.. :changelog:

History
-------

\*

* django docs: mention not to wrap with django's caching template loader
* updated history

5.8.1
+++++++
* mentioning the flask example in the installation section of the docs
* prevent endless recursion in Django template overriding

5.8.0
+++++++
* more details/docs for using pypugjs with jinja2
* fixed issue with Jinja Choiceloaders

5.7.2
+++++++
* Fix specifying attributes without commas.

5.7.1
+++++++
* code has been blacked

5.7.0
+++++++
* included encoding detection for template files

5.6.1
+++++++
* fixed documentation for the new translation call
* fixed typos in code
* added min Django version to the docs
* new release script

5.6.0
+++++++
* added enable_pug_translations call

5.5.1
+++++++
* fixed wrong exception handling for visitExtends

5.5.0
+++++++
* better caching for django template loader
* loader has been made compatible with django 1.11

5.4.0
+++++++
* added mixing to flask hello world
* Clean pipe inserts whitespace This allows for use of a single pipe character on a line to insert a whitespace before or after a tag.


5.3.0
+++++++
* fixed build script adding back all internal packages

5.2.0
+++++++
* fixed recursive import problem

5.1.5
+++++++
* addeded flake8 testing
* sorting out old Django version 1.11 and 2.0 are left for travis testing

5.1.4
+++++++
* better release script

5.1.3
+++++++
* cleanup / documentation
* extended makefile

5.1.2
+++++++

* added Makefile for testing, installing, releasing, linting ...
* added coverage reports
* package is mainly base on the cookiecutter package
* additional release helpers
* packages passes flake8 test


5.1.1
+++++++

* conditional classes feature (thx to paradoxxxzero)
* mixin support for jinja (matin)
* mixin support for django
* refactored the django tests to actually use the file loader
* some pep8 fixes


Authors
---------

* PyPugs was originally created as PyJade by Syrus Akbary in November 2011.
* It was then renamed maintained by Matan Noam Shavit
* Since I need it for my projects and hate coding plain HTML, I continued maintaining this package.
