# vim: expandtab:tabstop=4:shiftwidth=4

"""
Django view to allow the rest commands to
create new Zagg UniqueMetrics

"""
from rest_framework.views import APIView
from rest_framework.response import Response
from openshift_tools.monitoring.metricmanager import UniqueMetric, MetricManager

import yaml

#disabling these checks because we are extending the django framework
# and pylint isn't catching this
# Pylint isn't checking for APIView parent class, so disablign no-member check
#pylint: disable=too-many-public-methods,no-self-use,unused-argument,no-member,no-init
class MetricView(APIView):
    """
    Django view class to allow access to rest functions
    """
    def post(self, request, *args, **kwargs):
        """
        implementation of the REST GET method
        """

        config_file = '/etc/openshift_tools/zagg_server.yaml'
        config = yaml.load(file(config_file))

        for target in config['targets']:
            new_metric = UniqueMetric.from_request(request.data)
            mymm = MetricManager(target['path'])
            mymm.write_metrics(new_metric)

        return Response({"success": True})
