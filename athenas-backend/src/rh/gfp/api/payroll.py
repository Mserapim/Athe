# -*- coding: utf-8 -*-

import threading

from dateutil.relativedelta import relativedelta

from contrib.decorator import login_required
from contrib.middleware import set_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils, get_json_engine, getLogger
from engine.mq.models import Task
from django.db.models import Count
from rh.gfp.models import BankingConvenant, BankingEmployeeTypePayroll, ConfigEvent
from rh.gfp.models import (
    DadoBancarioServidorFolha as BankingDataPersonPayroll,
    Evento as Event,
    Folha as Payroll,
    FolhaMensagem as PayrollMessage,
    FolhaModelo as ModelPayroll,
    FolhaTipo as PayrollType,
    Periodo as Period,
    GenreEvent,
    SpecieEvent,
)
from standard.models import Choice, Configuration
from rh.models import Banco

from rh.gfp.tasks import (
    management_remuneration_bases,
    process_consolidate_payroll,
    process_copy_payroll,
    process_evaluation_differences_payroll,
    process_payroll,
    process_recalculate_payroll,
    vincular_processos_rra,
)


log = getLogger(__name__)
json = get_json_engine()


class GFPPeriod(RestfulDRY):

    _model = Period

    full_text_index = (
        "mes__icontains",
        "ano__icontains",
    )

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.PeriodManage")')

    def select(self, args=[]):
        obj = {"success": True}
        period = int(self.request.POST.get("period"))
        if period > 0:
            period = Period.objects.get(pk=period)
            obj.update({"period": self.model_to_dict(period)})
            period = period.pk
        else:
            obj.update(
                {"period": "{'pk': '-1'}, 'next_period': '',  'previous_period': ''"}
            )

        cfg = Configuration.objects.get(application="gfp")
        cfg.set("periodo", period)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def model_to_dict(self, instance):
        _dict = super(GFPPeriod, self).model_to_dict(instance)
        next_period = instance.next
        if next_period:
            next_period = next_period.id
        previous_period = instance.previous
        if previous_period:
            previous_period = previous_period.id

        _dict.update({"next_period": next_period, "previous_period": previous_period})
        return _dict


class GFPPayrollType(RestfulDRY):

    # exclude_fields = ['publicacao_processo', 'processo', 'modelo']

    _model = PayrollType

    full_text_index = (
        "titulo__icontains",
        "id__iexact",
        "carater__icontains",
        "abreviatura__icontains",
    )

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.PayrollTypeManage")')

    def select(self, args=[]):
        obj = {"success": True}
        payroll_type = int(self.request.POST.get("payroll_type"))
        if payroll_type > 0:
            payroll_type = self._model.objects.get(pk=payroll_type)

            log.debug("payroll_type: %s" % payroll_type)

            if payroll_type:
                obj.update({"period": self.model_to_dict(payroll_type)})
        cfg = Configuration.objects.get(application="gfp")
        cfg.set("folhatipo", payroll_type.pk if payroll_type != 0 else payroll_type)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPPayrollTypeActive(GFPPayrollType):

    # exclude_fields = ['publicacao_processo', 'processo', 'modelo']

    def get_query(self):
        return super(GFPPayrollTypeActive, self).get_query().filter(ativo=True)

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.PayrollTypeActiveManage")')


class GFPBankingDataPersonPayroll(RestfulDRY):

    _model = BankingDataPersonPayroll

    full_text_index = (
        "dado_bancario_pessoa__pessoa__nome__icontains",
        "id__iexact",
    )

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.payroll.BankingDataPersonPayrollManage")'
        )


class GFPBankingPersonTypePayroll(RestfulDRY):

    _model = BankingEmployeeTypePayroll

    force_orm_single = True

    full_text_index = (
        "banking_person__pessoa__nome__icontains",
        "person__pessoafisica__servidor__matricula__icontains",
    )

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.payroll.BankingEmployeeTypePayrollManage")'
        )

    def model_to_dict(self, instance):
        _dict = super(GFPBankingPersonTypePayroll, self).model_to_dict(instance)
        _dict.update(
            {
                "banking_person_unicode": "{banco_numero} - Ag: {agencia} - Número: {numero}".format(
                    banco_numero=str(instance.banking_person.banco.numero),
                    agencia=instance.banking_person.agencia,
                    numero=instance.banking_person.conta_corrente_completa,
                )
            }
        )
        return _dict


class GFPModelPayroll(RestfulDRY):

    _model = ModelPayroll

    force_upper = False

    force_persist_boolean_fields = ["somente_folha", "previdencia", "somente_ativo"]

    full_text_index = ("titulo__icontains",)

    @login_required("JSON")
    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new rh.gfp.payroll.ModelPayrollManage()")


class GFPPayroll(RestfulDRY):

    _model = Payroll

    full_text_index = ("unicode_cache__icontains",)

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.PayrollManage")')

    def model_to_dict(self, instance):
        _dict = super(GFPPayroll, self).model_to_dict(instance)
        q_message = instance.messages.filter(servidor=None, paycheck=None, entry=None)
        _dict.update(
            {
                "pendencia_folha": instance.lancamentos.filter(
                    confirma_folha=None
                ).count()
                or 0,
                "pendencia_controle": instance.lancamentos.filter(
                    confirma_controle=None
                ).count()
                or 0,
                "fechado_por_unicode": (
                    (
                        "%s - %s"
                        % (
                            instance.fechado_por,
                            DateUtils.date_to_str(instance.dt_fechamento),
                        )
                    )
                    if instance.fechado_por and instance.dt_fechamento
                    else ""
                ),
                "processado_por_unicode": (
                    (
                        "%s - %s"
                        % (
                            instance.processado_por,
                            DateUtils.date_to_str(instance.dt_processado),
                        )
                    )
                    if instance.processado_por and instance.dt_processado
                    else ""
                ),
                "icons": self.get_icons(instance),
                "message": q_message.first().pk if q_message.exists() else None,
                "periodo_ano": instance.periodo.ano,
                "periodo_mes": instance.periodo.mes,
                "next": instance.next.id if instance.next else None,
                "previous": instance.previous.id if instance.previous else None,
                "is_working": instance == self.get_working_payroll(),
                "complement": (
                    f"COMPL. {instance.complement}" if instance.complement else ""
                ),
            }
        )
        return _dict

    @login_required("JSON")
    def get_working_payroll(self):
        payroll = None
        try:
            cfg = Configuration.objects.get(application="gfp")
            payroll = Payroll.objects.get(pk=cfg.get("folha"))
        except Exception as e:
            log.exception(e)
            pass
        return payroll

    @login_required("JSON")
    def working(self, args=[]):
        obj = {}

        working_payroll = self.get_working_payroll()
        if working_payroll:
            obj.update(
                {"success": True, "payroll": self.model_to_dict(working_payroll)}
            )
        else:
            obj.update(
                {
                    "success": False,
                    "message": "Não existe folha de trabalho configurada!",
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def select(self, args=[]):
        obj = {"success": False}
        payroll = Payroll.objects.get(pk=self.request.POST.get("payroll"))

        # log.debug(('PAYROLL: %s' % payroll)

        if payroll:
            cfg = Configuration.objects.get(application="gfp")
            cfg.set("folha", payroll.pk)
            obj.update({"success": True, "payroll": self.model_to_dict(payroll)})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_icons(self, instance):
        obj = []
        obj_status = {
            "iconCls": "icon-core icon-core-blank",
            "title": instance.get_status_display(),
        }
        if instance.status == 1:
            obj_status.update({"iconCls": "icon-core icon-core-run"})
        elif instance.status == 2:
            obj_status.update({"iconCls": "icon-core icon-core-waiting"})
        elif instance.status == 3:
            obj_status.update({"iconCls": "icon-fopag icon-closed-padlock"})
        elif instance.status == 4:
            obj_status.update({"iconCls": "icon-fopag icon-stamp-arrow"})

        obj.append(obj_status)

        if (
            instance.lancamentos.filter(confirma_folha=None).count() > 0
            or instance.lancamentos.filter(confirma_controle=None).count() > 0
        ):
            pendencias = {
                "iconCls": "icon-fopag icon-attention",
                "title": "Esta folha ainda tem pendências.",
            }
        else:
            pendencias = {
                "iconCls": "icon-core icon-core-success",
                "title": "Esta folha não tem pendências",
            }

        obj.append(pendencias)

        return obj

    @login_required("JSON")
    def evaluate_differences(self, args=[]):
        obj = {"success": True}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            payroll = self._model.objects.get(pk=int(self.request.POST.get("payroll")))
            if not (payroll.is_processed or payroll.is_closed):
                err = payroll.OpenedPayroll()
                obj.update(success=False, message="%s" % err.args[0])
                # log.debug((err.args[0])
            else:
                Task.start(
                    management_remuneration_bases,
                    description="Avaliando bases de remuneração por período %s"
                    % payroll,
                    period_id=payroll.periodo.pk,
                    user=self.request.user.id,
                )

                Task.start(
                    process_evaluation_differences_payroll,
                    description="Avaliando diferenças da folha %s" % payroll,
                    payroll_id=payroll.pk,
                    user=self.request.user.id,
                )
        self.response.write(json.encode(obj))

    def _recalculate(self, args=[]):
        rst = {"success": True}

        def process(request, payroll, log):
            # SETTING USER FOR LOCAL

            set_current_user(request.user)

            payroll.recalculate()

        payroll = Payroll.objects.get(pk=int(self.request.POST["payroll"]))

        t = threading.Thread(target=process, args=(self.request, payroll, log))
        t.start()
        rst["message"] = "O recálculo está sendo feito, aguarde!"

        return rst

    @login_required("JSON")
    def recalculate(self, args=[]):
        obj = {"success": True}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            payroll = self._model.objects.get(pk=int(self.request.POST.get("payroll")))
            # payroll_id = int(self.request.POST.get('payroll'))
            model_id = self.request.POST.get("model") or None
            possessions_group = self.request.POST.get("possession_group", None)

            # Task.start(
            #     management_remuneration_bases,
            #     description='Avaliando bases de remuneração por período %s' % payroll,
            #     period_id=payroll.periodo.pk,
            #     user=self.request.user.id,
            # )

            Task.start(
                process_recalculate_payroll,
                description="Recalculo da folha %s" % payroll,
                payroll_id=payroll.pk,
                model_id=model_id,
                user=self.request.user.id,
                possessions_group=possessions_group,
            )
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def summarize(self, args=[]):
        rst = {"success": True, "message": ""}
        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            rst.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            Task.start(
                process_payroll,
                user=self.request.user.id,
                payroll=int(self.request.POST.get("payroll")),
                simulate=self.request.POST.get("simulate", True),
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(rst))

    @login_required("JSON")
    def consolidate_payroll(self, args=[]):
        obj = {"success": True}

        payroll = self._model.objects.get(pk=int(self.request.POST.get("payroll")))
        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            Task.start(
                process_consolidate_payroll,
                description="Consolidando folha %s" % payroll,
                payroll_id=payroll.pk,
                user=self.request.user.id,
            )

        self.response.write(json.encode(obj))

    @login_required("JSON")
    def copy_payroll(self, args=[]):
        obj = {"success": True}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            payroll_source = self._model.objects.get(
                pk=int(self.request.POST.get("payroll"))
            )
            type_of_copy = self.request.POST.get("type_of_copy")
            generate_bases = False
            if "generate_bases" in self.request.POST:
                generate_bases = True
            periodo_to, p_created = Period.objects.get_or_create(
                ano=int(self.request.POST.get("year")),
                mes=int(self.request.POST.get("month")),
                defaults={
                    "salario_minimo": payroll_source.periodo.salario_minimo,
                    "salario_teto_adm": payroll_source.periodo.salario_teto_adm,
                    "salario_teto_membros": payroll_source.periodo.salario_teto_membros,
                    "salario_familia": payroll_source.periodo.salario_familia,
                    "auxilio_creche": payroll_source.periodo.auxilio_creche,
                    "auxilio_alimentacao": payroll_source.periodo.auxilio_alimentacao,
                },
            )

            new_payroll, created = Payroll.objects.get_or_create(
                periodo=periodo_to,
                tipo_folha=PayrollType.objects.get(
                    pk=int(self.request.POST.get("type_payroll"))
                ),
                complement=int(self.request.POST.get("complement") or 0),
                defaults={
                    # TODO Procurar um configuração para a data provável de pagamento
                    "dt_pagamento": (
                        (payroll_source.dt_fechamento + relativedelta(months=1))
                        if payroll_source.dt_fechamento
                        else None
                    )
                },
            )
            if generate_bases:
                Task.start(
                    management_remuneration_bases,
                    description="Avaliando bases de remuneração por período %s"
                    % new_payroll,
                    period_id=periodo_to.pk,
                    user=self.request.user.id,
                )

            # log.debug(('PAYROLL: %s' % payroll_source)

            Task.start(
                process_copy_payroll,
                description="Copiando folha %s > %s" % (payroll_source, new_payroll),
                payroll_source_id=payroll_source.pk,
                payroll_target_id=new_payroll.pk,
                type_of_copy=type_of_copy,
                user=self.request.user.id,
            )

        self.response.write(json.encode(obj))

    @login_required("JSON")
    def evaluate_remuneration_bases(self, args=[]):
        obj = {"success": True}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            payroll = self._model.objects.get(pk=int(self.request.POST.get("payroll")))
            Task.start(
                management_remuneration_bases,
                description="Avaliando bases de remuneração por período %s" % payroll,
                period_id=payroll.periodo.pk,
                user=self.request.user.id,
            )
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def vincular_folha_processo_rra(self, args=[]):
        obj = {"success": True}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            Task.start(
                vincular_processos_rra,
                folha=self.request.POST.get("folha"),
                rra=self.request.POST.get("rra"),
                user=self.request.user.id,
            )
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def complements(self, args=[]):
        obj = {"collection": [], "count": 0}
        query = Choice.objects.filter(app_label="gfp", name="COMPLEMENT_PAYROLL")
        complements = [
            {"value": -1, "description": "TODOS"},
            {"value": 0, "description": "BASE"},
        ]
        for comp in query:
            complements.append({"value": int(comp.value), "description": comp.label})
        obj.update(count=query.count())
        obj.update(collection=complements)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPOpenedPayroll(GFPPayroll):

    def get_query(self):
        query = super(GFPOpenedPayroll, self).get_query()
        return query.filter(status__in=[1, 2])


class GFPPayrollMessage(RestfulDRY):

    _model = PayrollMessage

    force_upper = False

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.PayrollMessageManage")')


class GFPGenreEvent(RestfulDRY):

    _model = GenreEvent

    full_text_index = ("genre_number__iexact", "title__icontains")

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.GenreEventManage")')


class GFPGenreEventTransparency(GFPGenreEvent):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.transparencychoice.genreevent.TransparencyManage")'
        )

    @login_required("JSON")
    def add_config_transparency(self, args=[]):
        rst = {
            "success": False,
            "message": "Não foi executado nada ainda.",
        }

        try:
            params = self.get_params(self.request.POST, check_case=True)
            if isinstance(params.get("pk"), (list, tuple)) is False:
                pks = [params.get("pk")]
            else:
                pks = params.get("pk")
            self._model.manage_config_transparency(
                pks, params.get("config_transparency")
            )
            rst["success"] = True
            rst["message"] = "Sucesso."
        except Exception as err:
            log.exception(err)
            rst["message"] = err

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def remove_config_transparency(self, args=[]):
        rst = {
            "success": False,
            "message": "Não foi executado nada ainda.",
        }

        try:
            params = self.get_params(self.request.POST, check_case=True)
            if isinstance(params.get("pk"), (list, tuple)) is False:
                pks = [params.get("pk")]
            else:
                pks = params.get("pk")
            self._model.manage_config_transparency(pks, None)
            rst["success"] = True
            rst["message"] = "Sucesso."
        except Exception as err:
            log.exception(err)
            rst["message"] = err

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class GFPSpecieEvent(RestfulDRY):

    _model = SpecieEvent

    def get_query(self):
        query = super(self.__class__, self).get_query()
        genre_event = self.request.GET.get("genre_event")

        if genre_event:
            events = Event.objects.filter(genre_event=genre_event)
            return SpecieEvent.objects.exclude(
                pk__in=[i.specie_event.pk for i in events]
            )

        return query


class GFPBancoConsignacao(RestfulDRY):

    _model = Banco

    full_text_index = (
        "numero__icontains",
        "nome__icontains",
        "pessoajuridica__cnpj__icontains",
        "pessoajuridica__razao_social__icontains",
    )


class GFPEvent(RestfulDRY):

    _model = Event

    full_text_index = (
        "titulo__icontains",
        "numero__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.EventManage")')

    def convert_value_of_type_booleanfield(self, value):
        log.info("VALUE: %s" % value)
        return (
            True
            if (value.lower() == "on" or (value and value.isdigit() and int(value)))
            else False
        )

    def get_new_number_display(self, event_number):

        if len(event_number) == 5:
            return "%s-%s" % (event_number[:3], event_number[3:5])
        else:
            return event_number

    def model_to_dict(self, instance):
        params = super(GFPEvent, self).model_to_dict(instance)

        params.update(
            automatico=instance.automated if instance.current_config else None,
            calculo=(
                instance.calculation.pk
                if instance.current_config and instance.calculation
                else ""
            ),
            numero_display=self.get_new_number_display(instance.numero),
            multi_calculate=(
                True
                if instance.current_config
                and instance.automated
                and instance.calculation
                and getattr(instance.calculation.cls, "MULTI_CALCULATE", False)
                else False
            ),
            join_on_multi=(
                True
                if instance.current_config
                and instance.automated
                and instance.calculation
                and getattr(instance.calculation.cls, "JOIN_ON_MULTI", False)
                else False
            ),
        )

        return params

    @login_required("JSON")
    def tags(self, args=[]):
        obj = {"collection": [], "count": 0}
        query = Choice.objects.filter(app_label="gfp", name="EVENT_TAGS")
        tags = [
            {"value": -1, "description": "TODOS"},
        ]
        for comp in query:
            tags.append({"value": int(comp.value), "description": comp.label.upper()})
        obj.update(count=len(tags))
        obj.update(collection=tags)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def character(self, args=[]):
        obj = {"collection": [], "count": 0}
        query = Choice.objects.filter(app_label="gfp", name="EVENT_CHARACTER")
        character = [
            {"value": -1, "description": "TODOS"},
        ]
        for comp in query:
            character.append(
                {"value": int(comp.value), "description": comp.label.upper()}
            )
        obj.update(count=query.count())
        obj.update(collection=character)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPConfigEvent(RestfulDRY):

    _model = ConfigEvent

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.ConfigEventManage")')

    def copy_old_incide(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda"}
        try:
            old_event = ConfigEvent.objects.get(pk=self.request.POST.get("old_event"))
            # log.debug((old_event)
            new_event = ConfigEvent.objects.get(pk=self.request.POST.get("new_event"))
            # log.debug((new_event)
            for event in old_event.focuses_on.all():
                new_event.focuses_on.add(event)
            new_event.save()
        except Exception as e:
            obj.update(message=str(e))
        else:
            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPBankingConvenant(RestfulDRY):

    _model = BankingConvenant

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = ("identification__icontains", "bank__numero__iexact")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.payroll.BankingConvenantManage")')


class GFPActiveBankingConvenant(GFPBankingConvenant):
    """Summary."""

    def get_query(self):
        """Summary.

        Returns:
            QUERYSET: Filtered active convenants
        """
        return super(GFPActiveBankingConvenant, self).get_query().filter(active=True)


class GFPPeriodosFolha(RestfulDRY):

    _model = Period

    def get_query(self):

        # A lógica abaixo está comentada propositalmente.
        # Essa lógica busca os registros do model Periodo baseado nos registros de Folha existentes.
        # Porém essa lógica ficou muito lenta, então foi adotado a estratégia e retornar direto os registros
        # do model Periodo ordenado por ano e mês.
        # Caso em algum momento tenha diferença entre os Periodos e Folhas criadas, analisar para ativar essa lógica.

        # q_folha = Payroll.objects.values(
        #     'pk','periodo__ano','periodo__mes'
        # ).annotate(
        #     Count('periodo__ano'),
        #     Count('periodo__mes')
        # ).order_by(
        #     '-periodo__ano',
        #     '-periodo__mes','pk'
        # )
        #
        # periodos_ids = []
        # for ano_mes_folha in q_folha:
        #     q_periodo = Period.objects.filter(ano=ano_mes_folha['periodo__ano'], mes=ano_mes_folha['periodo__mes'])
        #     if q_periodo.exists():
        #         periodos_ids.append(q_periodo.first().pk)

        # return super(GFPPeriodosFolha, self).get_query().filter(pk__in=periodos_ids)

        return super(GFPPeriodosFolha, self).get_query().order_by("-ano", "-mes")
