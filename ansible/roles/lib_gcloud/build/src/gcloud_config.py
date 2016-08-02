# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudConfig(GcloudCLI):
    ''' Class to wrap the gcloud config command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 project=None,
                 region=None):
        ''' Constructor for gcloud resource '''
        super(GcloudConfig, self).__init__()

        self._working_param = {}

        if project:
            self._working_param['name'] = 'project'
            self._working_param['value'] = project
            self._working_param['section'] = 'core'
        elif region:
            self._working_param['name'] = 'region'
            self._working_param['value'] = region
            self._working_param['section'] = 'compute'

        self._current_config = self.get_compacted_config()


    def get_compacted_config(self):
        '''return compated config options'''

        results = self._list_config()

        compacted_results = {}
        for config in results['results']:
            compacted_results.update(results['results'][config])

        return compacted_results

    def list_config(self):
        '''return config'''
        results = self._list_config()

        return results

    def check_value(self, param, param_value):
        '''check to see if param needs to be updated'''
        return self._current_config[param] == param_value

    def update(self):
        ''' do updates, if needed '''
        if not self.check_value(self._working_param['name'], self._working_param['value']):
            config_set_results = self._config_set(self._working_param['name'], self._working_param['value'],
                                                  self._working_param['section'])
            list_config_results = self.list_config()
            config_set_results['results'] = list_config_results['results']

            return  config_set_results
        else:
            list_config_results = self.list_config()
            return {'results': list_config_results['results']}
