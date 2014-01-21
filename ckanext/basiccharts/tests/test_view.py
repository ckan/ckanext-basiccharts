import os
import inspect
import mock
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

    def test_can_view_only_if_datastore_is_active(self):
        active_datastore_data_dict = {
            'resource': { 'datastore_active': True }
        }
        inactive_datastore_data_dict = {
            'resource': { 'datastore_active': False }
        }
        assert self.plugin.can_view(active_datastore_data_dict)
        assert not self.plugin.can_view(inactive_datastore_data_dict)

    def test_schema_exists(self):
        schema = self.plugin.info().get('schema')
        assert schema is not None, 'Plugin should define schema'

    def test_schema_has_xAxis_and_yAxis(self):
        schema = self.plugin.info()['schema']
        assert schema.get('xAxis') is not None, 'Scheme should define "xAxis"'
        assert schema.get('yAxis') is not None, 'Scheme should define "yAxis"'

    def test_schema_xAxis_and_yAxis_are_required(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['xAxis'], '"xAxis" should be required'
        assert not_empty in schema['yAxis'], '"yAxis" should be required'

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_xAxis_and_yAxis(self, _):
        resource_view = {
          'xAxis': 'theXAxis',
          'yAxis': 'theYAxis'
        }

        template_variables = self._setup_template_variables('resource_id',
                resource_view)

        xAxis = template_variables.get('xAxis')
        yAxis = template_variables.get('yAxis')
        assert xAxis == 'theXAxis'
        assert yAxis == 'theYAxis'

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_fields_without_the_id(self, get_action):
        fields = [
          {'id': '_id', 'type': 'int4'},
          {'id': 'price', 'type': 'numeric'},
        ]
        expected_fields = [{'value': 'price'}]

        get_action.return_value.return_value = {
          'fields': fields,
          'records': {}
        }
        template_variables = self._setup_template_variables()

        returned_fields = template_variables.get('fields')
        assert returned_fields is not None
        assert returned_fields == expected_fields

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_records(self, get_action):
        records = ['the', 'records']

        get_action.return_value.return_value = {
          'fields': {},
          'records': records
        }
        template_variables = self._setup_template_variables()

        returned_records = template_variables.get('records')
        assert returned_records is not None
        assert returned_records == records

    def _setup_template_variables(self, resource_id='id', resource_view={}):
        context = {}
        data_dict = {
            'resource': { 'id': resource_id },
            'resource_view': resource_view
        }
        return self.plugin.setup_template_variables(context, data_dict)
