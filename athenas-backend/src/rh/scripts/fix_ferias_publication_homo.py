import django
import os
import datetime


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.ferias.models import PeriodoAquisitivo, PeriodoAquisitivoServidor

log = getLogger(__name__)

set_current_user("athenas")


def fill_publication_homologation_on_periodoaquisitivo():
    pas_all = PeriodoAquisitivo.objects.filter(
        homologation_publication__isnull=True
    ).distinct()
    count = 0
    for pas in pas_all:
        count += 1
        print(f"{count} of {pas_all.count()}")

        pasu = PeriodoAquisitivoServidor.objects.filter(
            periodo_aquisitivo=pas, homologation_publication__isnull=False
        ).first()
        if pasu:
            PeriodoAquisitivo.objects.filter(id=pas.id).update(
                homologation_publication=pasu.homologation_publication
            )


def run():
    fill_publication_homologation_on_periodoaquisitivo()


if __name__ == "__main__":
    run()
