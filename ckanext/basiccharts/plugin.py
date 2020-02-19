import os
import json
import collections

import ckan.plugins as p

not_empty = p.toolkit.get_validator('not_empty')
ignore_missing = p.toolkit.get_validator('ignore_missing')
ignore_empty = p.toolkit.get_validator('ignore_empty')


class BaseChart(p.SingletonPlugin):
    '''Class with methods common to all basic charts'''

    CHART_TYPE = 'base'
    GROUP_BY_IS_REQUIRED = False

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'basiccharts')

    def info(self):
        schema = {
            'y_axis': [not_empty],
            'show_legends': [ignore_missing]
        }

        if self.GROUP_BY_IS_REQUIRED:
            schema['group_by'] = [not_empty]
        else:
            schema['group_by'] = [ignore_missing]

        return {'icon': 'bar-chart',
                'filterable': True,
                'schema': schema,
                'iframed': False}

    def can_view(self, data_dict):
        return data_dict['resource'].get('datastore_active', False)

    def setup_template_variables(self, context, data_dict):
        resource = data_dict['resource']
        resource_view = data_dict['resource_view']
        resource_view['show_legends'] = bool(resource_view.get('show_legends'))

        fields = _get_fields_without_id(resource)

        return {'resource': resource,
                'resource_view': resource_view,
                'fields': fields,
                'group_by_is_required': self.GROUP_BY_IS_REQUIRED,
                'chart_type': self.CHART_TYPE}

    def view_template(self, context, data_dict):
        return 'basechart_view.html'

    def form_template(self, context, data_dict):
        return 'basechart_form.html'


class LineChart(BaseChart):

    CHART_TYPE = 'lines'

    def info(self):
        info = super(LineChart, self).info()
        info['schema']['x_axis'] = [not_empty]
        info['name'] = 'linechart'
        info['title'] = 'Line Chart'

        return info

    def form_template(self, context, data_dict):
        return 'linechart_form.html'


class BarChart(LineChart):

    CHART_TYPE = 'bars'

    def info(self):
        info = super(BarChart, self).info()
        info['schema']['horizontal'] = [ignore_missing]
        info['name'] = 'barchart'
        info['title'] = 'Bar Chart'

        return info

    def setup_template_variables(self, context, data_dict):
        superclass = super(BarChart, self)
        template_vars = superclass.setup_template_variables(context, data_dict)

        horizontal = bool(template_vars['resource_view'].get('horizontal'))
        template_vars['resource_view']['horizontal'] = horizontal

        return template_vars

    def form_template(self, context, data_dict):
        return 'barchart_form.html'


class PieChart(BaseChart):

    CHART_TYPE = 'pie'
    GROUP_BY_IS_REQUIRED = True

    def info(self):
        info = super(PieChart, self).info()
        info['name'] = 'piechart'
        info['title'] = 'Pie Chart'

        return info

    def form_template(self, context, data_dict):
        return 'piechart_form.html'


class BasicGrid(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.ITemplateHelpers)

    def get_helpers(self):
        return {'view_data': _view_data}

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        extra_template_paths = config.get('extra_template_paths', '')

        template_dir = os.path.join(rootdir, 'ckanext', 'basiccharts',
                                    'basicgrid', 'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                                                  extra_template_paths])

        p.toolkit.add_resource('basicgrid/resources', 'basicgrid')
        p.toolkit.add_resource('theme/public', 'basiccharts')

    def info(self):
        schema = {
            'fields': [ignore_missing, ignore_empty, convert_to_string,
                       validate_fields, unicode],
            'orientation': [ignore_missing],
        }

        return {'name': 'basicgrid',
                'title': 'Basic Grid',
                'icon': 'table',
                'iframed': False,
                'filterable': True,
                'schema': schema,
                }

    def can_view(self, data_dict):
        return True

    def view_template(self, context, data_dict):
        return 'basicgrid_view.html'

    def form_template(self, context, data_dict):
        return 'basicgrid_form.html'

    def setup_template_variables(self, context, data_dict):
        resource = data_dict['resource']
        fields = _get_fields_without_id(resource)
        resource_view = data_dict['resource_view']

        self._fields_as_string(resource_view)
        field_selection = json.dumps(
            [{'id': f['value'], 'text': f['value']} for f in fields]
        )

        orientations = [{'value': 'horizontal'}, {'value': 'vertical'}]

        return {'fields': fields,
                'field_selection': field_selection,
                'orientations': orientations}

    def _fields_as_string(self, resource_view):
        fields = resource_view.get('fields')

        if fields:
            resource_view['fields'] = convert_to_string(fields)


def _view_data(resource_view):
    data = {
        'resource_id': resource_view['resource_id'],
        'limit': int(resource_view.get('limit', 100))
    }

    filters = resource_view.get('filters', {})
    for key, value in parse_filter_params().items():
        filters[key] = value
    data['filters'] = filters

    fields = resource_view.get('fields')
    if fields:
        data['fields'] = convert_to_string(fields).split(',')

    result = p.toolkit.get_action('datastore_search')({}, data)
    return result


def parse_filter_params():
    filters = collections.defaultdict(list)
    filter_string = dict(p.toolkit.request.GET).get('filters', '')
    for filter in filter_string.split('|'):
        if filter.count(':') != 1:
            continue
        key, value = filter.split(':')
        filters[key].append(value)
    return dict(filters)


def convert_to_string(value):
    if isinstance(value, list):
        return ','.join(value)
    return value


def validate_fields(key, converted_data, errors, context):
    try:
        resource = {'id': converted_data['resource_id',]}
    except KeyError:
        resource = {'id': context['resource'].id}
    value = converted_data.get(key)
    allowed_fields = set(field['id'] for field in _get_fields(resource))
    for field in value.split(','):
        if field not in allowed_fields:
            msg = 'Field {field} not in table'.format(field=field)
            raise p.toolkit.Invalid(msg)
    return value


def _get_fields_without_id(resource):
    fields = _get_fields(resource)
    return [{'value': v['id']} for v in fields if v['id'] != '_id']


def _get_fields(resource):
    data = {
        'resource_id': resource['id'],
        'limit': 0
    }
    result = p.toolkit.get_action('datastore_search')({}, data)
    return result['fields']
