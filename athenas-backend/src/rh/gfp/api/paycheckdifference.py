# -*- coding: utf-8 -*-

import json
import time
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.db.models import CharField, Value, Q
from django.db.models.functions import Concat

from contrib.controller import ContentType
from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger
from contrib.decorator import login_required
from standard.models import Choice
from rh.gfp.models import (
    CorrectionFactor,
    Folha as Payroll,
    FolhaEvento as Entry,
    PaycheckDifference,
    PaycheckDifferenceConfig,
    PaycheckDifferenceItem,
    PeriodPayroll,
    DifferencePayroll,
    Evento as Event,
)
from engine.mq.models import Task
from ged.models import Arquivo as File
from contrib.middleware import get_current_user

# from rh.gfp.tasks import load_correction_file

from rh.gfp.tasks_paycheckdifference import (
    calculate_period_task,
    applicate_difference_task,
)
from rh.gfp.api.payroll import GFPPayroll

log = getLogger(__name__)
json_engine = get_json_engine()


class GFPCorrectionFactor(RestfulDRY):

    _model = CorrectionFactor

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "identifier__icontains",
        "ref_payment_cache__icontains",
        "ref_difference_cache__icontains",
    )

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("rh.gfp.paycheckdifference.CorrectionFactorManage")')


class GFPEntryDifference(RestfulDRY):

    _model = Entry

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "contracheque__folha__unicode_cache__icontains",
        "evento__numero__icontains",
        "evento__titulo__icontains",
        "contracheque__servidor__matricula__iexact",
        "contracheque__servidor__pessoa_fisica__nome__icontains",
    )

    only_fields = [
        "contracheque",
        "valor",
        "correct_valor",
        "correct_value",
        "patronal",
        "correct_patronal",
        "correct_employer_contribution",
        "diff_valor_aprovisionado",
        "diff_value_provisioned",
        "diff_patronal_aprovisionado",
        "diff_employer_contribution_provisioned",
        "created_at",
        "created_by",
        "modified_at",
        "modified_by",
    ]

    def get_query(self):
        return self._model.with_differences.all()

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("rh.gfp.paycheckdifference.EntryManage")')

    def setDifferenceEntry(self, args=[]):
        obj = {"success": False}
        try:
            Entry.objects.filter(pk=self.request.POST.get("entry")).update(
                paycheck_difference=self.request.POST.get("difference")
            )
            PaycheckDifference.objects.get(
                pk=self.request.POST.get("difference")
            ).save()
            pass
        except Exception as err:
            obj.update(message="Ocorreu um erro ao tentar adicionar folha evento!")
            log.exception(err)
        else:
            obj.update(success=True)
            obj.update(message="Evento adicionado com sucesso!")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @login_required("JSON")
    def load_file(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        correctionfile_id = self.request.POST.get("correctionfile")
        startyear = self.request.POST.get("startyear")
        month = self.request.POST.get("month")
        year = self.request.POST.get("year")
        correctionfile = (
            File.objects.get(pk=correctionfile_id).pk if correctionfile_id else None
        )

        try:
            # Task.start(
            #     load_correction_file,
            #     startyear=int(startyear),
            #     year=int(year),
            #     month=int(month),
            #     user=get_current_user().pk,
            #     correctionfile=correctionfile,
            #     success='''<p>Arquivo de fator de correções carregado com sucesso!</p>'''
            # )
            pass
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Carregamento do arquivo do fator de correções requisitado com sucesso, você será avisado quando o mesmo for concluído.",
            )

        self.renderer(rst)


class GFPPayCheckDifference(RestfulDRY):

    _model = PaycheckDifference

    force_orm_single = True

    full_text_index = (
        "event__numero__iexact",
        "event__titulo__icontains",
        "employee__matricula__iexact",
        "employee__pessoa_fisica__nome__icontains",
        "identifier__icontains",
        "title__icontains",
    )

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("rh.gfp.paycheckdifference.PayCheckDifferenceManage")')

    def apply(self, args=[]):
        rst = {"success": False, "message": "Não foi executado nada ainda."}
        # log.debug(('POST: %s' % self.request.POST)
        # log.debug((self.request.POST.get('payroll'))
        payroll = Payroll.objects.get(pk=self.request.POST.get("payroll"))
        if payroll.is_processed:
            rst["message"] = "Não pode ser aplicado diferenças em uma folha processada!"
        else:
            title = self.request.POST.get("title", "")
            installments = self.request.POST.get("installments", 1)
            rra = self.request.POST.get("rra", "")
            reason_difference = self.request.POST.get("reason_difference", 1)
            correction_factor_identifier = self.request.POST.get(
                "correction_factor", None
            )
            single_mode = (
                self.request.POST.get("single_mode", 0) and self._model.SINGLE_MODE
            )
            separate_ref_mode = (
                self.request.POST.get("separate_ref_mode", 0)
                and self._model.SEPARETE_REF_MODE
            )

            diff_mode = single_mode + separate_ref_mode

            q_entries = Entry.with_differences.filter(
                pk__in=self.request.POST.getlist("objects")
            ).order_by("servidor", "evento", "folha")

            errors = self._model.create_differences(
                payroll,
                entries=q_entries,
                title=title,
                diff_mode=diff_mode,
                installments=installments,
                correction_factor_identifier=correction_factor_identifier,
                rra=rra,
                reason_difference=reason_difference,
            )

            rst["success"] = (not errors and True) or False
            rst["message"] = "<br />{}".format(errors) if errors else ""

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def apply2(self, args=[]):
        rst = {"success": False, "message": "Não foi executado nada ainda."}
        # log.debug(('POST: %s' % self.request.POST)
        payroll = Payroll.objects.get(pk=self.request.POST.get("payroll"))
        if payroll.is_processed:
            rst["message"] = "Não pode ser aplicado diferenças em uma folha processada!"
        else:
            title = self.request.POST.get("title", "")
            # installments = self.request.POST.get('installments', 1)
            # correction_factor_identifier = self.request.POST.get('correction_factor', None)
            # single_mode = self.request.POST.get('single_mode', 0) and self._model.SINGLE_MODE
            # separate_ref_mode = self.request.POST.get('separate_ref_mode', 0) and self._model.SEPARETE_REF_MODE
            differences = self.request.POST.getlist("objects", [])

            # diff_mode = single_mode + separate_ref_mode
            #
            q_differences = PaycheckDifference.objects.filter(
                pk__in=differences
            ).order_by("employee")
            errors = []
            for pd in q_differences:
                try:
                    with transaction.atomic():
                        pd.apply(payroll, title)
                except Exception as e:
                    errors.append(str(e))

            rst["success"] = (not errors and True) or False
            rst["message"] = "<br />".join(errors) if errors else ""

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def ignore(self, args=[]):
        rst = {"success": False, "message": "Não foi executado nada ainda."}

        q_entries = Entry.objects.filter(
            pk__in=self.request.POST.getlist("objects")
        ).order_by("servidor", "evento", "folha")

        if not q_entries.exists():
            rst["message"] = "Nenhuma diferença de lançamento para ser ignorada!"
        else:
            title = self.request.POST.get("title", "")

            payroll = q_entries.first().contracheque.folha
            errors = self._model.create_differences(
                payroll, entries=q_entries, title=title, status=6
            )

            rst["success"] = (not errors and True) or False
            rst["message"] = "<br />".join(errors) if errors else ""

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def waiting(self, args=[]):
        rst = {"success": False, "message": "Não foi executado nada ainda."}

        q_entries = Entry.objects.filter(
            pk__in=self.request.POST.getlist("objects")
        ).order_by("servidor", "evento", "folha")

        if not q_entries.exists():
            rst["message"] = "Nenhuma diferença de lançamento para ser adiada!"
        else:
            title = self.request.POST.get("title", "")

            payroll = q_entries.first().contracheque.folha
            errors = self._model.create_differences(
                payroll, entries=q_entries, title=title, status=7
            )

            rst["success"] = (not errors and True) or False
            rst["message"] = "<br />".join(errors) if errors else ""

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_icons(self, instance):
        obj = []
        obj_status = {
            "iconCls": "icon-core icon-core-blank",
            "title": instance.get_status_display(),
        }
        # 1 ABERTO, 2 PAGANDO, 3 PARCIALMENTE PAGO, 4 PAGO
        if instance.status == 1:
            obj_status.update({"iconCls": "icon-fopag icon-exclamation-red"})
        elif instance.status == 2:
            obj_status.update({"iconCls": "icon-fopag icon-status-away"})
        elif instance.status == 3:
            obj_status.update({"iconCls": "icon-fopag icon-status-busy"})
        elif instance.status in [4, 5]:
            obj_status.update({"iconCls": "icon-fopag icon-status"})
        elif instance.status == 6:
            obj_status.update({"iconCls": "icon-fopag icon-status-offline"})
        elif instance.status == 7:
            obj_status.update({"iconCls": "icon-fopag icon-clock-select"})
        else:
            obj_status.update({"iconCls": "icon-fopag icon-attention"})
        obj.append(obj_status)

        obj_dif_automated = {"iconCls": "icon-core icon-core-blank", "title": ""}
        if not instance.source_differences:
            obj_dif_automated.update(
                {
                    "iconCls": "icon-fopag icon-compile-warning",
                    "title": "Diferença manual",
                }
            )
        obj.append(obj_dif_automated)

        return obj

    def model_to_dict(self, instance):
        params = super(GFPPayCheckDifference, self).model_to_dict(instance)

        params.update(
            icons=self.get_icons(instance),
            # employer_contribution_to_pay=instance.payable['employer_contribution'],
            # value_to_pay=instance.payable['value'],
            genre_event=(
                instance.event.genre_event.pk if instance.event.genre_event else None
            ),
        )

        return params


class GFPPayCheckDifferenceItem(RestfulDRY):

    _model = PaycheckDifferenceItem

    force_orm_single = True

    def model_to_dict(self, instance):
        params = super(GFPPayCheckDifferenceItem, self).model_to_dict(instance)
        payroll = instance.entry_difference.contracheque.folha
        params.update(
            event_unicode=str(instance.entry_difference.evento),
            event=instance.entry_difference.evento.pk,
            paycheck=instance.entry_difference.contracheque.pk,
            paycheck_unicode=str(instance.entry_difference.contracheque),
            reference="%02d/%04d - %s"
            % (payroll.periodo.mes, payroll.periodo.ano, payroll.tipo_folha),
        )

        return params


class GFPPaycheckDifferenceConfig(RestfulDRY):

    _model = PaycheckDifferenceConfig


class GFPPayrollDifferencePayroll(GFPPayroll):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.paycheckdifference.difference_payroll.difference.PayrollManage")'
        )

    def get_query(self):
        query = super(GFPPayrollDifferencePayroll, self).get_query()
        periodo_id = self.request.GET.get("periodo_id")
        if not periodo_id:
            return query.filter(Q(status__in=[1, 2, 3]))
        folhas = PeriodPayroll.objects.filter(pk=periodo_id).values_list(
            "folha", flat=True
        )
        return query.filter(Q(status__in=[1, 2]) | Q(pk__in=folhas))

    def do_put(self, pk=None):
        rst = {
            "success": True,
            "message": "",
        }

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst["success"] = False
            rst["message"] = f"Você não tem permissão para aplicar a diferença."
        else:
            difference_ids = self.request.PUT.getlist("difference_ids")

            if difference_ids[0] == "all":
                period_id = self.request.PUT.get("period_id")
                difference_ids = [
                    diff.id
                    for diff in DifferencePayroll.objects.filter(
                        status="AVAL", period_id=period_id
                    )
                ]

            for diff_id in difference_ids:
                diff_payroll = DifferencePayroll.objects.get(pk=diff_id)

                Task.start(
                    applicate_difference_task,
                    description=f"Aplicando diferença de folha: {diff_payroll}",
                    user=self.request.user.id,
                    difference_id=diff_payroll.pk,
                    payroll_id=self.request.PUT["folha"],
                )

                rst["message"] = f"Iniciando aplicação de diferença: {diff_payroll}."

        return rst


class GFPPeriodPayroll(RestfulDRY):

    _model = PeriodPayroll

    @login_required("JSON")
    def json(self, args=[]):
        params = {"folhas": self.get_folha_choices()}
        self.response["content-type"] = "text/javascript"
        self.response.write(
            f'Ext._create("rh.gfp.paycheckdifference.difference_payroll.Manage", {params})'
        )

    def model_to_dict(self, instance):
        params = super(GFPPeriodPayroll, self).model_to_dict(instance)
        if instance.folha:
            params.update(
                {
                    "period": f"{instance.folha.periodo.mes}/{instance.folha.periodo.ano} - {instance.folha.tipo_folha.titulo}"
                }
            )
        else:
            params.update({"period": instance.__str__()})
        return params

    def get_folha_choices(self):
        queryset = Payroll.objects.filter(
            status=3, periodo__ano__gte=2022, folha_period_payrolls__isnull=True
        )
        concat = Concat(
            "periodo__mes",
            Value("/"),
            "periodo__ano",
            Value(" - "),
            "tipo_folha__titulo",
            output_field=CharField(),
        )
        queryset = list(queryset.annotate(label=concat).values("pk", "label"))
        params = [[payroll.get("pk"), payroll.get("label")] for payroll in queryset]
        return params

    @login_required("JSON")
    def calculate_period(self, *args):
        obj = {
            "success": True,
            "message": "",
        }
        period = PeriodPayroll.objects.get(pk=self.request.POST.get("period_id"))
        period.calculate_last_date = datetime.now()
        period.save()

        Task.start(
            calculate_period_task,
            description=f"Cálculo de Diferença de folha do período: {period}",
            user=self.request.user.id,
            period_id=period.pk,
        )
        if period.folha:
            obj["message"] = (
                f"Iniciando cálculo do período: {period.folha.periodo.mes}/{period.folha.periodo.ano}"
            )
        else:
            obj["message"] = f"Iniciando cálculo do período: {period}"
        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def calculate_selected_periods(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        for period in PeriodPayroll.objects.filter(
            pk__in=self.request.POST.getlist("periods_ids")
        ):
            period.calculate_last_date = datetime.now()
            period.save()

            Task.start(
                calculate_period_task,
                description=f"Cálculo de Diferença de folha do período: {period}",
                user=self.request.user.id,
                period_id=period.pk,
            )

        obj["message"] = f"Iniciando cálculo dos períodos selecionados"
        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def calculate_all_periods(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        qtd_max_calc_period = Choice.objects.filter(
            app_label="gfp", name="CALC_RANGE_PERIOD_PAYROLL_DIFF", active=True
        )

        initial_period_config = Choice.objects.filter(
            app_label="gfp", name="INITIAL_PERIOD_PAYROLL_DIFF", active=True
        )

        if qtd_max_calc_period and initial_period_config:
            qtd_limit = qtd_max_calc_period.first().value
            date_sub = date.today() - relativedelta(months=qtd_limit)
            initial_year = date_sub.year
            initial_month = date_sub.month
            year_month_date_sub = int(f"{initial_year}{initial_month}")

            config_year = initial_period_config.first().cvalue
            config_month = initial_period_config.first().value
            year_month_config = int(f"{config_year}{config_month}")

            if year_month_date_sub < year_month_config:
                initial_year = config_year
                initial_month = config_month
        else:
            qtd_limit = 6
            date_sub = date.today() - relativedelta(months=qtd_limit)
            initial_year = date_sub.year
            initial_month = date_sub.month

            year_month_date_sub = int(f"{initial_year}{initial_month}")
            if year_month_date_sub < 20221:
                initial_year = 2022
                initial_month = 1

        periods = PeriodPayroll.objects.filter(
            Q(year__gte=initial_year) | Q(folha__periodo__ano__gte=initial_year),
            Q(month__gte=initial_month) | Q(folha__periodo__mes__gte=initial_month),
        )[:qtd_limit]
        for period in periods:
            period.calculate_last_date = datetime.now()
            period.save()

            Task.start(
                calculate_period_task,
                description=f"Cálculo de Diferença de folha do período: {period}",
                user=self.request.user.id,
                period_id=period.pk,
            )

        qtd_periods = periods.count()
        last_period = periods[len(periods) - 1]
        if last_period.folha:
            period = f"{last_period.folha.periodo.mes}/{last_period.folha.periodo.ano}"
        else:
            period = last_period
        obj["message"] = (
            f"Iniciando cálculos de {qtd_periods} períodos, a partide de {period}"
        )
        self.response.write(json_engine.encode(obj))


class GFPDifferencePayroll(RestfulDRY):

    _model = DifferencePayroll

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.paycheckdifference.difference_payroll.difference.Manage")'
        )

    def get_status_icon(self, instance):
        icons_status = {
            "AVAL": "icon-fopag icon-status-away",
            "APLI": "icon-fopag icon-status",
            "IGNO": "icon-fopag icon-status-busy",
        }

        return icons_status[instance.status]

    def get_type_diff_icon(self, instance):
        icon_type_diff = {
            "DESC": "icon-core icon-core-minus",
            "PROV": "icon-core icon-core-add",
        }

        return icon_type_diff[instance.type_diff]

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        icons.append(
            {
                "iconCls": self.get_status_icon(instance),
                "title": instance.get_status_display(),
                "alt": instance.get_status_display(),
            }
        )

        icons.append(
            {
                "iconCls": self.get_type_diff_icon(instance),
                "title": f"Tipo de diferença: {instance.get_type_diff_display()}",
                "alt": f"Tipo de diferença: {instance.get_type_diff_display()}",
            }
        )

        if instance.from_others_diffs:
            icons.append(
                {
                    "iconCls": "icon-fopag icon-node-select",
                    "title": "Vinculado à outras diferenças",
                    "alt": "Vinculado à outras diferenças",
                }
            )

        return icons

    def model_to_dict(self, instance):
        params = super(GFPDifferencePayroll, self).model_to_dict(instance)
        period_unicode = (
            f"{instance.period.folha.periodo.mes}/{instance.period.folha.periodo.ano}"
            if instance.period.folha
            else instance.periodo
        )
        params.update(
            {
                "period_unicode": period_unicode,
                "payroll_event": instance.payroll_event,
                "payroll_applied": instance.payroll_applied,
                "qtd_normalize": instance.qtd_normalize,
                "qtd_diff_normalize": instance.qtd_diff_normalize,
                "event_info": instance.event_info,
                "icons": self.get_icons(instance),
            }
        )

        return params

    def get_query(self):
        period_id = None
        getting_params = self.get_params().get("filter", "[]")
        params_list = json.loads(getting_params)
        q = []
        if params_list != []:
            try:
                period_id = [
                    x["value"] for x in params_list if x["property"] == "period"
                ][0]
            except:
                period_id = None

            if period_id != None:
                q = DifferencePayroll.objects.filter(
                    period_id=period_id,
                )

        return q

    def check_if_open_payroll_exists(self, period):
        folhas = list(
            Payroll.objects.filter(
                periodo__mes__gt=period.folha.periodo.mes,
                periodo__ano__gte=period.folha.periodo.ano,
                status__in=[1, 2],
            ).values_list("id", flat=True)
        )
        folhas.append(period.folha.id)
        return len(folhas) > 0

    def get_event_to_apply(self, genre_number, specie_number):
        q = Event.objects.filter(
            genre_event__genre_number=genre_number,
            specie_event__specie_number=specie_number,
        )

        return q.first() if q.exists() else None

    @login_required("JSON")
    def applicate_difference_validate(self, *args):
        success = True
        message = ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = f"Você não tem permissão para aplicar a diferença"
        else:
            difference_ids = self.request.POST.getlist("difference_ids")

            for diff_id in difference_ids:
                diff_payroll = DifferencePayroll.objects.get(pk=diff_id)

                if diff_payroll.status != "AVAL":
                    success = False
                    message = f"""
                    O status da diferença escolhida está '{diff_payroll.get_status_display()}'.
                    Só é permitido aplicar diferenças com status 'Avaliar'.
                    """
                elif self.check_if_open_payroll_exists(diff_payroll.period) is False:
                    success = False
                    message = f"""
                    Só é permitido aplicar diferenças em Folhas 'Abertas'.
                    Não existe folhas 'Abertas' para períodos maiores que {diff_payroll.period.month}/{diff_payroll.period.year}.
                    """
                else:
                    genre_number = diff_payroll.event.genre_event.genre_number
                    specie_number = "01" if diff_payroll.type_diff == "PROV" else "02"
                    event_to_apply = self.get_event_to_apply(
                        genre_number, specie_number
                    )

                    if event_to_apply is None:
                        success = False
                        message = f"""
                        Não foi possível encontrar a verba para aplicação de número: {genre_number}{specie_number}
                        """

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))

    @login_required("JSON")
    def applicate_all_difference_validate(self, *args):
        success = True
        message = ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = f"Você não tem permissão para aplicar a diferença"
        else:
            period_id = self.request.POST.get("period_id")
            for diff_payroll in DifferencePayroll.objects.filter(
                status="AVAL", period_id=period_id
            ):
                if self.check_if_open_payroll_exists(diff_payroll.period) is False:
                    success = False
                    message = f"""
                    Só é permitido aplicar diferenças em Folhas 'Abertas'.
                    Não existe folhas 'Abertas' para períodos maiores que {diff_payroll.period.folha.periodo.mes}/{diff_payroll.period.folha.periodo.ano}.
                    """
                else:
                    genre_number = diff_payroll.event.genre_event.genre_number
                    specie_number = "01" if diff_payroll.type_diff == "PROV" else "02"
                    event_to_apply = self.get_event_to_apply(
                        genre_number, specie_number
                    )

                    if event_to_apply is None:
                        success = False
                        message = f"""
                        Não foi possível encontrar a verba para aplicação de número: {genre_number}{specie_number}.
                        Diferença relacionada: {diff_payroll}
                        """

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))

    @login_required("JSON")
    def ignorate_difference(self, *args):
        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = f"Você não tem permissão para ignorar a diferença"
        else:
            difference_id = self.request.POST.get("difference_id")
            diff_payroll = DifferencePayroll.objects.get(pk=difference_id)

            if diff_payroll.status != "AVAL":
                success = False
                message = f"""
                O status da diferença escolhida está '{diff_payroll.get_status_display()}'.
                Só é permitido ignorar diferenças com status 'Avaliar'.
                """
            else:
                try:
                    diff_payroll.status = "IGNO"
                    diff_payroll.save()

                    success = True
                    message = "Diferença ignorada com sucesso."
                except:
                    success = False
                    message = "Não foi possível ignorar a diferença selecionada"

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))
