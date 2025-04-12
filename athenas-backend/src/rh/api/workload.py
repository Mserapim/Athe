# -*- coding: utf-8 -*-

import json
import threading

from django.db.models import Q

from contrib.decorator import login_required
from contrib.middleware import set_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils, Locker, getLogger
from engine.models import TaskSession
from rh.models import (
    CargaHoraria,
    HoursWorkContract,
    Publicacao,
    Servidor,
    MovimentacaoPosse,
)
from standard.models import Choice

log = getLogger(__name__)
# json = get_json_engine()


class RHWorkload(RestfulDRY):

    _model = CargaHoraria

    """ Em caso de delete ou update multi row força utilizar o ORM para realizar as ações."""
    force_orm_single = True

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workload.WorkloadManage")')

    @login_required(type="JSON")
    def get_employeers(self, args=[]):
        query = Servidor.objects.filter(tipo="S", ativo=True).order_by(
            "pessoa_fisica__nome"
        )
        count = query.count()

        obj = {
            "count": count,
            "collection": [
                {
                    "pk": employee.pk,
                    "matricula": employee.matricula,
                    "servidor": employee.pessoa_fisica.nome,
                }
                for employee in query
            ],
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def apply_workload_task(self, workload, task=None):
        lock_file = Locker.create_lock("apply_workload")
        task = TaskSession.start_execution("Carga horária") if not task else task
        log.debug("TASK: GENERATE WORKLOAD")
        try:
            jornada = (
                HoursWorkContract.objects.get(pk=workload["jornada_id"])
                if workload["jornada_id"] != ""
                else None
            )
            publication = (
                Publicacao.objects.get(pk=workload["publication"])
                if workload["publication"] != ""
                else None
            )
            for employee in workload["employees"]:
                try:
                    mov_posse = MovimentacaoPosse.objects.filter(
                        servidor=employee, ativo=True
                    ).first()
                    cg = CargaHoraria(
                        tipo=1,  # semanal
                        jornada_trabalho=jornada,
                        publicacao=publication,
                        data_inicio=(
                            mov_posse.data_posse
                            if mov_posse.data_posse
                            > DateUtils.str_to_date(workload["start_date"])
                            else DateUtils.str_to_date(workload["start_date"])
                        ),
                        data_fim=(
                            DateUtils.str_to_date(workload["end_date"])
                            if workload["end_date"] != ""
                            else None
                        ),
                        servidor=employee,
                        quantidade=jornada.jornada_semanal,
                    )
                    cg.save()
                    task.info("Adicionada carga horária para %s" % cg.servidor)
                except Exception as err:
                    task.info(
                        "Erro ao adicionar carga horária no servidor %s" % employee, 3
                    )
                    log.debug("ERRO: %s" % err)
        except Exception as err:
            task.info(err, 3)

        task.finish_execution()
        Locker.remove_lock(lock_file)

    @login_required("JSON")
    def apply_workload(self, args=[]):
        response = {"success": False, "message": "Nada foi feito ainda."}
        try:
            jornada_id = self.request.POST.get("jornada_trabalho", None)
            start_date = self.request.POST.get("data_inicio")
            end_date = self.request.POST.get("data_fim")
            publication = self.request.POST.get("publicacao")
            workplace = self.request.POST.get("workplace", None)
            all_employee = self.request.POST.get("allEmployee", False)
            types_by_possession = self.request.POST.get(
                "types_by_possession", None
            ).split(",")

            if not start_date or not jornada_id:
                raise Exception("Jornada ou data início não informado(s).")
            elif (
                jornada_id
                and not HoursWorkContract.objects.filter(pk=jornada_id).exists()
            ):
                raise Exception("Jornada de trabalho não encontrada.")
            else:
                employees = Servidor.objects.filter(
                    pk__in=CargaHoraria.objects.filter(
                        active=True,
                        servidor__ativo=True,
                        servidor__type_by_possession__in=types_by_possession,
                    )
                    .distinct()
                    .values("servidor__pk")  # [:10]
                )
                if not all_employee:
                    if workplace:
                        employees = employees.filter(
                            servidor_lotacao__lotacao__pk=int(workplace),
                            servidor_lotacao__ativo=True,
                        )

                workload = {
                    "jornada_id": jornada_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "publication": publication,
                    "employees": employees,
                }

                def process(request, workload, log):
                    set_current_user(request.user)
                    log.debug("INIT PROCESS WORKLOAD...")
                    if workload:
                        self.apply_workload_task(workload)

                t = threading.Thread(target=process, args=(self.request, workload, log))
                t.start()
        except Exception as err:
            log.exception(err)
            response.update(message="%s" % err.args[0])
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.renderer(response)

    def employee_type_by_possessions(self, args=[]):
        result = {
            "success": False,
            "message": "Nothing made yet.",
            "count": 0,
            "collection": [],
        }

        try:
            types_by_possession = Choice.objects.filter(
                app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION", active=True
            ).exclude(
                cvalue__in=[
                    "MCM",
                    "MEC",
                    "TCR",
                    "CTR",
                    "SAP",
                    "MAP",
                    "RFC",
                    "JCA",
                    "XXX",
                    "MBR",
                    "MBR2",
                    "MEL",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                    "MAP2",
                    "APO",
                    "BFP",
                    "REX",
                    "COE",
                ]
            )
        except Exception as e:
            result.update(message=str(e))
        else:
            result.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=types_by_possession.count(),
                collection=[
                    {"value": tp.cvalue, "description": str(tp.label)}
                    for tp in types_by_possession
                ],
            )

        self.response["content-type"] = "text/json"
        self.response.write(json.dumps(result))
