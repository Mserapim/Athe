"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import codecs
import datetime
import socket

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.wsgi import get_wsgi_application


if hasattr(settings, "LOCKS_DIR"):
    if not os.path.exists(settings.LOCKS_DIR):
        os.makedirs(settings.LOCKS_DIR)

    filename = os.path.join(
        settings.LOCKS_DIR, "%s.start" % slugify(socket.gethostname())
    )
    codecs.open(filename, "w").write(
        datetime.datetime.today().strftime("%Y%m%d%H%M%S%f")
    )
else:
    print(
        "\033[1m\033[33mWARNING: Lock directory (LOCKS_DIR) not configured in %s\033[0m"
        % os.environ["DJANGO_SETTINGS_MODULE"]
    )


if settings.DEBUG and (os.environ.get("PTVSD_ON") == "on"):
    try:
        import ptvsd
    except ModuleNotFoundError:
        print("Instale o modulo ptvsd para utilizar o debug")
    else:
        try:
            ptvsd.enable_attach(
                address=(
                    os.environ.get("PTVSD_IP", "0.0.0.0"),
                    os.environ.get("PTVSD_PORT", "5678"),
                )
            )
        except Exception:
            pass


application = get_wsgi_application()
