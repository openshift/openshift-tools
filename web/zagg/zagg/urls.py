from django.conf.urls import url, include
from rest_framework import routers
from zaggapi.views import MetricView

# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'metric', MetricView.as_view()),
]
