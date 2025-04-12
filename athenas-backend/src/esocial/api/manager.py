# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User

from contrib.decorator import login_required, profile
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from engine.mq.models import Task
from esocial.const import CATEGORIA_EVENTO_CADASTRO, PROCESS_STATUS_EVENT_VALIDS_SENT
from esocial.models import (
    BatchEvent,
    Event,
    EventDependency,
    Occurrence,
    PayrollPeriod,
    get_current_config,
)
from esocial.security.xml.manager import _load_data_to_string
from esocial.tasks.generation import (
    clear_restricted_production_task,
    clone_production_base_task,
    create_batches_task,
    create_events_task,
    delete_events_not_sent_task,
    delete_events_task,
    generate_delete_events_task,
)
from esocial.tasks.tasks import process_batches
from esocial.tasks.utils import _task_conflict_with_all, task_conflict_with_all
from esocial.utils import esocial_environment, process_xml_diff
from rh.gfp.models import Folha, Periodo
from rh.models import Servidor

log = getLogger(__name__)


class ESOCIALEvent(RestfulDRY):

    _model = Event

    force_orm_single = True

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "pk__iexact",
        "identifier__iexact",
        "acronym__icontains",
        "search_cache__icontains",
        "description__icontains",
    )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []
    def get_query(self):
        return super(ESOCIALEvent, self).get_query().filter(internal=False)

    def get_instance_model(self, pk):
        """Este método retorna a instância de pk.

        Args:
            pk (int)
        """
        obj = super().get_instance_model(pk)
        return obj.event

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        from_to_action = {
            1: "icon-esocial icon-add",
            2: "icon-esocial icon-edit",
            3: "icon-esocial icon-minus",
            4: "icon-esocial icon-add-all",
        }
        icons.append(
            {
                "iconCls": from_to_action.get(
                    instance.action, "icon-esocial icon-blank"
                ),
                "alt": instance.get_action_display(),
            }
        )
        icons.append(
            {
                "iconCls": (
                    "icon-esocial icon-run-ok"
                    if instance.xsd_schema_validated
                    else "icon-esocial icon-run-error"
                ),
                "alt": (
                    "XML Válido" if instance.xsd_schema_validated else "XML inválido"
                ),
            }
        )
        icons.append(
            {
                "iconCls": (
                    "icon-esocial icon-clear" if instance.has_exclusion_cache else ""
                ),
                "alt": (
                    f"Evento excluído por: {instance.modified_by_event}"
                    if instance.has_exclusion_cache
                    and hasattr(instance, "modified_by_event")
                    else ""
                ),
            }
        )

        if instance.process_status == 1:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-waiting-send",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status == 2:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-waiting",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status == 3:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-pack",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status == 4:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-pack-sent",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status == 5:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-block",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status == 202:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-warn",
                    "alt": instance.get_process_status_display(),
                }
            )
        if instance.process_status in (201, 210):
            icons.append(
                {
                    "iconCls": "icon-esocial icon-success",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status >= 301:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-error",
                    "alt": instance.get_process_status_display(),
                }
            )
        else:
            icons.append({"iconCls": "icon-esocial icon-blank", "alt": ""})

        return icons

    @login_required(type="JSON")
    def xml(self, args=[]):
        rst = {
            "xml_content": "",
            "xml_receipt": "",
            "xml_process": "",
            "identifier": "",
            "success": False,
            "message": "Nada feito ainda!",
        }
        success = False
        xml_content = identifier = xml_diff = ""
        try:
            instance = Event.objects.get(pk=self.request.POST.get("id"))
            identifier = instance.id
            xml_content = _load_data_to_string(instance.event.xml)
            try:
                xml_diff = process_xml_diff(instance.event.xml_diff)
            except Exception as err:
                log.exception(err)
                xml_diff = instance.event.xml_diff

            msg = "XML gerado com sucesso"
            success = True
        except Exception as e:
            log.exception(e)
            msg = "{}".format(e)

        rst.update(
            xml_content=xml_content,
            xml_diff=xml_diff,
            msg=msg,
            success=success,
            identifier=identifier,
        )

        self.renderer(rst)

    @profile(
        f"{settings.UPLOAD_STORE_DIR}/profiles/esocialevent_validate.prof", time=True
    )
    @login_required(type="JSON")
    def validate(self, args=[]):
        rst = {"success": False, "showMessage": True, "message": "Nada feito ainda!"}
        result = False
        event = Event.objects.get(pk=self.request.POST.get("id")).event
        xsd_schema_validated = event.xsd_schema_validated
        try:
            xsd_schema_validated_new = event.set_validation_xml_schema(assert_test=True)
            msg = "Validação realizada com sucesso."
            if xsd_schema_validated == xsd_schema_validated_new:
                msg = "Não houve alterações."
            result = True
        except Exception as err:
            log.exception(err)
            msg = f"{err}"

        rst.update(success=result, message=msg, instance=self.model_to_dict(event))
        self.renderer(rst)

    @login_required(type="JSON")
    def create_events(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            period = (
                self.request.POST.get("period")
                if "period" in self.request.POST
                else "None"
            )
            events = self.request.POST.getlist("events")

            if not task_conflict_with_all():
                Task.start(
                    create_events_task,
                    event_kind=self.request.POST.getlist("event_kind"),
                    user=get_current_user().pk,
                    period=period,
                    events=events,
                    # queue='low-priority'
                )
            else:
                raise Exception("Existe uma tarefa em execução. Aguarde o término.")

        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Criação de eventos solicitada!",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def generate_events_ti_registration(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            BatchEvent.generate_events_ti_registration_call_task()
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Geração de eventos de TI, Cadastro e Folha (e-Social)!",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def generate_events_ti(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            BatchEvent.generate_events_ti_call_task()
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Geração de eventos de TI, Cadastro e Folha (e-Social)!",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def generate_events_registration(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        categories = CATEGORIA_EVENTO_CADASTRO[
            self.request.POST.get("generate_category")
        ]
        try:
            BatchEvent.generate_events_registration_call_task(categories=categories)
        except Exception as e:
            log.exception(e)
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Geração de eventos de TI, Cadastro e Folha (e-Social)!",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def generate_events_sst(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            BatchEvent.generate_events_sst_call_task()
        except Exception as e:
            log.exception(e)
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Geração de eventos de TI, Cadastro e Folha (e-Social)!",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def generate_events_payroll(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        period = self.request.POST.get("period")
        period_end = self.request.POST.get("period_end")
        action = self.request.POST.get("generate_action")

        periods = [int(period)]
        if period_end:
            period_start = Periodo.objects.get(pk=int(period))
            periods.append(period_start.pk)
            period_end = Periodo.objects.get(pk=int(period_end))
            next_period = period_start.next_period()
            while next_period:
                periods.append(next_period.pk)
                if next_period == period_end:
                    break
                next_period = next_period.next_period()

        def validate():
            payroll = Folha.objects.filter(periodo__pk__in=periods).exclude(
                status__in=(3, 4)
            )
            message = ""
            for proll in payroll:
                message += f"{proll} "

            if message:
                raise Exception(
                    f"As folhas ({message}) não estão em PROCESSADO ou FECHADO."
                )

        try:
            if period:
                # validate()
                if not action:
                    BatchEvent.generate_events_payroll_call_task_list(period=periods)
                elif action == "payroll_process":
                    BatchEvent.generate_events_payroll_process_call_task_list(
                        period=periods, events=["s1200", "s1202", "s1207", "s1210"]
                    )
                elif action == "payroll_process_demonstratives":
                    BatchEvent.generate_events_payroll_process_call_task_list(
                        period=periods, events=["s1200", "s1202", "s1207"]
                    )
                elif action == "payroll_process_payments":
                    BatchEvent.generate_events_payroll_process_call_task_list(
                        period=periods, events=["s1210"]
                    )
                elif action == "payroll_deletion":
                    BatchEvent.generate_delete_events_payroll_call_task(period=period)
                elif action == "payroll_demonstrative_deletion":
                    BatchEvent.generate_delete_events_payroll_call_task(
                        period=period, events=["s1200", "s1202", "s1207"]
                    )
                elif action == "payroll_payment_deletion":
                    BatchEvent.generate_delete_events_payroll_call_task(
                        period=period, events=["s1210"]
                    )
                elif action == "payroll_closing":
                    BatchEvent.generate_close_events_payroll_call_task(period=period)
                elif action == "payroll_closing_analysis":
                    PayrollPeriod.analysis_call_task(period=period)
                elif action == "payroll_reopening":
                    BatchEvent.generate_reopen_events_payroll_call_task(period=period)
            else:
                raise Exception(
                    "Não foi informado um período para a geração dos eventos"
                )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Geração de eventos de TI, Cadastro e Folha (e-Social)!",
            )

        self.renderer(rst)

    @login_required(type="JSON")
    def generate_delete_events(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if not task_conflict_with_all():
                events = self.request.POST.getlist("id")
                Task.start(
                    generate_delete_events_task,
                    user=get_current_user().pk,
                    events=events,
                )
            else:
                raise Exception("Existe uma tarefa em execução. Aguarde o término.")

        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Geração de evento(s) de exclusão solicitada.",
            )

        self.renderer(rst)

    @login_required(type="JSON")
    def archive_success(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            ups = (
                Event.objects.filter(
                    process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT
                )
                .exclude(archived=True)
                .update(archived=True)
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message=f"Total de eventos arquivados: {ups}!")
        self.renderer(rst)

    @login_required(type="JSON")
    def archive_error(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            ups = (
                Event.objects.filter(
                    process_status__in=[401, 402, 403, 404, 405, 406, 407]
                )
                .exclude(archived=True)
                .update(archived=True)
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message=f"Total de eventos arquivados: {ups}!")
        self.renderer(rst)

    @login_required(type="JSON")
    def archive_selecteds(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        events_ids = [int(id) for id in self.request.POST.getlist("id")]

        try:
            ups = (
                Event.objects.filter(
                    pk__in=events_ids,
                    process_status__in=(201, 202, 401, 402, 403, 404, 405, 406, 407),
                )
                .exclude(archived=True)
                .update(archived=True)
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message=f"Total de eventos arquivados: {ups}!")
        self.renderer(rst)

    @login_required(type="JSON")
    def employee_exclude(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        employee = [int(pk) for pk in self.request.POST.getlist("id")]

        try:
            config = get_current_config()
            for employee in Servidor.objects.filter(matricula__in=employee):
                config.employee_exclude.add(employee)
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            message = "Todos adicionados com sucesso!"
            rst.update(success=True, message=message, showMessage=message)
        self.renderer(rst)

    @login_required(type="JSON")
    def repport_success(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        event = None
        try:
            event = Event.objects.get(pk=self.request.POST.get("id"))
            event.repport_success()
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            message = "Status de processamento modificado com sucesso!"
            rst.update(
                success=True,
                message=message,
                showMessage=message,
                instance=self.model_to_dict(event) if event else None,
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def repport_error(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        event = None
        try:
            event = Event.objects.get(pk=self.request.POST.get("id"))
            event.repport_error()
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            message = "Status de processamento modificado com sucesso!"
            rst.update(
                success=True,
                message=message,
                showMessage=message,
                instance=self.model_to_dict(event) if event else None,
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def occurrences_list(self, *args):
        occurrences = Occurrence.objects.distinct("code")
        obj = {}
        obj.update(
            root=[
                {
                    "pk": x.code,
                    "desc": str(x.code) + " - " + x.description.split(". A")[0],
                    "boxLabel": x.code,
                    "name": x.code,
                    "inputValue": x.code,
                    "checked": False,
                }
                for x in occurrences
            ]
        )
        obj.get("root").insert(0, {"pk": 0, "description": "TODAS"})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @login_required(type="JSON")
    def update_process_status(self, *args):
        rst = {"success": True, "message": "Nada feito ainda!"}
        try:
            if "event" not in self.request.POST:
                raise Exception("Evento não informado!")
            process_status = Event.objects.get(
                pk=int(self.request.POST.get("event"))
            ).event.update_process_status_ignore_validate(
                int(self.request.POST.get("process_status"))
            )
            rst.update(
                message=f"Status do processamento modificado para {process_status}!"
            )
        except Exception as err:
            log.exception(err)
            rst.update(success=False, message=f"{err}")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(rst))

    @login_required(type="JSON")
    def set_deleted(self, *args):
        rst = {"success": True, "message": "Nada feito ainda!"}
        try:
            if "events" not in self.request.POST:
                raise Exception("Evento(s) não informado(s)!")
            Event.set_deleted(events=self.request.POST.getlist("events"))
            rst.update(message='Evento(s) marcado(s) como "apagado(s)".')
        except Exception as err:
            log.exception(err)
            rst.update(success=False, message=f"{err}")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(rst))


class ESOCIALEventNotSend(RestfulDRY):

    _model = Event

    force_orm_single = True

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "acronym__icontains",
        "identifier__iexact",
        "search_cache__icontains",
        "description__icontains",
    )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []
    def get_query(self):
        return super(ESOCIALEventNotSend, self).get_query().summarize()


class ESOCIALBatchEvent(RestfulDRY):

    _model = BatchEvent

    force_orm_single = True

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = ("id__icontains", "description__icontains")

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            "Ext._create('esocial.manager.Manage', {environment: '%s'})"
            % esocial_environment()
        )

    def model_to_dict(self, instance):
        _dict = super().model_to_dict(instance)
        process_status_display = None
        if instance.delivery_status > 2:
            process_status_display = instance.get_process_status_display()
        _dict.update(process_status_display=process_status_display)
        return _dict

    def permissao_admin(self):
        """Checar se o usuário pertence ao grupo mpmt-perfil-esocial-admin,
        que o qual terá permissão forçar erro no lotes"""

        group_name = "mpmt-perfil-esocial-admin"
        if group_name:
            user = get_current_user()
            return user.groups.filter(name=group_name).exists()
        else:
            return False

    @login_required(type="JSON")
    def send(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            batch = BatchEvent.objects.get(pk=self.request.POST.get("id"))
            batch.send_to_esocial()
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Lote %s enviado com sucesso para a base do eSocial" % batch,
                instance=self.model_to_dict(batch),
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def consult(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            batch = BatchEvent.objects.get(pk=self.request.POST.get("id"))
            batch.consult_process()
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Consulta de processamento do lote %s realizada com sucesso!"
                % batch,
                instance=self.model_to_dict(batch),
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def error(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if self.permissao_admin():
                BatchEvent.objects.filter(pk=self.request.POST.get("id")).update(
                    process_status=401
                )
                rst.update(success=True, message="Ação realizada com sucesso.")
            else:
                rst.update(
                    success=False,
                    message="Não possui permissão para executar essa ação.",
                )
        except Exception as e:
            rst.update(message="{}".format(e))

        self.renderer(rst)

    @login_required(type="JSON")
    def xml(self, args=[]):
        rst = {
            "xml_content": "",
            "xml_receipt": "",
            "xml_process": "",
            "identifier": "",
            "success": False,
            "message": "Nada feito ainda!",
        }
        success = False
        xml_content = xml_receipt = xml_process = identifier = ""
        try:
            instance = BatchEvent.objects.get(pk=self.request.POST.get("id"))
            xml = instance.file_path
            identifier = instance.id
            receipt = xml.replace(".xml", "-receipt.xml")
            process = xml.replace(".xml", "-process.xml")

            xml_content = _load_data_to_string(instance.xml)
            if os.path.exists(receipt):
                xml_receipt = _load_data_to_string(receipt)

            if os.path.exists(process):
                xml_process = _load_data_to_string(process)

            msg = "XML gerado com sucesso"
            success = True
        except Exception as e:
            log.exception(e)
            msg = "{}".format(e)

        rst.update(
            xml_content=xml_content,
            xml_receipt=xml_receipt,
            xml_process=xml_process,
            identifier=identifier,
            msg=msg,
            success=success,
        )

        self.renderer(rst)

    @login_required(type="JSON")
    def process_all(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if not task_conflict_with_all():
                Task.start(process_batches, user=get_current_user().pk)
            else:
                raise Exception("Existe uma tarefa em execução. Aguarde o término.")
        except Exception as err:
            log.exception(err)
            rst.update(message=f"{err}")
        else:
            rst.update(
                success=True,
                message=None,
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def active_process(self, args=[]):
        rst = {
            "success": False,
            "processing": False,
            "process": "",
            "message": "Nada feito ainda!",
        }

        process = {}
        message = None
        try:
            process = _task_conflict_with_all(prefer_user=True)
            user = process.get("kwargs", {}).get("user", None)
            time_start = process.get("time_start", datetime.now())
            if user:
                now = datetime.now()
                user = User.objects.filter(pk=user).last()
                duration = now - datetime.fromtimestamp(time_start)
                duration = duration.total_seconds() / 60.0
                message = f"{process.get('name', '')} - começou há {round(duration, 2)} min - {user}".upper()
        except Exception as err:
            log.exception(err)
            rst.update(message=f"{err}")
        else:
            rst.update(
                success=True,
                processing=True if process else False,
                process=process.get("name", ""),
                message=message,
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def create_initial(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        obj, created = Event.objects.update_or_create(
            first_name="John",
            last_name="Lennon",
            defaults={"first_name": "Bob"},
        )
        try:
            self.consult_process()
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Consulta de processamento do lote %s realizada com sucesso!"
                % self,
                instance=self.model_to_dict(self),
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def create_batches(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if not task_conflict_with_all():
                Task.start(create_batches_task, user=get_current_user().pk)
            else:
                raise Exception("Existe uma tarefa em execução. Aguarde o término.")
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Criação de lotes solicitada!",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def clear_restricted_production(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if get_current_user().is_superuser:
                Task.start(clear_restricted_production_task, user=get_current_user().pk)
            else:
                raise Exception("Usuário não possui permissão!")
        except Exception as e:
            log.exception(e)
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Base local apagada. Lote de limpeza do ambiente de produção restrita foi gerado e enviado.",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def clear_local(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if get_current_user().is_superuser:
                Task.start(delete_events_task, user=get_current_user().pk)
            else:
                raise Exception("Usuário não possui permissão!")
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Base local está sendo apagada. Você pode verificar a finalização junto com as demais notificações.",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def clear_local_not_sent(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if get_current_user().is_superuser:
                Task.start(delete_events_not_sent_task, user=get_current_user().pk)
            else:
                raise Exception("Usuário não possui permissão!")
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Base local (eventos não enviados) está sendo apagada. \
                    Você pode verificar a finalização junto com as demais notificações.",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def clone_production_base(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if get_current_user().is_superuser:
                Task.start(clone_production_base_task, user=get_current_user().pk)
            else:
                raise Exception("Usuário não possui permissão!")
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Base de produção está sendo clonada para ambiente de desenvolvimento. \
                    Você pode verificar a finalização junto com as demais notificações.",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def archive_success(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            ups = (
                BatchEvent.objects.filter(
                    process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT
                )
                .exclude(archived=True)
                .update(archived=True)
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message=f"Total de pacotes arquivados: {ups}!")
        self.renderer(rst)

    @login_required(type="JSON")
    def archive_error(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            ups = (
                BatchEvent.objects.filter(process_status__in=(401, 402, 403, 404, 405))
                .exclude(archived=True)
                .update(archived=True)
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message=f"Total de pacotes arquivados: {ups}!")
        self.renderer(rst)

    @login_required(type="JSON")
    def archive_selecteds(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        events_ids = (int(ident) for ident in self.request.POST.getlist("id"))

        try:
            ups = (
                BatchEvent.objects.filter(
                    pk__in=events_ids,
                    process_status__in=(201, 202, 401, 402, 403, 404, 405),
                )
                .exclude(archived=True)
                .update(archived=True)
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message=f"Total de pacotes arquivados: {ups}!")
        self.renderer(rst)

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        if instance.delivery_status == 1:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-waiting-send",
                    "alt": instance.get_process_status_display(),
                }
            )
        if instance.delivery_status == 2:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-pack",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.delivery_status in (201, 202) and instance.process_status == 101:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-pack-sent",
                    "alt": instance.get_process_status_display(),
                }
            )
        if instance.process_status == 201:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-success",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status == 202:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-warn",
                    "alt": instance.get_process_status_display(),
                }
            )
        elif instance.process_status >= 301:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-error",
                    "alt": instance.get_process_status_display(),
                }
            )
        else:
            icons.append({"iconCls": "icon-esocial icon-blank", "alt": ""})
        return icons


class ESOCIALBatchEventEmployee(ESOCIALBatchEvent):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            "Ext._create('esocial.manager.ManageEmployee', {environment: '%s'})"
            % esocial_environment()
        )


class ESOCIALEventDependency(RestfulDRY):

    _model = EventDependency

    force_orm_single = True

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "event__acronym__icontains",
        "event__identifier__iexact",
        "event__search_cache__icontains",
        "event__description__icontains",
    )

    def model_to_dict(self, instance):
        _dict = super(ESOCIALEventDependency, self).model_to_dict(instance)
        _dict.update(
            dependency_process_status_display=f"{instance.dependency.get_process_status_display()}"
        )
        return _dict
