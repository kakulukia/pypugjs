"""Test that the Jinja2 |escape filter applies to the full expression.

Regression tests for two related bugs where |escape was appended as a raw
suffix, causing Jinja2 filter precedence to bind it to the wrong operand:

1. Buffered code: `= expr or fallback` compiled to
   ``{{ expr or fallback|escape }}`` — |escape only bound to `fallback`.
   (Fixed in visitCode, PR #90.)

2. Interpolation: `#{a - 10}` compiled to
   ``{{ a - 10|escape }}`` — |escape bound to `10`, producing a Markup
   string, so the subtraction became `int - Markup` (TypeError).
   (Fixed in interpolate.)

The fix wraps the expression in parentheses so |escape applies to the
entire result.
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


class TestBufferedCodeEscape:
    """Ensure |escape applies to the whole expression in `= expr` output."""

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


class TestInterpolationEscape:
    """Ensure |escape applies to the whole expression in #{} interpolation."""

    def test_subtraction(self):
        result = _compile('p #{a - 10} more')
        assert '(a - 10)|escape' in result

    def test_or_expression(self):
        result = _compile('p #{a or b}')
        assert '(a or b)|escape' in result

    def test_simple_var(self):
        result = _compile('p #{name}')
        assert '(name)|escape' in result

    def test_subtraction_renders_correctly(self):
        compiled = _compile('p #{a - 10} more')
        html = _render(compiled, a=42)
        assert '32 more' in html

    def test_interpolation_xss(self):
        compiled = _compile('p #{a or b}')
        html = _render(compiled, a='<script>xss</script>', b='safe')
        assert '&lt;script&gt;' in html
        assert '<script>' not in html

    def test_unescaped_interpolation(self):
        """!{} should not add |escape or parentheses."""
        result = _compile('p !{a - 10}')
        assert '|escape' not in result
        assert 'a - 10' in result

    def test_multiple_interpolations(self):
        result = _compile('p #{a + b} and #{c - d}')
        assert '(a + b)|escape' in result
        assert '(c - d)|escape' in result
