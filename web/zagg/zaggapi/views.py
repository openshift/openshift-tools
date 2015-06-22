"""
Django view to allow the rest commands to
create new Zagg UniqueMetrics

"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from metricmanager import UniqueMetric, MetricManager

#disabling these checks because we are extending the django framework
# and pylint isn't catching this
# Pylint isn't checking for APIView parent class, so disablign no-member check
#pylint: disable=too-many-public-methods,no-self-use,unused-argument,no-member
class MetricView(APIView):
    """
    Django view class to allow access to rest functions
    """
    def __init__(self):
        pass

    def post(self, request, *args, **kwargs):
        """
        implementation of the REST GET method
        """
        new_metric = UniqueMetric.from_request(request.data)
        mymm = MetricManager('/tmp/metrics')
        mymm.write_metrics(new_metric)

        return Response({"success": True})

    def get(self, request, *args, **kwargs):
        """
        implementation of the REST GET method
        """
        mymm = MetricManager('/tmp/metrics')
        results = mymm.read_metrics()

        res = []
        for uniqm in results:
            res.append(uniqm.to_dict())
        response = Response(res, status=status.HTTP_200_OK)

        return response
