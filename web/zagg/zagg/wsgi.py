"""
WSGI config for zagg project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zagg.settings")

from django.core.wsgi import get_wsgi_application
# application is from django and is needed by django.
# disabling the invalid-name pylint check
# pylint: disable=invalid-name
application = get_wsgi_application()
