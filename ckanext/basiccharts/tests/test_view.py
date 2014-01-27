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
        schema = self.plugin.schema()
        assert schema is not None, 'Plugin should define schema'

    def test_schema_has_chart_type(self):
        schema = self.plugin.schema()
        assert schema.get('chart_type') is not None, 'Schema should define "chart_type"'

    def test_schema_chart_type_is_required(self):
        schema = self.plugin.schema()
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['chart_type'], '"chart_type" should be required'

    def test_schema_has_filter_field(self):
        schema = self.plugin.schema()
        assert schema.get('filter_field') is not None, 'Schema should define "filter_field"'

    def test_schema_filter_field_doesnt_validate(self):
        schema = self.plugin.schema()
        assert len(schema['filter_field']) == 0, 'Schema shouldn\'t have validators'

    def test_schema_has_filter_value(self):
        schema = self.plugin.schema()
        assert schema.get('filter_value') is not None, 'Schema should define "filter_value"'

    def test_schema_filter_value_doesnt_validate(self):
        schema = self.plugin.schema()
        assert len(schema['filter_value']) == 0, 'Schema shouldn\'t have validators'

    def test_schema_has_y_axis(self):
        schema = self.plugin.schema()
        assert schema.get('y_axis') is not None, 'Schema should define "y_axis"'

    def test_schema_y_axis_is_required(self):
        schema = self.plugin.schema()
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['y_axis'], '"y_axis" should be required'

    def test_schema_has_series(self):
        schema = self.plugin.schema()
        assert schema.get('series') is not None, 'Schema should define "series"'

    def test_schema_series_is_required(self):
        schema = self.plugin.schema()
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['series'], '"series" should be required'

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_resource(self, _):
        resource = {
          'id': 'resource_id',
          'other_attribute': 'value'
        }

        template_variables = self._setup_template_variables(resource)

        assert 'resource' in template_variables
        assert template_variables['resource'] == resource

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_resource_view(self, _):
        resource_view = {
          'id': 'resource_id',
          'other_attribute': 'value'
        }

        template_variables = \
          self._setup_template_variables(resource_view=resource_view)

        assert 'resource_view' in template_variables
        assert template_variables['resource_view'] == resource_view

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

    def _setup_template_variables(self, resource={'id': 'id'}, resource_view={}):
        context = {}
        data_dict = {
            'resource': resource,
            'resource_view': resource_view
        }
        return self.plugin.setup_template_variables(context, data_dict)


class TestLineChart(TestBasicCharts):

    @classmethod
    def setup_class(cls):
        p.load('basiccharts')
        p.load('linechart')
        cls.plugin = p.get_plugin('linechart')

    @classmethod
    def teardown_class(cls):
        p.unload('linechart')
        p.unload('basiccharts')

    def test_plugin_isnt_iframed(self):
        iframed = self.plugin.info().get('iframed', True)
        assert not iframed, 'Plugin should not be iframed'

    def test_schema_has_x_axis(self):
        schema = self.plugin.info()['schema']
        assert schema.get('x_axis') is not None, 'Schema should define "x_axis"'

    def test_schema_x_axis_is_required(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['x_axis'], '"x_axis" should be required'

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_define_correct_chart_type(self, _):
        template_variables = self._setup_template_variables()
        assert 'chart_type' in template_variables
        assert template_variables['chart_type'] == 'line'

