from __future__ import absolute_import

import os
import re

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders import cached

from pypugjs.utils import process
from .compiler import Compiler


class Loader(cached.Loader):
    is_usable = True

    def include_pug_sources(self, contents):
        """Lets fetch top level pug includes to enable  mixins"""
        match = re.search(r'^include (.*)$', contents, re.MULTILINE)
        while match:
            mixin_name = match.groups()[0]
            origin = [o for o in self.get_template_sources(mixin_name)][0]
            template = origin.loader.get_contents(origin)
            template = self.include_pug_sources(template)
            contents = re.sub(r'^include (.*)$', template, contents, flags=re.MULTILINE)
            match = re.search(r'^include (.*)$', contents, re.MULTILINE)
        return contents

    def get_contents(self, origin):
        contents = origin.loader.get_contents(origin)
        if os.path.splitext(origin.template_name)[1] in ('.pug', '.jade'):
            contents = self.include_pug_sources(contents)
            contents = process(
                contents, filename=origin.template_name, compiler=Compiler
            )
        return contents

    def get_template(self, template_name, **kwargs):
        """
        Uses cache if debug is False, otherwise re-reads from file system.
        """
        if getattr(settings, 'TEMPLATE_DEBUG', settings.DEBUG):
            try:
                return super(cached.Loader, self).get_template(template_name, **kwargs)
            # TODO: Change IOError to FileNotFoundError after future==0.17.0
            except IOError:
                raise TemplateDoesNotExist(template_name)

        return super(Loader, self).get_template(template_name, **kwargs)
