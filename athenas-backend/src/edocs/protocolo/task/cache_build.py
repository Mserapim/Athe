import os

from celery import Celery
from time import time
from edocs.protocolo.models import Protocolo

app = Celery("edoc")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def async_cache_migration(protocol_id):
    protocol = Protocolo.objects.get(pk=protocol_id)
    cache = protocol.appends_of_document
