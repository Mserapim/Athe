# -*- coding: utf-8 -*-
import json
from datetime import datetime

from django.db.models.expressions import F
from django.db.models import Q

from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger, employee_from_user
from rh.gfp.models import ContraCheque as Paycheck
from rh.gfp.models import FolhaTipo
from rh.models import Servidor as Employee
from standard.models import Choice


log = getLogger(__name__)


class PVFPayCheckReport(RestfulDRY):

    _model = Paycheck

    key_all_kinds = 999999
    key_none_kind = 999998

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.reports.PayCheckManage")')

    def get_payroll_types(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            employee = employee_from_user(get_current_user())
            month = self.request.POST.get("month")
            year = self.request.POST.get("year")

            paychecks = Paycheck.objects.filter(
                servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf,
                folha__available_pvf=True,
                folha__periodo__mes=month,
                folha__periodo__ano=year,
            )

            payrolltypes = FolhaTipo.objects.filter(
                ativo=True, folhas__paychecks__in=[x.pk for x in paychecks]
            ).distinct()

            # payrolltypes = FolhaTipo.objects.filter(ativo=True)
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(payrolltypes),
                collection=[
                    {"pk": payrolltype.pk, "description": str(payrolltype)}
                    for payrolltype in payrolltypes
                ],
            )
            if len(payrolltypes) == 0:
                obj["collection"].append(
                    {
                        "pk": self.key_none_kind,
                        "description": "Holerite não disponível para o filtro selecionado",
                    }
                )
            else:
                obj["collection"].append(
                    {"pk": self.key_all_kinds, "description": "TODOS"}
                )
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_year(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            years = []
            start_year = Choice.objects.get(
                app_label="pvf", name="HOLERITE_START_YEAR"
            ).value
            data_year = datetime.today().year
            while data_year >= start_year:
                years.append(data_year)
                data_year = data_year - 1

            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(years),
                collection=[{"pk": year, "description": str(year)} for year in years],
            )

        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    @login_required("JSON")
    def paycheck_list(self, args=[]):
        json = get_json_engine()
        obj = {"success": True, "message": ""}
        try:
            employee = employee_from_user(get_current_user())
            month = self.request.POST.get("month")
            year = self.request.POST.get("year")
            type = self.request.POST.get("type")

            if type == str(self.key_all_kinds):
                list_month = [month]
                if int(month) == 12:
                    list_month.append(13)
                types = FolhaTipo.objects.all()
                list_types = [x.pk for x in types]
                query_cc = Paycheck.objects.filter(
                    servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf,
                    folha__periodo__mes__in=list_month,
                    folha__periodo__ano=year,
                    folha__tipo_folha__pk__in=list_types,
                )

            else:
                query_cc = Paycheck.objects.filter(
                    servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf,
                    folha__periodo__mes=month,
                    folha__periodo__ano=year,
                    folha__tipo_folha__pk=type,
                )

            self.check_available_message(month, query_cc, obj)
            list_paycheck = ",".join(
                [str(cc.pk) for cc in query_cc.filter(folha__available_pvf=True)]
            )
            obj.update(list_paycheck=list_paycheck)

        except Exception as e:
            self.log.exception(e)
            obj["message"] = e
            obj["success"] = False
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def check_available_message(self, month, query_cc, obj):
        check_available = self.check_available(query_cc)
        if not query_cc:
            obj["message"] = (
                "Não há dados para serem exibidos para o filtro selecionado."
            )
            obj["success"] = False
        else:
            if not check_available and int(month) >= datetime.today().month:
                obj["message"] = "Dados não disponíveis."
                obj["success"] = False
            elif not check_available and int(month) < datetime.today().month:
                obj["message"] = "Dados não disponíveis, consultar folha de pagamento."
                obj["success"] = False

        return obj

    def check_available(self, paychecks):
        for check in paychecks:
            if check.folha.available_pvf:
                return True

        return False


class GPPayCheckReport(PVFPayCheckReport):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.PayCheckManage")')

    @login_required("JSON")
    def paycheck_list(self, args=[]):
        json = get_json_engine()
        obj = {"success": True, "message": ""}
        try:
            employee_received = Employee.objects.filter(
                pk=self.request.POST.get("employee")
            ).first()
            employee = (
                employee_received
                if employee_received
                else employee_from_user(get_current_user())
            )
            start_competence = self.request.POST.get("start_competence")
            end_competence = self.request.POST.get("end_competence")

            if start_competence:
                try:
                    start_month, start_year = start_competence.split("/")

                except Exception as e:
                    obj.update(message=str(e))
                    obj.update(status="error")

            if end_competence:
                try:
                    end_month, end_year = end_competence.split("/")
                except Exception as e:
                    obj.update(message=str(e))
                    obj.update(status="error")
            if not int(start_month) in [x for x in range(1, 13)]:
                obj["message"] = "Informe um mês válido (competência inicial)"
                obj["success"] = False

            if not len(start_year) == 4:
                obj["message"] = "Informe um ano válido (competência inicial)"
                obj["success"] = False

            if not int(end_month) in [x for x in range(1, 13)]:
                obj["message"] = "Informe um mês válido (competência final)"
                obj["success"] = False

            if not len(end_year) == 4:
                obj["message"] = "Informe um ano válido (competência final)"
                obj["success"] = False

            if not obj["success"] == False:
                list_types = [x.pk for x in FolhaTipo.objects.all()]
                query_cc = Paycheck.objects.filter(
                    (
                        Q(
                            folha__periodo__mes__gte=start_month,
                            folha__periodo__ano=start_year,
                        )
                        | Q(folha__periodo__ano__gt=start_year)
                    )
                    & (
                        Q(
                            folha__periodo__mes__lte=end_month,
                            folha__periodo__ano=end_year,
                        )
                        | Q(folha__periodo__ano__lt=end_year)
                    ),
                    servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf,
                    folha__tipo_folha__pk__in=list_types,
                )

                if not query_cc:
                    obj["message"] = (
                        "Não foram localizados contracheques para o período"
                    )
                    obj["success"] = False
                list_paycheck = ",".join([str(cc.pk) for cc in query_cc])

                obj.update(list_paycheck=list_paycheck)

        except Exception as e:
            self.log.exception(e)
            obj["message"] = e
            obj["success"] = False
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
