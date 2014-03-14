import ckan.plugins as p

not_empty = p.toolkit.get_validator('not_empty')
ignore_missing = p.toolkit.get_validator('ignore_missing')
aslist = p.toolkit.aslist


class BasicCharts(p.SingletonPlugin):
    p.implements(p.ITemplateHelpers)

    def get_helpers(self):
        return {'remove_linebreaks': _remove_linebreaks,
                'get_filter_values': get_filter_values}


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
            'filter_fields': [ignore_missing],
            'filter_values': [ignore_missing],
            'y_axis': [not_empty],
            'show_legends': [ignore_missing]
        }

        if self.GROUP_BY_IS_REQUIRED:
            schema['group_by'] = [not_empty]
        else:
            schema['group_by'] = [ignore_missing]

        return {'icon': 'bar-chart',
                'schema': schema,
                'sizex': 4,
                'sizey': 3,
                'iframed': False}

    def can_view(self, data_dict):
        return data_dict['resource'].get('datastore_active', False)

    def setup_template_variables(self, context, data_dict):
        resource = data_dict['resource']
        resource_view = data_dict['resource_view']
        resource_view = self._filter_fields_and_values_as_list(resource_view)
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

    def _filter_fields_and_values_as_list(self, resource_view):
        if 'filter_fields' in resource_view:
            if isinstance(resource_view['filter_fields'], basestring):
                resource_view['filter_fields'] = [resource_view['filter_fields']]
        if 'filter_values' in resource_view:
            if isinstance(resource_view['filter_values'], basestring):
                resource_view['filter_values'] = [resource_view['filter_values']]
        return resource_view


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
        info['sizex'] = 2
        info['sizey'] = 2

        return info


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


def _remove_linebreaks(string):
    '''Convert a string to be usable in JavaScript'''
    return str(string).replace('\n', '')

def get_filter_values(resource):
    ''' Tries to get out filter values so they can appear in dropdown list.
    Leaves input as text box when the table is too big or there are too many
    distinct values.  Current limits are 5000 rows in table and 500 distict
    values.'''

    data = {
        'resource_id': resource['id'],
        'limit': 5001
    }
    result = p.toolkit.get_action('datastore_search')({}, data)
    # do not try to get filter values if there are too many rows.
    if len(result.get('records', [])) == 5001:
        return {}

    filter_values = {}
    for field in result.get('fields', []):
        if field['type'] != 'text':
            continue
        distinct_values = set()
        for row in result.get('records', []):
            distinct_values.add(row[field['id']])
        # keep as input if there are too many distinct values.
        if len(distinct_values) > 500:
            continue
        filter_values[field['id']] = [{'id': value, 'text': value}
                                      for value
                                      in sorted(list(distinct_values))]
    return filter_values
