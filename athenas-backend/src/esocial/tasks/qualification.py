# -*- coding: utf-8 -*-


import os

# import json
import time
from datetime import datetime  # , timedelta

from celery import Celery
from dateutil.relativedelta import relativedelta
from django.db.models import F, Q

from contrib.helpers import clear_to_ascii
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from engine.mq.const import TIPO_TASK_PROCESSAMENTO_ESOCIAL
from engine.mq.models import Task
from esocial.loaders.qualification import QualifLoader
from esocial.models import RegistrationQualification
from ged.models import Arquivo as GedFile
from rh.models import Dependencia, PessoaFisica, Servidor as Employee
from rh.models import Trainee
from standard.models import Choice

log = getLogger(__name__)
app = Celery("esocial")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def generate_qualification_file(task, hook, user, all=False):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"

    feedback("", 100)
    task.message = ""  # message
    task.state = state
    task.save()


@app.task()
def discouver_persons(task, hook, user):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    def create_or_update_reg_qualification(
        task, person, type_of_person, employee=None, force=False
    ):
        log.debug("%s: %s" % (person, employee))
        query_nis = person.documento.filter(tipo_documento__in=[5, 6])
        nis_pis_pasep = query_nis.first().numero[0:11] if query_nis else ""
        obj, created = RegistrationQualification.objects.get_or_create(
            natural_person=person,
            defaults={
                "type_of_person": type_of_person,
                "last_modified_person_at": person.modified_at,
                "last_modified_person_by": person.modified_by,
                "nome": clear_to_ascii(person.nome),
                "cpf": person.cpf[0:11] if person.cpf else "",
                "dn": person.data_nascimento,
                "nis": nis_pis_pasep,
                "employee": employee,
            },
        )
        if created:
            task.info(
                msg="Registro criado para %s (%s)."
                % (pf.nome, obj.get_type_of_person_display()),
                type_of=1,
            )
        else:
            if obj.type_of_person != type_of_person and not force:
                log.debug(">>>> 1")
                type_of_person_display = Choice.objects.get(
                    app_label="esocial", name="TYPE_OF_PERSON", value=type_of_person
                ).label
                task.info(
                    msg="Registro não criado para %s (%s). Tipo existente: %s"
                    % (
                        pf.nome,
                        type_of_person_display,
                        obj.get_type_of_person_display(),
                    ),
                    type_of=2,
                )
            else:
                log.debug(">>>> 2")
                obj.nome = clear_to_ascii(person.nome)
                obj.cpf = person.cpf[0:11] if person.cpf else ""
                obj.dn = person.data_nascimento
                obj.nis = nis_pis_pasep
                obj.employee = employee
                if obj.diff:
                    diff = ""
                    for k in obj.diff:
                        diff += "<p>%s: %s >> %s</p>" % (
                            k,
                            obj.diff[k][0],
                            obj.diff[k][1],
                        )
                    task.info(
                        msg="Registro atualizado pois as diferenças abaixo foram encontradas:%s"
                        % (diff),
                        type_of=2,
                    )
                    obj.set_unqualified()
                obj.save()

        return obj, created

    state = "progress"
    # payroll = Payroll.objects.get(pk=payroll_id)
    message = "<p>Erro ao avaliar pessoas qualificáveis.</p>"
    task = Task.objects.get(uuid=task)
    log.debug("TASK %s" % task.uuid)

    try:
        set_current_user(user)
        feedback("", 0, message="<p>Avaliando pessoas qualificáveis</p>", state=state)
        task.info(
            msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )
        task.description = "Atualização da lista de pessoas qualificáveis."
        task.notificar_hermes = True
        task.tipo_processamento = TIPO_TASK_PROCESSAMENTO_ESOCIAL

        # Procurando por servidores que não entraram na folha
        # log.debug('TASK %s - Criando contracheques...' % task.uuid)

        dt_now = datetime.now().date()
        dt_ini = dt_now - relativedelta(months=1)

        q_employees = Employee.objects.exclude(
            type_by_possession__in=["EST", "EXT", "TCR", "VOL", "JCA"]
        ).filter(Q(paychecks__folha__dt_pagamento__gt=dt_ini) | Q(ativo=True))
        q_employees_d = q_employees.distinct()
        q_trainees = Trainee.objects.filter(ativo=True)

        feedback(
            "",
            0,
            message="<p>Avaliando pessoas não qualificáveis para remover do cadastro!</p>",
            state=state,
        )
        for q in RegistrationQualification.objects.filter():
            q_pensioner_death = q.employee.pensao_pagador.filter(
                type_of_pension=2
            ).exists()  # Verificando se é pagador de pensão por morte
            remove_reg = q_pensioner_death
            remove_reg |= (
                not q_employees.filter(pk=q.employee.pk).exists()
                and q.type_of_person in [1, 2, 3, 4, 6]
            ) or (
                not q_trainees.filter(pk=q.employee.pk).exists()
                and q.type_of_person in [5]
            )
            if q.employee.pessoa_fisica != q.natural_person:
                adep = (
                    q.employee.dependentes.filter(
                        dependencias__dependente__pessoa_fisica=q.natural_person,  # IRRF
                        dependencias__tipo=1,  # IRRF
                    )
                    .dependencies_active_in(dt_ini, dt_now)
                    .exists()
                )
                pp = q.employee.paychecks.filter(
                    pensioner=q.natural_person, folha__dt_pagamento__gt=dt_ini
                ).exists()
                log.debug(
                    ">>> %s:%s ADEP:%s PP:%s TP:%s"
                    % (q.employee, q.natural_person, adep, pp, q.type_of_person)
                )
                if (not adep and q.type_of_person == 3) or (
                    not pp and q.type_of_person in [4, 6]
                ):
                    remove_reg |= True
            if remove_reg:
                q.delete()
                task.info(msg="Registro removido para pessoa %s" % q.nome, type_of=2)

        total = q_employees_d.count() + q_trainees.count()
        inc_progress = 100.0 / total if total else 0

        for s in q_employees_d.order_by("-ativo", "pessoa_fisica__nome"):
            pf = s.pessoa_fisica
            type_of_person = 2 if not s.ativo else 1

            q_pensioners_death = s.pensao_pagador.filter(
                type_of_pension=2
            )  # Verificando se é pagador de pensão por morte

            if not q_pensioners_death:
                obj, created = create_or_update_reg_qualification(
                    task, pf, type_of_person, employee=s, force=True
                )

            q_pensioners = s.paychecks.filter(
                folha__dt_pagamento__range=(dt_ini, dt_now)
            ).exclude(pensioner__isnull=True)
            # Apenas contracheques dos pensionistas desse servidor
            for ccp in q_pensioners:
                pf = ccp.pensioner
                type_of_person = 4 if ccp.employee_pays_pension == 2 else 6
                obj, created = create_or_update_reg_qualification(
                    task, pf, type_of_person, employee=s
                )

            q_dependents_irrf = (
                Dependencia.objects.irrf_actives(s, dt_now)
                .values("dependente__pessoa_fisica")
                .distinct()
            )
            for dep in q_dependents_irrf:
                pf = PessoaFisica.objects.get(pk=dep["dependente__pessoa_fisica"])
                type_of_person = 3
                obj, created = create_or_update_reg_qualification(
                    task, pf, type_of_person, employee=s
                )

            Task.objects.filter(pk=task.pk).update(
                progress=F("progress") + inc_progress
            )

        for e in q_trainees.order_by("-ativo", "pessoa_fisica__nome"):
            pf = e.pessoa_fisica
            type_of_person = 5
            obj, created = create_or_update_reg_qualification(
                task, pf, type_of_person, employee=e
            )

            Task.objects.filter(pk=task.pk).update(
                progress=F("progress") + inc_progress
            )

        state = "ready"
        message = "<p>Avaliação realizada com sucesso!</p>"
        task.info(
            msg="Finalizando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )

    except Exception as err:
        log.exception("{}".format(err))
        state = "failed"
        task.info(msg="Erro ao avaliar pessoas - {}".format(err), type_of=3)

    feedback("", 100)
    task.message = message
    task.state = state
    task.save()


@app.task()
def qualificate_batch(task, hook, user="", ged_file_id=None):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    # payroll = Payroll.objects.get(pk=payroll_id)
    message = "<p>Erro ao carregar arquivo de qualificação.</p>"
    log.debug("TASK 1 %s" % task)
    task = Task.objects.get(uuid=task)

    log.debug("TASK 2 %s" % task.uuid)

    try:
        set_current_user(user)
        feedback(
            "", 0, message="<p>Carregando arquivo de qualificação</p>", state=state
        )
        task.info(
            msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )
        task.description = "Carregando arquivo de qualificação."
        task.notificar_hermes = True
        task.tipo_processamento = TIPO_TASK_PROCESSAMENTO_ESOCIAL
        # Procurando por servidores que não entraram na folha
        # log.debug('TASK %s - Criando contracheques...' % task.uuid)

        # ff = '/app/D.CNS.CPF.003.20171222135247.01786078000146.92248586191.TXT.REJEITADO'
        ged_file = GedFile.objects.get(pk=ged_file_id)
        qe = QualifLoader(ged_file.absolute_path, original_basename=ged_file.filename)
        qe.execute(task)  # res

        state = "ready"
        message = "<p>Arquivo de qualificação carregado com sucesso!</p>"
        task.info(
            msg="Finalizando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )

    except Exception as err:
        log.exception("{}".format(err))
        state = "failed"
        task.info(
            msg="Erro ao carregar arquivo de qualificação - {}".format(err), type_of=3
        )

    feedback("", 100)
    task.message = message
    task.state = state
    task.save()
