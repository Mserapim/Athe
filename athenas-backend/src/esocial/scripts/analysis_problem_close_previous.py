# -.- coding: utf-8 -.-
import os
import django


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from esocial.models import Event, S2299, S2399, BatchEvent
from contrib.utils import getLogger, DateUtils


log = getLogger(__name__)


set_current_user("gustavodettenborn")


def run():

    events_closed_by = {}
    events_to_exclude = []

    for event in Event.objects.filter(acronym__in=("s2200", "s2300")).valids_sent():
        closed_by = event.closed_by_event

        if not closed_by:
            """TENTA ENCONTRAR O DESLIGAMENDO CORRETO"""
            if event.acronym == "s2200":
                closed_by = (
                    S2299.objects.filter(registry_employee=event.registry_employee)
                    .valids_sent()
                    .last()
                )

            else:
                closed_by = (
                    S2399.objects.filter(registry_employee=event.registry_employee)
                    .valids_sent()
                    .last()
                )

            if closed_by:
                employee = event.event.employee()
                termination_date = (
                    DateUtils.date_to_str(employee.termination_date)
                    if employee.termination_date
                    else None
                )
                if employee.ativo:
                    """CASO O SERVIDOR ESTEJA ATIVO, VAI ADICIONAR NA LISTA DE REMOÇÃO DO EVENTO DO ESOCIAL"""
                    msg = f"{event.event.acronym} {employee} | DELISGAMENTO: {termination_date} - ATIVO"
                    print(
                        f"{msg} | O EVENTO DE DESLIGAMENTO SERÁ EXCLUÍDO: {closed_by}"
                    )
                    events_to_exclude.append(closed_by.pk)
                elif not getattr(event, "modified_by_event", None):
                    """DO CONTRÁRIO, VAI ATUALIZAR O EVENTO DE CADASTRO COM SEU FECHAMENTO"""
                    msg = f"{event.event.acronym} {employee} | DELISGAMENTO: {termination_date} - INATIVO"
                    print(f"{msg} | SERÁ FECHADO POR: {closed_by}")
                    events_closed_by.update({event.pk: closed_by.pk})

                    Event.objects.filter(pk=event.pk).update(
                        end_validity=closed_by.start_validity,
                        closed_by_event=closed_by.pk,
                    )
                    closed_by.refresh_from_db()
                    closed_by.save()

    """APAGAR EVENTOS NO ESOCIAL"""
    BatchEvent.generate_delete_events(events=events_to_exclude)
    print("É NECESSÁRIO ENVIAR TODOS EVENTOS DE REMOÇÃO DOS DESLIGAMENTOS!")


if __name__ == "__main__":
    run()
