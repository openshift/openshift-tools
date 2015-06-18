from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from metric.metricmanager import UniqueMetric, MetricManager

class MetricView(APIView):

    def post(self, request, *args, **kwargs):
        new_metric = UniqueMetric.from_request(request.data)
        mmm = MetricManager('/tmp/metrics')
        mmm.write_metrics(new_metric) # this can be a list of metrics too!

        return Response({"success": True})

    def get(self, request, *args, **kwargs):
        mmm = MetricManager('/tmp/metrics')
        results = mmm.read_metrics()

        r = []
        for um in results:
            r.append(um.to_JSON())

        #r = [{ "results": "hw" }]

        response = Response(r, status=status.HTTP_200_OK)

        return response
