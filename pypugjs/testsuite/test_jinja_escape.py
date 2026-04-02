"""Test that the Jinja2 |escape filter applies to the full expression.

Regression test for a bug where `= expr or fallback` compiled to
``{{ expr or fallback|escape }}``.  Due to Jinja2 filter precedence,
|escape only bound to `fallback`, leaving `expr` unescaped (XSS).
The fix wraps the expression in parentheses: ``{{ (expr or fallback)|escape }}``.
"""

from jinja2 import Environment

from pypugjs.ext.jinja import Compiler
from pypugjs.parser import Parser


def _compile(src: str) -> str:
    block = Parser(src).parse()
    return Compiler(block).compile()


def _render(template_str: str, **ctx) -> str:
    env = Environment(autoescape=False)
    return env.from_string(template_str).render(**ctx)


class TestEscapeFilterPrecedence:
    """Ensure |escape applies to the whole expression, not just the last operand."""

    def test_simple_expression(self):
        result = _compile('p= text')
        assert '(text)|escape' in result

    def test_or_expression(self):
        result = _compile("p= a or 'fallback'")
        assert "(a or 'fallback')|escape" in result

    def test_or_expression_renders_escaped(self):
        compiled = _compile("p= a or 'fallback'")
        html = _render(compiled, a='<script>alert(1)</script>')
        assert '&lt;script&gt;' in html
        assert '<script>' not in html

    def test_or_expression_fallback_still_works(self):
        compiled = _compile("p= a or 'fallback'")
        assert 'fallback' in _render(compiled, a='')
        assert 'fallback' in _render(compiled, a=None)

    def test_unescaped_output_not_wrapped(self):
        """!= (unescaped) should not add |escape or parentheses."""
        result = _compile('p!= raw')
        assert '|escape' not in result
        assert '{{raw}}' in result

    def test_unbuffered_code_not_affected(self):
        """Unbuffered code (- var = ...) should not be wrapped."""
        result = _compile('- x = 1')
        assert '{%' in result
        assert '|escape' not in result
