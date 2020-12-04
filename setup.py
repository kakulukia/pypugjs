#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("pypugjs", "__init__.py")


readme = open('README.rst').read()
history = open('docs/HISTORY.rst').read().replace('.. :changelog:', '')
url = 'https://github.com/kakulukia/pypugjs'

setup(
    name='pypugjs',
    version=version,
    description="PugJS syntax template adapter for Django, Jinja2, Mako and Tornado templates",
    long_description=readme + '\n\n' + history,
    author='Andy Grabow',
    author_email='andy@freilandkiwis.de',
    license='MIT',
    keywords=['pug', 'pugjs', 'template', 'converter'],
    url=url,
    download_url=url + '/tarball/' + version,
    packages=find_packages(),
    entry_points={'console_scripts': ['pypugjs = pypugjs.convert:convert_file']},
    install_requires=['six', 'chardet'],
    tests_require=[
        'nose',
        'django',
        'jinja2',
        'tornado',
        'pyramid >= 1.5',
        'pyramid-mako',
        'mako',
    ],
    # include_package_data=True,
    # zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
