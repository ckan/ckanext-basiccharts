import os
import inspect
import mock
import nose.tools
import pylons.config as config

import ckan.plugins as p

import ckanext.basiccharts


class TestBaseChart(object):

    @classmethod
    def setup_class(cls):
        cls.plugin = ckanext.basiccharts.plugin.BaseChart()

    @nose.tools.raises(p.PluginNotFoundException)
    def test_plugin_cant_be_loaded(self):
        p.load('basechart')

    def test_chart_type(self):
        assert self.plugin.CHART_TYPE == 'base', '"CHART_TYPE" should be "base"'

    def test_group_by_is_required(self):
        assert self.plugin.GROUP_BY_IS_REQUIRED == False, '"GROUP_BY_IS_REQUIRED" should be false'

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
        schema = self.plugin.info()['schema']
        assert schema is not None, 'Plugin should define schema'

    def test_schema_has_y_axis(self):
        schema = self.plugin.info()['schema']
        assert schema.get('y_axis') is not None, 'Schema should define "y_axis"'

    def test_schema_y_axis_is_required(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['y_axis'], '"y_axis" should be required'

    def test_schema_has_group_by(self):
        schema = self.plugin.info()['schema']
        assert schema.get('group_by') is not None, 'Schema should define "group_by"'

    def test_schema_group_by_doesnt_validate_if_group_by_isnt_required(self):
        original_value = self.plugin.GROUP_BY_IS_REQUIRED
        self.plugin.GROUP_BY_IS_REQUIRED = False
        schema = self.plugin.info()['schema']
        self.plugin.GROUP_BY_IS_REQUIRED = original_value
        ignore_missing = p.toolkit.get_validator('ignore_missing')
        assert ignore_missing in schema['group_by'], '"group_by" should ignore missing'

    def test_schema_group_by_is_required_if_group_by_is_required(self):
        original_value = self.plugin.GROUP_BY_IS_REQUIRED
        self.plugin.GROUP_BY_IS_REQUIRED = True
        schema = self.plugin.info()['schema']
        self.plugin.GROUP_BY_IS_REQUIRED = original_value
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['group_by'], '"group_by" should be required'

    def test_schema_has_show_legends(self):
        schema = self.plugin.info()['schema']
        assert schema.get('show_legends') is not None, 'Schema should define "show_legends"'

    def test_schema_show_legends_doesnt_validate(self):
        schema = self.plugin.info()['schema']
        ignore_missing = p.toolkit.get_validator('ignore_missing')
        assert ignore_missing in schema['show_legends'], '"show_legends" should ignore missing'

    def test_plugin_isnt_iframed(self):
        iframed = self.plugin.info().get('iframed', True)
        assert not iframed, 'Plugin should not be iframed'

    def test_plugin_is_filterable(self):
        filterable = self.plugin.info().get('filterable', False)
        assert filterable, 'Plugin should be filterable'

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
    def test_setup_template_variables_adds_show_legends_as_true_if_it_was_defined(self, _):
        template_variables = self._setup_template_variables(resource_view={'show_legends': 'True'})

        show_legends = template_variables['resource_view']['show_legends']
        assert show_legends is True, show_legends

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_show_legends_as_false_if_it_was_undefined(self, _):
        template_variables = self._setup_template_variables(resource_view={})

        show_legends = template_variables['resource_view']['show_legends']
        assert show_legends is False, show_legends

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
    def test_setup_template_variables_adds_chart_type(self, _):
        template_variables = self._setup_template_variables()
        assert 'chart_type' in template_variables
        assert template_variables['chart_type'] == self.plugin.CHART_TYPE

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_defines_group_by_is_required_correctly(self, _):
        template_variables = self._setup_template_variables()
        assert 'group_by_is_required' in template_variables
        assert template_variables['group_by_is_required'] == self.plugin.GROUP_BY_IS_REQUIRED

    def _setup_template_variables(self, resource={'id': 'id'}, resource_view={}):
        context = {}
        data_dict = {
            'resource': resource,
            'resource_view': resource_view
        }
        return self.plugin.setup_template_variables(context, data_dict)


class TestLineChart(TestBaseChart):

    @classmethod
    def setup_class(cls):
        p.load('linechart')
        cls.plugin = p.get_plugin('linechart')

    @classmethod
    def teardown_class(cls):
        p.unload('linechart')

    def test_schema_has_x_axis(self):
        schema = self.plugin.info()['schema']
        assert schema.get('x_axis') is not None, 'Schema should define "x_axis"'

    def test_schema_x_axis_is_required(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['x_axis'], '"x_axis" should be required'

    def test_chart_type(self):
        assert self.plugin.CHART_TYPE == 'lines', '"CHART_TYPE" should be "lines"'


class TestBarChart(TestLineChart):

    @classmethod
    def setup_class(cls):
        p.load('barchart')
        cls.plugin = p.get_plugin('barchart')

    @classmethod
    def teardown_class(cls):
        p.unload('barchart')

    def test_schema_has_horizontal(self):
        schema = self.plugin.info()['schema']
        assert schema.get('horizontal') is not None, 'Schema should define "horizontal"'

    def test_schema_horizontal_doesnt_validate(self):
        schema = self.plugin.info()['schema']
        ignore_missing = p.toolkit.get_validator('ignore_missing')
        assert ignore_missing in schema['horizontal'], '"horizontal" should ignore missing'

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_horizontal_as_true_if_it_was_defined(self, _):
        template_variables = self._setup_template_variables(resource_view={'horizontal': 'True'})

        horizontal = template_variables['resource_view']['horizontal']
        assert horizontal is True, horizontal

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_horizontal_as_false_if_it_was_undefined(self, _):
        template_variables = self._setup_template_variables(resource_view={})

        horizontal = template_variables['resource_view']['horizontal']
        assert horizontal is False, horizontal

    def test_chart_type(self):
        assert self.plugin.CHART_TYPE == 'bars', '"CHART_TYPE" should be "bars"'


class TestPieChart(TestBaseChart):

    @classmethod
    def setup_class(cls):
        p.load('piechart')
        cls.plugin = p.get_plugin('piechart')

    @classmethod
    def teardown_class(cls):
        p.unload('piechart')

    def test_chart_type(self):
        assert self.plugin.CHART_TYPE == 'pie', '"CHART_TYPE" should be "pie"'

    def test_group_by_is_required(self):
        assert self.plugin.GROUP_BY_IS_REQUIRED == True, '"GROUP_BY_IS_REQUIRED" should be true'
