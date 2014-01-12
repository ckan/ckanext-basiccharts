import os
import inspect
import pylons.config as config

import ckan.plugins as p


class TestBasicCharts(object):

    @classmethod
    def setup_class(cls):
        p.load('basiccharts')
        cls.plugin = p.get_plugin('basiccharts')

    @classmethod
    def teardown_class(cls):
        p.unload('basiccharts')

    def test_plugin_templates_path_is_added_to_config(self):
        filename = inspect.getfile(inspect.currentframe())
        path = os.path.dirname(filename)
        templates_path = os.path.abspath(path + "/../theme/templates")

        assert templates_path in config['extra_template_paths'], templates_path

    def test_plugin_isnt_iframed(self):
        iframed = self.plugin.info().get('iframed', True)
        assert not iframed, 'Plugin should not be iframed'
