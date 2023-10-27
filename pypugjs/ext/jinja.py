import os

from jinja2.ext import Extension
from jinja2.runtime import Undefined
from markupsafe import Markup

import pypugjs.runtime
from pypugjs import Compiler as _Compiler
from pypugjs.runtime import attrs as _attrs, iteration, open
from pypugjs.utils import process

ATTRS_FUNC = '__pypugjs_attrs'
ITER_FUNC = '__pypugjs_iter'


def attrs(attrs, terse=False):
    return Markup(_attrs(attrs, terse, Undefined))


class Compiler(_Compiler):
    def __init__(self, node, **options):
        self.filename = options.pop('_filename')
        super().__init__(node, **options)
    
    def visitCodeBlock(self, block):
        if self.mixing > 0:
            if self.mixing > 1:
                caller_name = '__pypugjs_caller_%d' % self.mixing
            else:
                caller_name = 'caller'
            self.buffer(
                '{%% if %s %%}%s %s() %s{%% endif %%}'
                % (
                    caller_name,
                    self.variable_start_string,
                    caller_name,
                    self.variable_end_string,
                )
            )
        else:
            self.buffer('{%% block %s %%}' % block.name)
            if block.mode == 'append':
                self.buffer(
                    '%ssuper()%s'
                    % (self.variable_start_string, self.variable_end_string)
                )
            self.visitBlock(block)
            if block.mode == 'prepend':
                self.buffer(
                    '%ssuper()%s'
                    % (self.variable_start_string, self.variable_end_string)
                )
            self.buffer('{% endblock %}')

    def visitMixin(self, mixin):
        self.mixing += 1
        if not mixin.call:
            self.buffer('{%% macro %s(%s) %%}' % (mixin.name, mixin.args))
            self.visitBlock(mixin.block)
            self.buffer('{% endmacro %}')
        elif mixin.block:
            if self.mixing > 1:
                self.buffer('{%% set __pypugjs_caller_%d=caller %%}' % self.mixing)
            self.buffer('{%% call %s(%s) %%}' % (mixin.name, mixin.args))
            self.visitBlock(mixin.block)
            self.buffer('{% endcall %}')
        else:
            self.buffer(
                '%s%s(%s)%s'
                % (
                    self.variable_start_string,
                    mixin.name,
                    mixin.args,
                    self.variable_end_string,
                )
            )
        self.mixing -= 1

    def visitAssignment(self, assignment):
        self.buffer('{%% set %s = %s %%}' % (assignment.name, assignment.val))

    def visitCode(self, code):
        if code.buffer:
            val = code.val.lstrip()
            val = self.var_processor(val)
            self.buf.append(
                '%s%s%s%s'
                % (
                    self.variable_start_string,
                    val,
                    '|escape' if code.escape else '',
                    self.variable_end_string,
                )
            )
        else:
            self.buf.append('{%% %s %%}' % code.val)

        if code.block:
            # if not code.buffer: self.buf.append('{')
            self.visit(code.block)
            # if not code.buffer: self.buf.append('}')

            if not code.buffer:
                codeTag = code.val.strip().split(' ', 1)[0]
                if codeTag in self.auto_close_code:
                    self.buf.append('{%% end%s %%}' % codeTag)

    def visitEach(self, each):
        self.buf.append(
            "{%% for %s in %s(%s,%d) %%}"
            % (','.join(each.keys), ITER_FUNC, each.obj, len(each.keys))
        )
        self.visit(each.block)
        self.buf.append('{% endfor %}')

    def visitInclude(self, node):
        path = self.format_path(node.path)
        if path.startswith('/'):
            if not self.options.get('basedir'):
                raise Exception("Include path '{}' requires basedir option to resolve.".format(path))

            else:
                path = os.path.join(self.options["basedir"], path)
        else:
            if not self.filename:
                raise Exception("Include path '{}' requires filename to resolve.".format(path))

            else:
                path = os.path.join(os.path.dirname(self.filename), path)

        if not os.path.exists(path):
            raise Exception("Include path '{}' does not exist.".format(path))

        with open(path, 'r') as fd:
            src = fd.read()

        if not path.endswith(self.extension):
            self.buf.append(src)

        else:
            parser = pypugjs.parser.Parser(src)
            block = parser.parse()
            self.visit(block)
            
    def attributes(self, attrs):
        return "%s%s(%s)%s" % (
            self.variable_start_string,
            ATTRS_FUNC,
            attrs,
            self.variable_end_string,
        )


class PyPugJSExtension(Extension):
    options = {}
    file_extensions = '.pug'

    def __init__(self, environment):
        super(PyPugJSExtension, self).__init__(environment)

        environment.extend(pypugjs=self)

        environment.globals[ATTRS_FUNC] = attrs
        environment.globals[ITER_FUNC] = iteration
        self.variable_start_string = environment.variable_start_string
        self.variable_end_string = environment.variable_end_string
        self.options["variable_start_string"] = environment.variable_start_string
        self.options["variable_end_string"] = environment.variable_end_string

    def preprocess(self, source, name, filename=None):
        loader = self.environment.loader
        try:
            # we're in a Flask app
            loader = loader.app.jinja_loader
        except AttributeError:
            pass
            
        if hasattr(loader, 'searchpath') and len(loader.searchpath):
            self.options["basedir"] = loader.searchpath[0]

        if filename:
            self.options["_filename"] = filename

        if (not name) or (os.path.splitext(name)[1] not in self.file_extensions):
            return source
        else:
            return process(source, filename=name, compiler=Compiler, **self.options)
