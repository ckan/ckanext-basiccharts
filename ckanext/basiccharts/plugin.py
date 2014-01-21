import ckan.plugins as p

not_empty = p.toolkit.get_validator('not_empty')


class BasicCharts(p.SingletonPlugin):
    '''This extension makes basic charts'''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'basiccharts')

    def info(self):
        schema = {
            'xAxis': [not_empty],
            'yAxis': [not_empty]
        }

        return {'name': 'basiccharts',
                'title': 'Basic Charts',
                'icon': 'bar-chart',
                'schema': schema,
                'iframed': False}

    def can_view(self, data_dict):
        return data_dict['resource'].get('datastore_active', False)

    def setup_template_variables(self, context, data_dict):
        fields = _get_fields(data_dict['resource'])
        xAxis = data_dict['resource_view'].get('xAxis')
        yAxis = data_dict['resource_view'].get('yAxis')
        fields = [{'value': v['id']} for v in fields if v['id'] != '_id']
        return {'fields': fields,
                'xAxis': xAxis,
                'yAxis': yAxis,
                'records': _get_records_from_datastore(data_dict['resource'])}

    def view_template(self, context, data_dict):
        return 'basiccharts_view.html'

    def form_template(self, context, data_dict):
        return 'basiccharts_form.html'


def _get_fields(resource):
    limit = 0
    return _datastore_search(resource, limit)['fields']

def _get_records_from_datastore(resource):
    limit = 5000
    offset = 0
    return _datastore_search(resource, limit, offset)['records']

def _datastore_search(resource, limit=None, offset=None):
    data = {'resource_id': resource['id']}
    if limit:
        data['limit'] = limit
    if offset:
        data['offset'] = offset
    result = p.toolkit.get_action('datastore_search')({}, data)
    return result

