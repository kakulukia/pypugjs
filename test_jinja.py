from __future__ import print_function

import pypugjs
from pypugjs.ext.jinja import Compiler

a = pypugjs.Parser(
    '''!!! 5
html
    head: title Hello from flask
    body(attr="2" ba=2)
        if name
            h1(class="red") Hello
                span #{ name }
            span.description #{ name|capitalize } is a great name!
        else
            h1 Hello World!'''
)
block = a.parse()
compiler = Compiler(block)
print(compiler.compile())
# OUT: <!DOCTYPE html>
# OUT: <html{{__pypugjs_attrs(terse=True)}}>
# OUT:   <head{{__pypugjs_attrs(terse=True)}}>
# OUT:     <title{{__pypugjs_attrs(terse=True)}}>Hello from flask
# OUT:     </title>
# OUT:   </head>
# OUT:   <body{{__pypugjs_attrs(terse=True, attrs=[('attr',("2" ba=2))])}}>{% if  name %}
# OUT:     <h1{{__pypugjs_attrs(terse=True, attrs=[('class', (("red")))])}}>Hello {{name|escape}}
# OUT:     </h1><span{{__pypugjs_attrs(terse=True, attrs=[('class', (('description')))])}}>{{name|capitalize}}
# is a great name!</span>{% else %}
# OUT:     <h1{{__pypugjs_attrs(terse=True)}}>Hello World!
# OUT:     </h1>{% endif %}
# OUT:   </body>
# OUT: </html>
