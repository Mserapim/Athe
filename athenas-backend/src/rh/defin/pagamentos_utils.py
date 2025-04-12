from contrib.utils import getLogger
from contrib.decorator import login_required
from rh.gfp.paycheckdifference_utils import calc_from_period
from rh.gfp.models import Evento

log = getLogger(__name__)


@login_required("JSON")
def calculate_inss(inst, employee, payroll, base_value):
    if inst.inss_exempt:
        inss_value = 0
    else:
        event = Evento.objects.get(numero="89900")
        params = {"base_value": base_value}
        res = calc_from_period(employee, payroll, event, params)
        inss_value = res["valor"]
    return inss_value


@login_required("JSON")
def calculate_irrf(inst, employee, payroll, base_value):
    event = Evento.objects.get(numero="99700")
    params = {"base_value": base_value}
    res = calc_from_period(employee, payroll, event, params)
    return res["valor"]
