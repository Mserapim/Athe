# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user

from rh.models import DigitalDocument
from rh.registration.models import FormInformation
from standard.models import Choice

from contrib.utils import getLogger


import datetime
import time


log = getLogger(__name__)


set_current_user("athenas")

print(
    """
    Este script possui regras específicas de listagem e envio de recadastramentos para validação.
    Ele checa se os servidores possuem o documento digital 59.
    Lista todos os pendentes.
    Tenta enviar caso o cliente deseje enviar.
"""
)

# TODO: CRIAR POSSIBILIDADE DE ENVIO EM LOTE SEM CHECAGEM DE REGRAS


pks = []
found = []
choice = {}
fi_pendencies = []
fi_attachment = []
for c in Choice.get_choices_for("registration", "FORMINFORMATION_STATE"):
    choice.update({c[0]: c[1]})
count = 0
rs = {
    1: {"count_not_fill": 0, "count_filled": 0, "pendency": 0},
    2: {"count_not_fill": 0, "count_filled": 0, "pendency": 0},
    3: {"count_not_fill": 0, "count_filled": 0, "pendency": 0},
    4: {"count_not_fill": 0, "count_filled": 0, "pendency": 0},
    5: {"count_not_fill": 0, "count_filled": 0, "pendency": 0},
}
print("pk|state_display|state|possui documento digital 59 para envio")
for fi in (
    FormInformation.objects.filter(employee__ativo=True)
    .exclude(
        employee__pk__in=DigitalDocument.objects.filter(document_type=59).values(
            "employee"
        )
    )
    .order_by("employee")
):
    fi_doc = fi.digital_documents.filter(document_type=59).exists()
    if not (fi.state in (2, 3) and fi_doc):
        found.append(fi.pk)
        print(
            f'{fi} | {fi.get_state_display()} | {fi.state} | {"PREENCHIDO" if fi_doc else "NÃO PREENCHIDO"}'
        )
        count += 1
        pendency, errors = fi.pendency()
        if pendency:
            fi_pendencies.append(fi)
        rs1 = rs.get(fi.state)
        if fi_doc:
            rs1.update(
                {
                    "count_filled": rs1.get("count_filled") + 1,
                    "pendency": (rs1.get("pendency") + 1 if pendency else 0),
                }
            )
            fi_attachment.append(fi)
        else:
            rs1.update(
                {
                    "count_not_fill": rs1.get("count_not_fill") + 1,
                    "pendency": (rs1.get("pendency") + 1 if pendency else 0),
                }
            )

print(f"total {count}")
for r in rs:
    print(
        f'{choice.get(r)} - com anexo({rs.get(r).get("count_filled")}) - sem anexo({rs.get(r).get("count_not_fill")}) - pendências({rs.get(r).get("count_not_fill")})'
    )


print(f"Com pendências: {len(fi_pendencies)}")
for fi in fi_pendencies:
    print(fi)


rs = input(
    f"\nVocê deseja enviar {len(fi_attachment)} recadastramentos para validação? (y/N)\n"
)

if rs == "y":
    count = 0
    for fi in fi_attachment:
        try:
            fi.send_validation()
            count += 1
            print(f"{fi.pk} | {fi}")
        except Exception as err:
            print(err)
    print(f"Enviados: {count} de {len(fi_attachment)}")
else:
    print(f"Nada foi enviado.")
