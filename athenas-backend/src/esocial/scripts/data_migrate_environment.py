# -.- coding: utf-8 -.-
"""
    ATENÇÃO: SÓ EXECUTE ESTE SCRIPT CASO VOCÊ TENHA ENVIADO PARA PRODUÇÃO DO ESOCIAL ANTES DESSA VERSÃO!

    Este script modifica o valor do campo "environment" para 1(Produção). Dos seguintes modelos:
        - EventDependency;
        - BatchEvent;
        - ReturnResult;
        - Occurrence;
        - Reference;

    Este script migra o valor de ide_evento_tp_amb_deprecated para ide_evento_tp_amb.
"""


import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from esocial.models import (
    BatchEvent,
    Event,
    EventDependency,
    Occurrence,
    Reference,
    ReturnResult,
)


def data_migrate_environment():
    for event in Event.objects_all.filter():
        event = event.event
        if hasattr(event, "ide_evento_tp_amb_deprecated") and hasattr(
            event, "ide_evento_tp_amb"
        ):
            Event.objects_all.filter(pk=event.pk).update(
                ide_evento_tp_amb=event.ide_evento_tp_amb_deprecated
            )

    EventDependency.objects_all.filter().update(environment=1)
    BatchEvent.objects_all.filter().update(environment=1)
    ReturnResult.objects_all.filter().update(environment=1)
    Occurrence.objects_all.filter().update(environment=1)
    Reference.objects_all.filter().update(environment=1)


if __name__ == "__main__":
    rs = input(
        """
    ATENÇÃO: SÓ EXECUTE ESTE SCRIPT CASO VOCÊ TENHA ENVIADO PARA PRODUÇÃO DO ESOCIAL ANTES DESSA VERSÃO!

    Este script modifica o valor do campo "environment" para 1(Produção). Dos seguintes modelos:
        - EventDependency;
        - BatchEvent;
        - ReturnResult;
        - Occurrence;
        - Reference;

    Este script migra o valor de ide_evento_tp_amb_deprecated para ide_evento_tp_amb.

    VOCÊ QUER EXECUTAR? (y/N)"""
    )
    if rs == "y":
        data_migrate_environment()
