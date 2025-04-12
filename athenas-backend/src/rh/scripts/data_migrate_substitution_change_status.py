# -.- coding: utf-8 -.-
import django
import os
import datetime


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.const import ACTIVE, FINISHED, SCHEDULED
from rh.afastamento.models import MovimentacaoSubstituicao
from rh.models import MovimentacaoSubstituicao


log = getLogger(__name__)


set_current_user("athenas")


def setup_substitution_status():
    query = MovimentacaoSubstituicao.objects.filter()
    count = 0
    total = query.count()
    today = datetime.datetime.now().date()
    print(f"{count} of {total}")
    for sub in query.order_by("-data_inicio"):
        active = sub.is_active()
        state = SCHEDULED
        if active:
            state = ACTIVE
        elif sub.data_fim and sub.data_fim < today:
            state = FINISHED
        if sub.state != state:
            MovimentacaoSubstituicao.objects.filter(pk=sub.pk).update(state=state)
            print(f"{count} of {total}")
            count += 1


def setup_substitution_status_change_date():
    query = MovimentacaoSubstituicao.objects.filter().exclude(
        status_change_date__isnull=False
    )
    count = 0
    total = query.count()
    today = datetime.datetime.now().date()
    print(f"{count} of {total}")
    for sub in query.order_by("-data_inicio"):
        status_change_date = None
        if sub.data_fim and sub.data_fim < today:
            status_change_date = sub.data_fim
        elif sub.state == ACTIVE:
            status_change_date = sub.data_inicio
        if status_change_date:
            MovimentacaoSubstituicao.objects.filter(pk=sub.pk).update(
                status_change_date=status_change_date
            )
        print(f"{count} of {total}")
        count += 1


def run():
    setup_substitution_status()
    setup_substitution_status_change_date()

    print("ATIVOS:")
    for sub in MovimentacaoSubstituicao.objects.filter(state=ACTIVE):
        print(sub)
    print("AGENDADOS:")
    for sub in MovimentacaoSubstituicao.objects.filter(state=SCHEDULED):
        print(sub)


if __name__ == "__main__":
    run()
