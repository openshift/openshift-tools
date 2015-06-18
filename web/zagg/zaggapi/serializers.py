#from metric.models import Metric
from metric.metricmanager import Metric
from rest_framework import serializers


class MetricSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Metric
        fields = ('name', 'id')
