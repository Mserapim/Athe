# -*- coding: utf-8 -*-
import json as js
import datetime
from django.db.models import Count

from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import Restful, RestfulDRY
from contrib.utils import employee_from_user, get_json_engine, getLogger, DateUtils
from rh.dayoff.models import Activity, Usufruct, UsufructPaymentControl, UsufructSell
from rh.dayoff.const import (
    PAYMENT_CHECKED,
    PAYMENT_DECLINED,
    REGULAR_VACATIONS,
    INDIVIDUAL_VACATION,
    USU_AUTORIZED_CI,
    USU_CANCELED,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_INTERRUPTED,
    USU_SOLD,
    USU_SUSPENDED,
)
from standard.models import Choice
from contrib.daterange import NewDateRange
from django.db.models import Q


json = get_json_engine()

log = getLogger(__name__)


class DAYOFFPaymentVacation(RestfulDRY):
    """
    API para tela de conferência de pagamentos de férias
    """

    _model = Usufruct

    full_text_index = (
        "activity__acquisition_period__employee__pessoa_fisica__nome__icontains",
        "activity__acquisition_period__employee__matricula__icontains",
    )

    def get_query(self):
        """
        Filtragem de query para que retorne os usufrutos que são passíveis de confirmação
        """
        query = super(DAYOFFPaymentVacation, self).get_query()
        return query.filter(
            activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                REGULAR_VACATIONS,
                INDIVIDUAL_VACATION,
            ],
            status__in=[
                USU_HOMOLOGATED,
                USU_ENJOYING,
                USU_ENJOYED,
                USU_SUSPENDED,
                USU_INTERRUPTED,
                USU_AUTORIZED_CI,
            ],
            activity__acquisition_period__payments__isnull=True,
        ).order_by("start_date")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.payment_vacation.vacation.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(DAYOFFPaymentVacation, self).model_to_dict(instance)

        _dict_.update({"icons": instance.icons})
        _dict_.update({"employee_unicode": f"{instance.employee}"})
        _dict_.update({"status_display": instance.get_status_display()})
        _dict_.update(
            {
                "start_date": (
                    instance.start_date.strftime("%d/%m/%Y")
                    if instance.start_date
                    else None
                )
            }
        )
        _dict_.update(
            {
                "end_date": (
                    instance.end_date.strftime("%d/%m/%Y")
                    if instance.end_date
                    else None
                )
            }
        )
        _dict_.update({"activity_unicode": f"{instance.activity}"})
        _dict_.update({"days": instance.days})
        _dict_.update({"competence": f"{instance.payment_competence}"})
        _dict_.update({"employee_pk": f"{  str(instance.employee.pk) }"})
        _dict_.update(
            {"employee_type": "MEMBRO" if instance.employee.is_member else "SERVIDOR"}
        )
        _dict_.update({"employee_registry": f"{  str(instance.employee.matricula) }"})
        _dict_.update({"origin_of_request": instance.origin_of_request})
        _dict_.update({"is_suspension": instance.is_suspension})
        _dict_.update({"is_retification": instance.is_retification})
        _dict_.update({"activity_label": instance.activity_label})

        _dict_.update({"competence_paid": instance.competence_paid_str})

        status_conf_payment = (
            instance.ctrl_payments.first().get_status_display()
            if instance.ctrl_payments.exists()
            else "Sem análise"
        )
        _dict_.update({"status_conference_payment": status_conf_payment})

        _dict_.update({"allows_suspend": instance.allows_suspend})
        _dict_.update(
            {"group_period": str(instance.activity.acquisition_period.group_period)}
        )

        return _dict_

    def validate_reference(self):
        competence = self.request.POST.get("competence", None)
        if "/" not in competence:
            raise Exception(
                "A competência deve possuir o formato MM/AAAA, sendo o 'mês'+'/'+'ano'. Ex.: 01/2022."
            )
        month, year = competence.split("/")
        if len(str(month)) != 2 or len(str(year)) != 4:
            raise Exception(
                "A competência deve possuir o formato MM/AAAA, sendo dois dígitos para mês e quatro dígitos para o ano. Ex.: 01/2022."
            )

    def do_full_text_filter(self, query):
        """Realiza pesquisa com valor de keyword do Request nos campos adicionados em full_text_index.

        :param query: QuerySet a ser aplicada o filtro com keyword.

        :returns: QuerySet com filtro aplicado.
        """

        if self.full_text_index:
            qf = None

            value_index = self.request.GET.get("keyword") or self.request.POST.get(
                "keyword"
            )

            for index in self.full_text_index:
                q = Q(**{index: value_index})
                qf = q if qf is None else Q(qf | q)

            query = query.filter(qf)

        return query

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
                qtd_usufrutos = 0
                qtd_usufrutos_invalidos = 0

                usufruct_ids = self.request.POST.getlist("ids", [])

                if not usufruct_ids:
                    query_usufrutos = self.get_query().filter()
                    if "filter" in self.request.POST:
                        query_usufrutos = self.do_filter(query_usufrutos)
                    if "keyword" in self.request.POST:
                        query_usufrutos = self.do_full_text_filter(query_usufrutos)
                else:
                    query_usufrutos = self.get_query().filter(pk__in=usufruct_ids)

                for usufruct in query_usufrutos:
                    qtd_usufrutos += 1
                    if usufruct.payment_year is None or usufruct.payment_month is None:
                        qtd_usufrutos_invalidos += 1

                    else:
                        UsufructPaymentControl.objects.update_or_create(
                            employee=usufruct.activity.acquisition_period.employee,
                            usufruct=usufruct,
                            type_of_control=1,
                            defaults={
                                "status": PAYMENT_CHECKED,
                                "checked_by": employee_from_user(get_current_user()),
                            },
                        )

                if (qtd_usufrutos == 1 and qtd_usufrutos_invalidos > 0) or (
                    qtd_usufrutos > 1 and qtd_usufrutos_invalidos == qtd_usufrutos
                ):
                    response.update(
                        {
                            "success": False,
                            "message": "É necessário preencher a competência de pagamento.",
                        }
                    )
                elif qtd_usufrutos > 1 and qtd_usufrutos_invalidos > 0:
                    response.update(
                        {
                            "success": True,
                            "message": "A conferência foi realizada com sucesso. Porém somente os registros com a competência de pagamento foram processados.",
                        }
                    )
                else:
                    response.update(
                        {
                            "success": True,
                            "message": "A conferência foi realizada com sucesso.",
                        }
                    )
        except Exception as err:
            log.error(err)
            msg = (
                str(err)
                if can is False
                else "Ocorreu um erro no processamento, entre em contato com o administrador do sistema."
            )
            response = {"success": False, "message": msg}
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

        if not self.request.POST.get("competence", None) or not self.request.POST.get(
            "qtd_parcel", None
        ):
            response.update(
                {
                    "message": "Informe a Competência de Pagamento e o Número de Parcelas",
                }
            )

        else:
            try:
                self.validate_reference()
            except Exception as err:
                response.update(
                    {
                        "message": err,
                    }
                )

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
                    month, year = self.request.POST.get("competence", None).split("/")
                    ano_atual = datetime.datetime.now().year
                    mes_valido = month.isdigit() and 1 <= int(month) <= 12
                    ano_valido = (
                        year.isdigit() and ano_atual - 1 <= int(year) <= ano_atual + 1
                    )

                    if mes_valido is False:
                        response.update(
                            {
                                "success": False,
                                "message": "Mês inválido.",
                            }
                        )
                    elif ano_valido is False:
                        response.update(
                            {
                                "success": False,
                                "message": "Ano inválido.",
                            }
                        )
                    else:
                        usufruct_ids = self.request.POST.getlist("ids", [])

                        if not usufruct_ids:
                            query_usufrutos = self.get_query().filter()
                            if "filter" in self.request.POST:
                                query_usufrutos = self.do_filter(query_usufrutos)
                            if "keyword" in self.request.POST:
                                query_usufrutos = self.do_full_text_filter(
                                    query_usufrutos
                                )
                        else:
                            query_usufrutos = self.get_query().filter(
                                pk__in=usufruct_ids
                            )

                        for usufruct in query_usufrutos:
                            UsufructPaymentControl.objects.update_or_create(
                                employee=usufruct.activity.acquisition_period.employee,
                                usufruct=usufruct,
                                type_of_control=1,
                                defaults={
                                    "status": PAYMENT_DECLINED,
                                    "checked_by": employee_from_user(
                                        get_current_user()
                                    ),
                                    "observation": self.request.POST.get(
                                        "observation", None
                                    ),
                                },
                            )
                            usufruct.payment_month = month
                            usufruct.payment_year = year
                            usufruct.payment_installments = self.request.POST.get(
                                "qtd_parcel", None
                            )
                            usufruct.save_base()

                        response.update(
                            {
                                "success": True,
                                "message": "O declínio foi realizada com sucesso.",
                            }
                        )

            except Exception as err:
                log.error(err)
                msg = (
                    str(err)
                    if can is False
                    else "Competência de pagamento deve ser alterada através do gerenciador admin."
                )
                response = {"success": False, "message": msg}
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(response))

    def export(self, args=[]):
        query = self.get_query().filter()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if self.request.GET.get("keyword"):
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        # payroll = None

        rst = []
        for record in query:
            rst.append(
                {
                    "Status": (
                        record.ctrl_payments.first().get_status_display()
                        if record.ctrl_payments.first()
                        else "Sem análise"
                    ),
                    "Servidor": record.employee,
                    "Situação": record.get_status_display(),
                    "Tipo Servidor": (
                        "MEMBRO" if record.employee.is_member else "SERVIDOR"
                    ),
                    "Atividade": f"{record.activity}",
                    "Status da Atividade": record.activity.get_status_display(),
                    "Grupo": str(record.activity.acquisition_period.group_period),
                    "Início das Férias": (
                        record.start_date.strftime("%d/%m/%Y")
                        if record.start_date
                        else None
                    ),
                    "Final das Férias": (
                        record.end_date.strftime("%d/%m/%Y")
                        if record.end_date
                        else None
                    ),
                    "Dias": record.days,
                    "Competência de Pagamento": (
                        record.competence_paid
                        if record.competence_paid
                        else (
                            f"{record.payment_competence}| {record.payment_installments}(PENDENTE)"
                            if record.payment_month and record.payment_year
                            else ""
                        )
                    ),
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    @login_required("JSON")
    def buscar_lista_anos(self, args=[]):
        obj = {"root": []}

        q_anos = (
            Usufruct.objects.filter(
                payment_year__isnull=False,
                activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                    REGULAR_VACATIONS,
                    INDIVIDUAL_VACATION,
                ],
            )
            .exclude(status=USU_CANCELED)
            .values("payment_year")
            .annotate(dcount=Count("payment_year"))
            .order_by()
        )
        anos = [
            str(x["payment_year"]) for x in q_anos if len(str(x["payment_year"])) == 4
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


class DAYOFFSellVacation(DAYOFFPaymentVacation):
    """
    API para tela de conferência de pagamentos de venda de férias
    """

    full_text_index = (
        "activity__acquisition_period__employee__pessoa_fisica__nome__icontains",
        "activity__acquisition_period__employee__matricula__icontains",
    )

    def json(self, args=[]):
        vacation_deadline = (
            Choice.objects.filter(app_label="rh", name="VACATION_DEADLINE")
            .first()
            .value
        )
        self.response["content-type"] = "text/javascript"
        self.response.write(
            """
            Ext._create("rh.dayoff.mpmt.payment_vacation.sell_vacation.Manage",
            {
                vacation_deadline: "%s"
            }
            )"""
            % vacation_deadline
        )

    def get_query(self):
        flist = js.loads(self.get_params().get("filter", "[]"))
        ano = [x["value"] for x in flist if x["property"] == "payment_year"][0]

        try:
            mes = [x["value"] for x in flist if x["property"] == "payment_month"][0]
        except:
            mes = None

        if mes:
            q = Usufruct.objects.filter(
                activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                    REGULAR_VACATIONS,
                    INDIVIDUAL_VACATION,
                ]
            ).filter(payment_year=ano, payment_month=mes)

            ids = [x.activity.pk for x in q]
            query = UsufructSell.objects.filter(
                activity__pk__in=ids, status=USU_SOLD
            ).exclude(status=USU_CANCELED)

        return query.filter(
            Q(activity__acquisition_period__employee__ativo=True)
            | Q(
                Q(activity__acquisition_period__employee__ativo=False)
                & Q(ctrl_payments__status__in=[2, 3])  # Declinado, Conferido
            )
        )

    def model_to_dict(self, instance):
        hoje = datetime.datetime.today().date()
        flist = js.loads(self.get_params().get("filter", "[]"))

        try:
            ano = [x["value"] for x in flist if x["property"] == "payment_year"][0]
            mes = [x["value"] for x in flist if x["property"] == "payment_month"][0]
        except:
            ano = hoje.year
            mes = hoje.month

        _dict = super(DAYOFFSellVacation, self).model_to_dict(instance)
        _dict.update({"icons": instance.icons})
        _dict.update({"earliest_date": self.set_earliest_date(instance, ano, mes)})

        return _dict

    def set_earliest_date(self, instance, ano, mes):
        dt_range = NewDateRange.range_from_month(ano, mes)
        dt_range_inicio = dt_range[0]
        dt_range_fim = dt_range[1]

        q = (
            Usufruct.objects.filter(
                activity=instance.activity,
                start_date__isnull=False,
                start_date__lte=dt_range_fim,
                start_date__gte=dt_range_inicio,
            )
            .filter(
                activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                    REGULAR_VACATIONS,
                    INDIVIDUAL_VACATION,
                ]
            )
            .exclude(pk=instance.pk)
        )

        if q.exists():
            q_atividades = q.first().activity_modifieds
            if q_atividades.exists() and q_atividades.last().usufructs.exists():
                return (
                    q_atividades.last().usufructs.last().start_date.strftime("%d/%m/%Y")
                )
            else:
                return q.first().start_date.strftime("%d/%m/%Y")
        else:
            query = instance.acquisition_period.activities.filter(type_of_activity=8)
            if query.exists() and query.last().usufructsin.exists():
                dt_inicio = query.last().usufructsin.first()["start_date"]
                return dt_inicio.strftime("%d/%m/%Y")
        return ""

    def export(self, args=[]):
        query = self.get_query().filter()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if self.request.GET.get("keyword"):
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = []
        for record in query:

            hoje = datetime.datetime.today().date()
            flist = js.loads(self.get_params().get("filter", "[]"))

            try:
                ano = [x["value"] for x in flist if x["property"] == "payment_year"][0]
                mes = [x["value"] for x in flist if x["property"] == "payment_month"][0]
            except:
                ano = hoje.year
                mes = hoje.month

            rst.append(
                {
                    "Status": (
                        record.ctrl_payments.first().get_status_display()
                        if record.ctrl_payments.first()
                        else "Sem análise"
                    ),
                    "Servidor": record.employee,
                    "Situação": record.get_status_display(),
                    "Tipo Servidor": (
                        "MEMBRO" if record.employee.is_member else "SERVIDOR"
                    ),
                    "Atividade": f"{record.activity}",
                    "Status da Atividade": record.activity.get_status_display(),
                    "Grupo": str(record.activity.acquisition_period.group_period),
                    "Data da Venda": self.set_earliest_date(record, ano, mes),
                    "Dias": record.days,
                    "Competência de Pagamento": (
                        record.competence_paid
                        if record.competence_paid
                        else (
                            f"{record.payment_competence}| {record.payment_installments}(PENDENTE)"
                            if record.payment_month and record.payment_year
                            else ""
                        )
                    ),
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    @login_required("JSON")
    def buscar_lista_anos(self, args=[]):
        obj = {"root": []}

        q_anos = (
            UsufructSell.objects.filter(
                payment_year__isnull=False,
                activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                    REGULAR_VACATIONS,
                    INDIVIDUAL_VACATION,
                ],
            )
            .exclude(status=USU_CANCELED)
            .values("payment_year")
            .annotate(dcount=Count("payment_year"))
            .order_by()
        )
        anos = [x["payment_year"] for x in q_anos if len(str(x["payment_year"])) == 4]
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
