import codecs
import os
import sys
from optparse import OptionParser

from pypugjs.utils import process


def convert_file():
    support_compilers_list = [
        'html',
        'django',
        'jinja',
        'underscore',
        'mako',
        'tornado',
    ]

    usage = "usage: %prog [options] [file [output]]"
    parser = OptionParser(usage)
    parser.add_option(
        "-o", "--output", dest="output", help="Write output to FILE", metavar="FILE"
    )
    parser.add_option(
        "-c",
        "--compiler",
        dest="compiler",
        choices=support_compilers_list,
        default='html',
        help="Compiler to use (default: html)",
    )
    parser.add_option(
        "-e",
        "--ext",
        dest="extension",
        help="Set import/extends default file extension",
        metavar="FILE",
    )

    options, args = parser.parse_args()

    compiler_name = options.compiler

    # Compiler jetzt dynamisch laden
    try:
        compiler_module = __import__(
            f'pypugjs.ext.{compiler_name}', fromlist=['pypugjs']
        )
        compiler_class = compiler_module.Compiler
    except ImportError:
        sys.exit(
            f"Compiler '{compiler_name}' not available. Please install it, or use one of: {', '.join(support_compilers_list)}"
        )

    file_output = options.output or (args[1] if len(args) > 1 else None)

    if options.extension:
        extension = '.%s' % options.extension
    elif options.output:
        extension = os.path.splitext(options.output)[1]
    else:
        extension = None

    import six

    if len(args) >= 1:
        template = codecs.open(args[0], 'r', encoding='utf-8').read()
    elif six.PY3:
        template = sys.stdin.read()
    else:
        template = codecs.getreader('utf-8')(sys.stdin).read()

    output = process(
        template,
        compiler=compiler_class,
        staticAttrs=True,
        extension=extension,
    )

    if file_output:
        with codecs.open(file_output, 'w', encoding='utf-8') as outfile:
            outfile.write(output)
    elif six.PY3:
        sys.stdout.write(output)
    else:
        codecs.getwriter('utf-8')(sys.stdout).write(output)


if __name__ == '__main__':
    convert_file()
