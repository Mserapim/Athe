import time
import os
from datetime import datetime

from django.db.models import Q

from celery import Celery

from contrib.utils import getLogger
from contrib.middleware import set_current_user, get_current_user
from contrib.daterange import NewDateRange

from engine.mq.models import Task
from rh.gfp.models import Evento as Event, Folha as Payroll, Servidor
from rh.models import (
    MovimentacaoSubstituicao,
    MovesSubstitutionsConsolidated,
    Servidor as Employee,
)

from rh.gfp.gfp_utils import get_paycheck, create_entry
from rh.gfp.gcpp_utils import criar_gcpp
from rh.gratifications_manager.gm_utils import (
    buscar_verba_calculo_exerc_cumul_consolidado,
)
from rh.gratifications_manager.cumulative_exercices_utils import (
    consolidar_exerc_cumul_subs,
)

log = getLogger(__name__)
app = Celery("gratificaions_manager")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def autorizate_mov_sub_task(task, hook, user, movs_ids):
    """
    Esta Task é responsável por autorizar pagamentos dos exercícios cumulativos que foram selecionados
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    task = Task.objects.get(uuid=task)
    movs = MovimentacaoSubstituicao.objects.filter(pk__in=movs_ids)

    state = "progress"
    msg = f"Autorizando pagamentos de {movs.count()} exercícios cumulativos.."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)

    try:
        # Não está utilizando o filter().update() para que execute propositalmente o método save()
        # no save() há uma verificação para preenchimento automático dos campos de efeito financeiro

        for mov in movs:
            mov.able_to_pay = True
            mov.save()
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = f"<p>Erro ao autorizar pagamentos dos exercícios cumulativos selecionados.</p>"
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def consolidate_able_to_pay_employee_task(
    task, hook, user, employee_id, employee_movs_ids, periodo_cumul_subs_id
):
    """
    Esta Task é responsável por consolidar exercícios cumulativos de um servidor
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    task = Task.objects.get(uuid=task)
    employee = Employee.objects.get(pk=employee_id)
    movs = MovimentacaoSubstituicao.objects.filter(pk__in=employee_movs_ids).order_by(
        "data_inicio"
    )

    state = "progress"
    msg = f"Consolidando {movs.count()} exercícios cumulativos para o servidor: {employee}."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)

    try:
        consolidar_exerc_cumul_subs(employee, employee_movs_ids, periodo_cumul_subs_id)
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = f"<p>Erro ao consolidar exercícios cumulativos para o servidor: {employee}.</p>"
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def desconsolidate_item_task(task, hook, user, mov_sub_consolidated_id):
    """
    Esta Task é responsável por desconsolidar um registro consolidado de exercícios cumulativos.
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    task = Task.objects.get(uuid=task)
    mov_sub_cons = MovesSubstitutionsConsolidated.objects.get(
        pk=mov_sub_consolidated_id
    )

    state = "progress"
    msg = f"Desconsolidando exercícios cumulativos: {mov_sub_cons}."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)

    try:
        mov_sub_cons.substitutions.all().update(consolidated=False)
        mov_sub_cons.delete()
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = f"<p>ERRO ao desconsolidar exercício cumulativo consolidado: {mov_sub_cons}.</p>"
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def calculate_consolidated_task(task, hook, user, mov_sub_consolidated_id):
    """
    Esta Task é responsável por calcular um registro consolidado de exercícios cumulativos.
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    task = Task.objects.get(uuid=task)
    mov_sub_cons = MovesSubstitutionsConsolidated.objects.get(
        pk=mov_sub_consolidated_id
    )

    state = "progress"
    msg = f"Calculando exercícios cumulativos: {mov_sub_cons}."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)

    try:
        event = buscar_verba_calculo_exerc_cumul_consolidado()
        payroll = (
            Payroll.objects.filter(tipo_folha__titulo="NORMAL")
            .order_by("-periodo__ano", "-periodo__mes")
            .first()
        )

        classcode = event.calculation_at(payroll.date_range.first)
        cls = classcode.cls
        calc = cls(
            mov_sub_cons.employee,
            payroll,
            event,
            params={"qnt": mov_sub_cons.days_consolidated},
        )
        ret = calc.calculate()

        mov_sub_cons.qtd_max = ret["qnt_max"]
        mov_sub_cons.installments_paid = ret["parcela"]
        mov_sub_cons.installments = ret["prazo"]
        mov_sub_cons.pct = ret["pct"]
        mov_sub_cons.base_value = ret["valor_base"]
        mov_sub_cons.value_calculated = ret["valor"]
        mov_sub_cons.contribution_base = ret["base_previdencia"]
        mov_sub_cons.employer_value = ret["patronal"]

        mov_sub_cons.save()
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = (
            f"<p>ERRO ao calcular exercício cumulativo consolidado: {mov_sub_cons}.</p>"
        )
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def applicate_consolidated_task(task, hook, user, mov_sub_id, payroll_id):
    """
    Esta Task é responsável por aplicar o cumulativo consolidado em folha
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    task = Task.objects.get(uuid=task)

    mov_sub = MovesSubstitutionsConsolidated.objects.get(pk=mov_sub_id)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Aplicando cumulativo consolidado: {mov_sub}</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    log.debug(f"TASK {task.uuid} - Aplicando cumulativo consolidado: {mov_sub}.")

    try:
        payroll_to_apply = Payroll.objects.get(pk=payroll_id)
        event_to_apply = buscar_verba_calculo_exerc_cumul_consolidado()

        paycheck_to_apply = get_paycheck(mov_sub.employee, payroll_to_apply)

        if paycheck_to_apply.lancamentos.filter(evento=event_to_apply).exists():
            state = "failed"
            message = f"""
            <p>A Folha escolhida, {paycheck_to_apply}, já possui uma rúbrica com este evento.
            Por favor escolha outra Folha para aplicar este cumulativo consolidade: {mov_sub}</p>
            """
            task.info(msg=message, type_of=3)
        else:
            create_entry(
                paycheck_to_apply,
                event_to_apply,
                qtd=mov_sub.days_consolidated,
                qtd_max=mov_sub.qtd_max,
                installments_paid=mov_sub.installments_paid,
                installments=mov_sub.installments,
                pct=mov_sub.pct,
                value=mov_sub.value_calculated,
                base_value=mov_sub.base_value,
                employer_value=mov_sub.employer_value,
                # info=f"{mov_sub.period.month}/{mov_sub.period.year}",
                # ref_year=mov_sub.period.year,
                # ref_month=mov_sub.period.month,
                contribution_base=mov_sub.contribution_base,
                insertion_type=8,  # Choice id 8 - Tipo de Inserção: Exercício Cumulativo
            )

            mov_sub.paid_out = True
            mov_sub.paycheck_applied = paycheck_to_apply
            mov_sub.save()

            state = "ready"
            message = f"<p>Aplicação concluída do cumulativo consolidado: {mov_sub}."
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = f"<p>Erro ao aplicar a cumulativo consolidado: {mov_sub}</p>"
        task.info(msg=message, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def defer_consolidated_task(task, hook, user, mov_sub_id):
    """
    Esta Task é responsável por aplicar o cumulativo consolidado em folha
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    task = Task.objects.get(uuid=task)

    mov_sub = MovesSubstitutionsConsolidated.objects.get(pk=mov_sub_id)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Deferindo cumulativo consolidado: {mov_sub}</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    log.debug(f"TASK {task.uuid} - Deferindo cumulativo consolidado: {mov_sub}.")

    try:
        gcpp = criar_gcpp(
            servidor=mov_sub.employee,
            evento=buscar_verba_calculo_exerc_cumul_consolidado(),
            qtd_dias=mov_sub.days_consolidated,
            periodo_ano=datetime.now().year,
            periodo_mes=datetime.now().month,
            servidor_conferido_por=Servidor.objects.get(user=get_current_user()),
            modulo_origem="exercício cumulativo consolidado",
        )

        mov_sub.defer = True
        mov_sub.gcpp = gcpp
        mov_sub.save()

        state = "ready"
        message = f"<p>Deferimento concluído do cumulativo consolidado: {mov_sub}."
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = f"<p>Erro ao deferir a cumulativo consolidado: {mov_sub}</p>"
        task.info(msg=message, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def efetivar_exercicio_cumulativo_task(task, hook, user, mov_substituicao):
    from rh.pvf.models import PVFExercicioCumulativo

    message = "<p>Efetivando exercicio cumulativo...</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        PVFExercicioCumulativo.efetivar_exercicio_cumulativo(
            task=task, mov_substituicao=mov_substituicao
        )
        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao efetivar os exercicios cumulativos</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception
