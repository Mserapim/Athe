# -*- coding: utf-8 -*-
import datetime
from celery import Celery
import os

from django.db.models import Count

from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, get_json_engine, getLogger
from engine.mq.models import Task
from rh.dayoff.const import (
    PAYMENT_APPROVED,
    PAYMENT_CHECKED,
    PAYMENT_DENNIED,
    PAYMENT_WAITING,
)
from rh.dayoff.models import UsufructPaymentControl
from rh.gfp.tasks_payment_vacation import (
    start_calculate_usufruct_payment,
    start_implement_usufruct_payment,
)


json = get_json_engine()

log = getLogger(__name__)

app = Celery("gratificaions_manager")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


class GFPPaymentVacation(RestfulDRY):
    """
    API para tela de gestão de Gratificações e Abonos
    """

    _model = UsufructPaymentControl

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
    )

    def get_query(self):
        return (
            super()
            .get_query()
            .filter(status=PAYMENT_CHECKED)
            .order_by("employee__matricula")
        )

    @login_required("JSON")
    def buscar_lista_anos(self, args=[]):
        obj = {"root": []}

        q_anos = (
            UsufructPaymentControl.objects.filter(usufruct__payment_year__isnull=False)
            .values("usufruct__payment_year")
            .annotate(dcount=Count("usufruct__payment_year"))
            .order_by()
        )
        anos = [
            x["usufruct__payment_year"]
            for x in q_anos
            if len(str(x["usufruct__payment_year"])) == 4
        ]
        anos.sort(reverse=True)
        for ano in anos:
            obj.get("root").append(
                {
                    "pk": ano,
                    "description": ano,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.vacation.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(GFPPaymentVacation, self).model_to_dict(instance)

        _dict_.update({"employee_unicode": f"{instance.employee}"})
        _dict_.update({"checked_by_unicode": f"{instance.checked_by}"})
        _dict_.update({"status_display": instance.usufruct.get_status_display()})
        _dict_.update(
            {
                "checked_at": (
                    instance.checked_at.strftime("%d/%m/%Y")
                    if instance.checked_at
                    else None
                )
            }
        )
        _dict_.update(
            {
                "start_date": (
                    instance.usufruct.start_date.strftime("%d/%m/%Y")
                    if instance.usufruct.start_date
                    else None
                )
            }
        )
        _dict_.update(
            {
                "end_date": (
                    instance.usufruct.end_date.strftime("%d/%m/%Y")
                    if instance.usufruct.end_date
                    else None
                )
            }
        )
        _dict_.update({"activity_unicode": f"{instance.usufruct.activity}"})
        _dict_.update(
            {
                "start_date_acquisition": instance.usufruct.activity.acquisition_period.start_date_acquisition.strftime(
                    "%d/%m/%Y"
                )
            }
        )
        _dict_.update(
            {
                "end_date_acquisition": instance.usufruct.activity.acquisition_period.end_date_acquisition.strftime(
                    "%d/%m/%Y"
                )
            }
        )
        _dict_.update(
            {
                "start_date_fruition": instance.usufruct.activity.acquisition_period.start_date_fruition.strftime(
                    "%d/%m/%Y"
                )
            }
        )
        _dict_.update({"days": instance.usufruct.days})
        _dict_.update({"competence": f"{instance.usufruct.payment_competence}"})
        _dict_.update({"employee_pk": f"{  str(instance.employee.pk) }"})
        _dict_.update(
            {"employee_type": "MEMBRO" if instance.employee.is_member else "SERVIDOR"}
        )
        _dict_.update({"employee_registry": f"{  str(instance.employee.matricula) }"})
        _dict_.update({"origin_of_request": instance.usufruct.origin_of_request})
        _dict_.update({"is_suspension": instance.usufruct.is_suspension})
        _dict_.update({"is_retification": instance.usufruct.is_retification})
        _dict_.update({"activity_label": instance.usufruct.activity_label})
        _dict_.update(
            {
                "competence_paid": (
                    instance.usufruct.competence_paid
                    if instance.usufruct.competence_paid
                    else (
                        f"{instance.usufruct.payment_competence}| {instance.usufruct.payment_installments}(PENDENTE)"
                        if instance.usufruct.payment_month
                        and instance.usufruct.payment_year
                        else ""
                    )
                )
            }
        )
        _dict_.update({"status_conference_payment": instance.get_status_display()})
        _dict_.update({"allows_suspend": instance.usufruct.allows_suspend})
        _dict_.update(
            {
                "group_period": str(
                    instance.usufruct.activity.acquisition_period.group_period
                )
            }
        )

        return _dict_

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = []
        for record in query:
            rst.append(
                {
                    "Matricula": record.employee.matricula,
                    "Servidor": record.employee.pessoa_fisica.nome,
                    "Tipo Servidor": (
                        "MEMBRO" if record.employee.is_member else "SERVIDOR"
                    ),
                    "Situação": record.get_payroll_ctrl_status_display(),
                    "Início do Período Aquisitivo": record.usufruct.activity.acquisition_period.start_date_acquisition.strftime(
                        "%d/%m/%Y"
                    ),
                    "Fim do Período Aquisitivo": record.usufruct.activity.acquisition_period.end_date_acquisition.strftime(
                        "%d/%m/%Y"
                    ),
                    "Dias Programados": record.usufruct.days,
                    "Valor Calculado": record.calculated_value,
                    "Valor Confirmado": record.confirmed_value,
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    def do_put_single(self, pk=None):
        """
        Atualiza uma instância do objeto e atualiza a confirmação de pagamento.
        """
        inst = self.Model.objects.filter(pk=pk).first()
        if not inst.payroll_ctrl_status == PAYMENT_WAITING:
            raise Exception(
                "Somente usufrutos em análise podem ter o valor confirmado alterado manualmente."
            )
        rst = super().do_put_single(pk)
        inst.manual_confirmation_payment = True
        inst.manual_confirmation_by = employee_from_user(get_current_user())
        inst.manual_confirmation_at = datetime.datetime.now().date()
        inst.save()
        return rst

    @login_required("JSON")
    def control_checked(self, *args):
        """
        Função responsável por criar o controle de pagamento de usufrutos
        """
        response = {
            "success": False,
            "message": "A conferência está sendo processada",
        }
        try:
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                response.update(
                    message="Você não tem permissão para conferir %s."
                    % self.Model._meta.object_name
                )
            else:
                today = datetime.datetime.now().date()
                usufruct_payment_controls = UsufructPaymentControl.objects.filter(
                    pk__in=[int(x) for x in self.request.POST.get("ids", 0).split(",")]
                )
                for usufruct_payment_control in usufruct_payment_controls:
                    if not usufruct_payment_control.calculated_value:
                        response.update(
                            {
                                "success": False,
                                "message": "É necessário fazer o cálculo do Abono/Gratificação para torná-lo apto para pagamento.",
                            }
                        )

                    else:
                        usufruct = usufruct_payment_control.usufruct
                        if usufruct:
                            usu_control, created = (
                                UsufructPaymentControl.objects.update_or_create(
                                    employee=usufruct.activity.acquisition_period.employee,
                                    usufruct=usufruct,
                                    defaults={
                                        "type_of_control": 2,
                                        "payroll_ctrl_status": PAYMENT_APPROVED,
                                        "applied_by": employee_from_user(
                                            get_current_user()
                                        ),
                                        "applied_at": today,
                                    },
                                )
                            )
                            if not created and not usu_control.confirmed_value:
                                usu_control.confirmed_value = (
                                    usu_control.calculated_value
                                )
                                usu_control.save()
                        response.update(
                            {
                                "success": True,
                                "message": "A conferência foi realizada com sucesso.",
                            }
                        )
        except Exception as err:
            log.error(err)
            response = {
                "success": False,
                "message": "Ocorreu um erro no processamento, entre em contato com o administrador do sistema.",
            }
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(response))

    @login_required("JSON")
    def control_declined(self, *args):
        """
        Função responsável por criar o controle de declínio de pagamento de usufrutos
        """
        response = {
            "success": False,
            "message": "O declínio de pagamento está sendo processado",
        }

        try:
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                response.update(
                    message="Você não tem permissão para declinar %s."
                    % self.Model._meta.object_name
                )
            else:
                today = datetime.datetime.now().date()
                usufruct_payment_controls = UsufructPaymentControl.objects.filter(
                    pk__in=[int(x) for x in self.request.POST.get("ids", 0).split(",")]
                )
                for usufruct_payment_control in usufruct_payment_controls:
                    if not usufruct_payment_control.calculated_value:
                        response.update(
                            {
                                "success": False,
                                "message": "É necessário fazer o cálculo do Abono/Gratificação para torná-lo inapto para pagamento.",
                            }
                        )

                    else:
                        usufruct = usufruct_payment_control.usufruct
                        if usufruct:
                            UsufructPaymentControl.objects.update_or_create(
                                employee=usufruct.activity.acquisition_period.employee,
                                usufruct=usufruct,
                                defaults={
                                    "type_of_control": 2,
                                    "payroll_ctrl_status": PAYMENT_DENNIED,
                                    "applied_by": employee_from_user(
                                        get_current_user()
                                    ),
                                    "applied_at": today,
                                    "observation": self.request.POST.get(
                                        "observation", None
                                    ),
                                },
                            )
                        response.update(
                            {
                                "success": True,
                                "message": "O declínio foi realizada com sucesso.",
                            }
                        )
        except Exception as err:
            log.error(err)
            response = {
                "success": False,
                "message": "Ocorreu um erro no processamento, entre em contato com o administrador do sistema. ",
            }
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(response))

    def control_calculate(self, *args):
        """
        Função responsável por calcular o valor de pagamento das gratificações e abonos
        """
        response = {
            "success": False,
            "message": "O cálculo de pagamento de abonos e gratificações está sendo processado",
        }

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            response.update(
                message="Você não tem permissão para calcular %s."
                % self.Model._meta.object_name
            )
        else:
            if self.request.POST.get("ids", 0):
                control_usufructs = self.get_query().filter(
                    pk=self.request.POST.get("ids", 0), payroll_ctrl_status=1
                )
            else:
                control_usufructs = self.get_query().filter(payroll_ctrl_status=1)
            if not control_usufructs:
                response["message"] = (
                    "Nenhuma Gratificação/Abono apto a cáculo foi selecionado."
                )
            else:
                Task.start(
                    start_calculate_usufruct_payment,
                    description="Implementação de Abonos e Férias",
                    user_pk=get_current_user().pk,
                    control_usufructs=[
                        x for x in control_usufructs.values_list("pk", flat=True)
                    ],
                )

                response["success"] = True

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(response))

    def control_implement(self, *args):
        """
        Função responsável por implementar o valor de pagamento das gratificações e abonos
        """
        response = {
            "success": False,
            "message": "A implementação em folha dos abonos e gratificações está sendo processada",
        }

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            response.update(
                message="Você não tem permissão para implantar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                if self.request.POST.get("ids", 0):
                    numeros_lista = [
                        int(num)
                        for num in self.request.POST.getlist("ids", 0)[0].split(",")
                    ]
                    control_usufructs = self.get_query().filter(
                        pk__in=numeros_lista, payroll_ctrl_status=3
                    )
                else:
                    raise Exception("Nenhum usufruto/abono selecionado.")
                if not self.request.POST.get("payroll", None):
                    response["message"] = (
                        "Selecione a folha que deseja implementar os abonos/gratificações"
                    )
                elif not self.request.POST.get(
                    "month", None
                ) or not self.request.POST.get("year", None):
                    response["message"] = "Ocorreu um erro com os filtros do período."
                else:
                    Task.start(
                        start_implement_usufruct_payment,
                        "Implementação de Abonos e Férias",
                        user_pk=get_current_user().pk,
                        control_usufructs=[
                            x for x in control_usufructs.values_list("pk", flat=True)
                        ],
                        payroll_id=self.request.POST.get("payroll", None),
                    )
                response["success"] = True
                response["message"] = (
                    "A implementação em folha dos abonos e gratificações foi finalizada com sucesso."
                )
            except Exception as e:
                log.error(f"Error {e}")
                response["message"] = str(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(response))
