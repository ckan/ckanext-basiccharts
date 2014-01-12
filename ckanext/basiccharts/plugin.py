import ckan.plugins as p


class BasicCharts(p.SingletonPlugin):
    '''This extension makes basic charts'''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'basiccharts')

    def info(self):
        return {'iframed': False}

    def can_view(self, data_dict):
        return data_dict['resource'].get('datastore_active', False)

    def setup_template_variables(self, context, data_dict):
        return {}

    def view_template(self, context, data_dict):
        return 'basiccharts_view.html'

    def form_template(self, context, data_dict):
        return 'basiccharts_form.html'
