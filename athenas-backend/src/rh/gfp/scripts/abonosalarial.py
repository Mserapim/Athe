from rh.gfp.models import *
from contrib.middleware import set_current_user
import datetime

set_current_user("athenas")
folha_eventos = (
    FolhaEvento.objects.filter(evento__numero="05200")
    .order_by("servidor_id", "folha__periodo__ano", "folha__periodo__mes")
    .distinct("servidor_id")
)
extra = ExtraPayment.objects.get(slug="ABONO-PERMANENCIA")

for fe in folha_eventos:
    extra_employee = ExtraPaymentPeriod(
        extra_payment=extra,
        employee=fe.servidor,
        start_validity=datetime.date(fe.folha.periodo.ano, fe.folha.periodo.mes, 1),
        type_value=2,
        value=100,
        main_salary=False,
    )
    if fe.servidor.data_desligamento:
        extra_employee.end_validity = fe.servidor.data_desligamento

    extra_employee.save()
