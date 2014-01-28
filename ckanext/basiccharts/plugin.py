import ckan.plugins as p

not_empty = p.toolkit.get_validator('not_empty')


class BaseChart(p.SingletonPlugin):
    '''Class with methods common to all basic charts'''

    CHART_TYPE = 'base'

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'basiccharts')

    def info(self):
        schema = {
            'filter_field': [],
            'filter_value': [],
            'series': [not_empty],
            'y_axis': [not_empty]
        }

        return {'icon': 'bar-chart',
                'schema': schema,
                'iframed': False}

    def can_view(self, data_dict):
        return data_dict['resource'].get('datastore_active', False)

    def setup_template_variables(self, context, data_dict):
        resource = data_dict['resource']
        resource_view = data_dict['resource_view']
        fields = _get_fields_without_id(resource)

        return {'resource': data_dict['resource'],
                'resource_view': data_dict['resource_view'],
                'fields': fields,
                'chart_type': self.CHART_TYPE}

    def view_template(self, context, data_dict):
        return 'basiccharts_view.html'

    def form_template(self, context, data_dict):
        return 'basiccharts_form.html'


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
        info['name'] = 'barchart'
        info['title'] = 'Bar Chart'

        return info


class PieChart(BaseChart):

    CHART_TYPE = 'pie'

    def info(self):
        info = super(PieChart, self).info()
        info['name'] = 'piechart'
        info['title'] = 'Pie Chart'

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
