from pypugjs.ext.mako import preprocessor

try:
    from pyramid_mako import MakoRendererFactory
    from pyramid_mako import parse_options_from_settings
    from pyramid_mako import PkgResourceTemplateLookup

    is_pyramid_mako = True
except ImportError:
    from pyramid import mako_templating

    is_pyramid_mako = False


class PyPugJSRenderer(object):
    """
    The PugJS renderer
    """

    def __init__(self, info):
        info.settings['mako.preprocessor'] = preprocessor
        self.makoRenderer = mako_templating.renderer_factory(info)

    def __call__(self, value, system):
        return self.makoRenderer(value, system)


def add_pugjs_renderer(config, extension, mako_settings_prefix='mako.'):
    renderer_factory = MakoRendererFactory()
    config.add_renderer(extension, renderer_factory)

    def register():
        settings = config.registry.settings
        settings['{0}preprocessor'.format(mako_settings_prefix)] = preprocessor

        opts = parse_options_from_settings(
            settings, mako_settings_prefix, config.maybe_dotted
        )
        lookup = PkgResourceTemplateLookup(**opts)

        renderer_factory.lookup = lookup

    config.action(('pug-renderer', extension), register)


def includeme(config):
    if not is_pyramid_mako:
        # looks broken, but i dont know how to fix
        config.add_renderer(".pug", renderer)  # noqa
    else:
        config.add_directive('add_pugjs_renderer', add_pugjs_renderer)
        config.add_pugjs_renderer('.pug')
