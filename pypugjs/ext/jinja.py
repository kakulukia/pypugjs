import pypugjs.runtime
import os
from jinja2.ext import Extension

from pypugjs import Compiler as _Compiler
from pypugjs.runtime import attrs as _attrs, iteration
from jinja2 import Markup
from jinja2.runtime import Undefined
from pypugjs.utils import process


ATTRS_FUNC = '__pypugjs_attrs'
ITER_FUNC = '__pypugjs_iter'


def attrs(attrs, terse=False):
    return Markup(_attrs(attrs, terse, Undefined))


class Compiler(_Compiler):

    def _wrap_var(self, var):
        return f'{self.variable_start_string}{var}{self.variable_end_string}'

    def visit_code_block(self, block):
        if self.mixing > 0:
            if self.mixing > 1:
                caller_name = f'__pypugjs_caller_{self.mixing}'
            else:
                caller_name = 'caller'
            self.buffer(
                f'{{% if {caller_name} %}}'
                f'{self._wrap_var(caller_name + "()")}'
                f'{{% endif %}}')
        else:
            self.buffer(f'{{% block {block.name} %}}')
            if block.mode == 'append':
                self.buffer(self._wrap_var('super()'))
            self.visitBlock(block)
            if block.mode == 'prepend':
                self.buffer(self._wrap_var('super()'))
            self.buffer('{% endblock %}')

    def visit_mixin(self, mixin):
        self.mixing += 1
        if not mixin.call:
            self.buffer(f'{{% macro {mixin.name}({mixin.args}) %}}')
            self.visitBlock(mixin.block)
            self.buffer('{% endmacro %}')
        elif mixin.block:
            if self.mixing > 1:
                self.buffer(
                    f'{{% set __pypugjs_caller_{self.mixing}=caller %}}')
            self.buffer(f'{{% call {mixin.name}({mixin.args}) %}}')
            self.visitBlock(mixin.block)
            self.buffer('{% endcall %}')
        else:
            self.buffer(self._wrap_var(f'{mixin.name}({mixin.args})'))
        self.mixing -= 1

    def visit_assignment(self, assignment):
        self.buffer(f'{{% set {assignment.name} = {assignment.val} %}}')

    def visit_code(self, code):
        if code.buffer:
            val = code.val.lstrip()
            val = self.var_processor(val)
            self.buf.append(
                self._wrap_var(f'{val}{"|escape" if code.escape else ""}'))
        else:
            self.buf.append(f'{{% {code.val} %}}')

        if code.block:
            self.visit(code.block)
            if not code.buffer:
                code_tag = code.val.strip().split(' ', 1)[0]
                if code_tag in self.autocloseCode:
                    self.buf.append(f'{{% end{code_tag} %}}')

    def visit_each(self, each):
        self.buf.append(f'{{% for {",".join(each.keys)} in '
                        f'{ITER_FUNC}({each.obj}, {len(each.keys)}) %}}')
        self.visit(each.block)
        self.buf.append('{% endfor %}')

    def visit_include(self, node):
        path = self.format_path(node.path)
        fullpath = ''
        searchpath = self.options.get('searchpath', [''])
        for basedir in searchpath:
            if os.path.exists(os.path.join(basedir, path)):
                fullpath = os.path.join(basedir, path)
                break
        if not fullpath:
            raise FileNotFoundError(
                f'No such file {path} in Jinja loader searchpath')
        with open(fullpath) as f:
            src = f.read()
        parser = pypugjs.parser.Parser(src)
        block = parser.parse()
        self.visit(block)

    def attributes(self, attrs_):
        return self._wrap_var(f'{ATTRS_FUNC}({attrs_})')

    visitCodeBlock = visit_code_block
    visitMixin = visit_mixin
    visitAssignment = visit_assignment
    visitCode = visit_code
    visitEach = visit_each
    visitInclude = visit_include


class PyPugJSExtension(Extension):
    options = {}
    file_extensions = '.pug'

    def __init__(self, environment):
        super().__init__(environment)
        environment.extend(pypugjs=self)
        environment.globals[ATTRS_FUNC] = attrs
        environment.globals[ITER_FUNC] = iteration
        self.variable_start_string = environment.variable_start_string
        self.variable_end_string = environment.variable_end_string
        self.options['variable_start_string'] = (
            environment.variable_start_string)
        self.options['variable_end_string'] = environment.variable_end_string

    def preprocess(self, source, name, filename=None):
        if 'include' in source:
            loader = self.environment.loader
            try:
                # This is necessary in a Flask app
                loader = loader.app.jinja_loader
            except AttributeError:
                pass
            self.options['searchpath'] = loader.searchpath

        if (not name or
           (name and not os.path.splitext(name)[1] in self.file_extensions)):
            return source
        return process(
            source, filename=name, compiler=Compiler, **self.options)
