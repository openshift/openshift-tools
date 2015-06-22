"""
Django urls file for the zagg project
"""
from django.conf.urls import url
from zaggapi.views import MetricView

# Additionally, we include login URLs for the browsable API.
# urlpatterns is from django and is needed by django.
# disabling the invalid-name pylint check
# pylint: disable=invalid-name
urlpatterns = [
    url(r'metric', MetricView.as_view()),
]
