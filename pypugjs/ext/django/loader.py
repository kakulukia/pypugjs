from __future__ import absolute_import

import os
import re

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader
from django.utils.functional import cached_property

from pypugjs.utils import process
from .compiler import Compiler


class Loader(BaseLoader):
    is_usable = True

    def __init__(self, engine, loaders, dirs=None):
        self.dirs = dirs
        self.engine = engine
        self.template_cache = {}
        self._loaders = loaders
        self.debug = (
            settings.TEMPLATE_DEBUG
            if hasattr(settings, 'TEMPLATE_DEBUG')
            else settings.DEBUG
        )

    @cached_property
    def loaders(self):
        return self.engine.get_template_loaders(self._loaders)

    def reset(self):
        """ Empty the template cache. """
        self.template_cache.clear()

    def get_dirs(self):
        return self.dirs if self.dirs is not None else self.engine.dirs

    def include_pug_sources(self, contents):
        """Lets fetch top level pug includes to enable  mixins"""
        match = re.search(r'^include (.*)$', contents, re.MULTILINE)
        if match:
            mixin_name = match.groups()[0]
            origin = [o for o in self.get_template_sources(mixin_name)][0]
            template = origin.loader.get_contents(origin)
            template = self.include_pug_sources(template)
            contents = re.sub(r'^include (.*)$', template, contents, flags=re.MULTILINE)
        return contents

    def get_contents(self, origin):

        if os.path.splitext(origin.template_name)[1] in ('.pug', '.jade'):
            contents = origin.loader.get_contents(origin)
            contents = self.include_pug_sources(contents)
            contents = process(
                contents, filename=origin.template_name, compiler=Compiler
            )
        else:
            contents = origin.loader.get_contents(origin)

        return contents

    def get_template_sources(self, template_name):
        """
        Only forward the internal loaders sources.
        """
        for loader in self.loaders:
            for origin in loader.get_template_sources(template_name):
                yield origin

    def get_template(self, template_name, skip=None, **kwargs):
        """
        Call self.get_template_sources() and return a Template object for
        the first template matching template_name. If skip is provided, ignore
        template origins in skip. This is used to avoid recursion during
        template extending.

        This version includes a little caching. The not existing templates are
        also cached because this resulted in a major loading issued in a
        wagtail admin instance.
        """
        template = self.template_cache.get(template_name)
        if not template or self.debug:
            try:
                template = super(Loader, self).get_template(template_name, skip)
            # TODO: Change IOError to FileNotFoundError after future==0.17.0
            except IOError:
                template = 'TemplateDoesNotExist'
            self.template_cache[template_name] = template

        if template == 'TemplateDoesNotExist':
            raise TemplateDoesNotExist(template_name)

        return template
