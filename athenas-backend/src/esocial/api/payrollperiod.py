# -*- coding: utf-8 -*-
from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from esocial.models import PayrollPeriod
from esocial.utils import esocial_environment
from rh.gfp.models import Periodo


log = getLogger(__name__)


class ESOCIALPayrollPeriod(RestfulDRY):

    _model = PayrollPeriod

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

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
        self.response.write('Ext._create("esocial.payrollperiod.Manage")')

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        icons.append(
            {
                "iconCls": (
                    "icon-esocial icon-pendency"
                    if instance.pendency_cache
                    else "icon-esocial icon-success"
                ),
                "alt": (
                    "Com pendências" if instance.pendency_cache else "Sem pendências"
                ),
            }
        )
        icons.append(
            {
                "iconCls": (
                    "icon-esocial icon-payroll-sent"
                    if instance.sent
                    else "icon-esocial icon-payroll-waiting-send"
                ),
                "alt": "Enviado" if instance.sent else "Não enviado",
            }
        )
        icons.append(
            {
                "iconCls": (
                    "icon-esocial icon-closed"
                    if instance.closed
                    else "icon-esocial icon-open"
                ),
                "alt": "Fechado" if instance.closed else "Aberto",
            }
        )

        return icons

    @login_required(type="JSON")
    def analisys(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        all_periods = self.request.POST.get("all_periods", False)
        payroll_period = [int(pk) for pk in self.request.POST.getlist("payroll_period")]

        try:
            if all_periods:
                self.Model.analysis_all_period_call_task()
            elif payroll_period:
                periods = []
                for pp in self.Model.objects.filter(pk__in=payroll_period):
                    period = Periodo.objects.filter(mes=pp.month, ano=pp.year).last()
                    if period:
                        periods.append(period.pk)

                self.Model.analysis_all_period_call_task(periods=periods)
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message="Tarefa de Análise de Períodos iniciada!")
        self.renderer(rst)


class ESOCIALPayrollPeriodManage(ESOCIALPayrollPeriod):

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

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
            "Ext._create('esocial.payrollperiod.PayrollPeriodManage', {environment: '%s'})"
            % esocial_environment()
        )
