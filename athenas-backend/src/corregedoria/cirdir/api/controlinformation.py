# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user, person_from_user
from contrib.middleware import get_current_user
from standard.models import Configuration
from django.db.models import Q
from django.template.defaultfilters import slugify
from datetime import datetime
from django.template import loader, Context
from decimal import Decimal, ROUND_UP
from django.db.models import Max
from engine.mq.models import Task
from corregedoria.cirdir.tasks import add_newyear, schedule_action
from corregedoria.cirdir.models import (
    ControlInformation,
    Address,
    Teaching,
    Property,
    Debits,
    Health,
    History,
)
from rh.models import Servidor, Lotacao
from edocs.protocolo.models import Protocolo, Movimentacao, TipoDocumento
import json

log = getLogger(__name__)


class CIRDIRControlInformation(RestfulDRY):
    _model = ControlInformation
    force_upper = False
    full_text_index = [
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
        "year__icontains",
    ]

    def json(self, args=[]):
        manage = ""
        user = get_current_user()
        if user.has_perm("cirdir.can_management_member"):
            manage = 'Ext._create("corregedoria.cirdir.Manage",{"title": "SRDIR - Administrador"})'
        elif user.has_perm("cirdir.can_management_employee"):
            manage = 'Ext._create("corregedoria.cirdir.Manage",{"title": "DBVR - Administrador"})'
        elif employee_from_user(user).tipo == "M":
            manage = 'Ext._create("corregedoria.cirdir.Manage",{"title": "SRDIR"})'
        elif employee_from_user(user).tipo == "S":
            manage = 'Ext._create("corregedoria.cirdir.Manage",{"title": "DBVR"})'

        self.response["content-type"] = "text/javascript"
        self.response.write(manage)

    def get_old_registration(self, employee):
        return Servidor.objects.exclude(pk=employee.pk).filter(
            pessoa_fisica=employee.pessoa_fisica
        )

    def get_query(self):
        atual_employee = Servidor.objects.get(
            pk=employee_from_user(get_current_user()).pk
        )
        cfg = Configuration.get_or_create("corregedoria")
        type_member = (
            cfg.get("autoCreateForTypeMember").replace('"', "")[1:-1].split(",")
        )
        type_employee = (
            cfg.get("autoCreateForTypeEmployee").replace('"', "")[1:-1].split(",")
        )
        query = ControlInformation.objects.all()
        filter = ["None"]
        if get_current_user().has_perm("cirdir.can_management_member"):
            filter = filter + type_member
        if get_current_user().has_perm("cirdir.can_management_employee"):
            filter = filter + type_employee

        query = query.exclude(hidden=True).filter(
            Q(employee__type_by_possession__in=filter) | Q(employee=atual_employee)
        )

        if not query:
            query = self.Model.objects.exclude(hidden=True).filter(
                employee__in=self.get_old_registration(atual_employee)
            )

        return query

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRControlInformation, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "person_id": instance.employee.pessoa_fisica.pk,
                "employee_type": instance.employee.tipo,
                "previous_year": (
                    instance.previous_controlinformation.year
                    if instance.previous_controlinformation
                    else None
                ),
                "check_address": instance.check_access_criteria("address"),
                "check_teaching": instance.check_access_criteria("teaching"),
                "check_property": instance.check_access_criteria("property"),
                "check_debits": instance.check_access_criteria("debits"),
                "check_health": instance.check_access_criteria("health"),
                "check_attach_irpf": instance.check_access_criteria("irpf"),
            }
        )
        return _dict_

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            controlinformation = ControlInformation.objects.filter(
                pk=int(params.get("controlinformation", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=controlinformation.rendered)
        self.renderer(rst)

    def open(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            criteria = self.request.POST.get("criteria")
            srdir_id = int(self.request.POST.get("srdir_id"))
            srdir = self.get_query().get(pk=srdir_id)
            srdir.open(criteria)
        except self.Model.DoesNotExist:
            rst.update(message="SRDIR não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="SRDIR foi aberto com sucesso.")
        return self.renderer(rst)

    def close(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            criteria = self.request.POST.get("criteria")
            srdir_id = int(self.request.POST.get("srdir_id"))
            srdir = self.get_query().get(pk=srdir_id)
            srdir.close(criteria)
        except self.Model.DoesNotExist:
            rst.update(message="SRDIR não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="SRDIR foi fechado com sucesso.")
        return self.renderer(rst)

    def open_all(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            criteria = self.request.POST.get("criteria")
            for srdir in ControlInformation.objects.filter(
                year=int(self.request.POST.get("year"))
            ):
                srdir.open(criteria)
        except self.Model.DoesNotExist:
            rst.update(message="SRDIR não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="SRDIR foi aberto com sucesso.")
        return self.renderer(rst)

    def get_lastyear(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            lastyear = ControlInformation.objects.aggregate(lastyear=Max("year"))[
                "lastyear"
            ]
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="SRDIR foi encontrado com sucesso.",
                lastyear=lastyear,
            )
        return self.renderer(rst)

    def close_all(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            criteria = self.request.POST.get("criteria")
            for srdir in ControlInformation.objects.filter(
                year=int(self.request.POST.get("year"))
            ):
                srdir.close(criteria)
        except self.Model.DoesNotExist:
            rst.update(message="SRDIR não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="SRDIR foi fechado com sucesso.")
        return self.renderer(rst)

    def add_newyear(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:

            user = get_current_user()
            if not user.has_perm("cirdir.super_administrator"):
                raise Exception("Você não possui permissão para executar essa ação.")

            lastyear = self.request.POST.get("lastyear")
            newyear = self.request.POST.get("newyear")
            address = self.request.POST.get("address") == "on"
            teaching = self.request.POST.get("teaching") == "on"
            property = self.request.POST.get("property") == "on"
            debits = self.request.POST.get("debits") == "on"
            health = self.request.POST.get("health") == "on"
            Task.start(
                add_newyear,
                newyear=newyear,
                lastyear=lastyear,
                address=address,
                teaching=teaching,
                property=property,
                debits=debits,
                health=health,
                user=user.pk,
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Adição do ano <b>%s</b> no SRDIR foi solicitada com sucesso.<br />Logo você será notificado do término da operação."
                % newyear,
            )
        return self.renderer(rst)

    def get_storeyear(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            years = (
                ControlInformation.objects.all()
                .distinct("year")
                .values("year")
                .order_by("-year")
            )
            data = []
            if years:
                data = [
                    {
                        "key": year["year"],
                        "value": str(year["year"]),
                    }
                    for year in years
                ]
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=years.count() if years else 0,
                collection=data,
            )
        return self.renderer(rst)

    def add_employeeyear(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            employee = self.request.POST.get("employee")
            year = self.request.POST.get("year")
            address = self.request.POST.get("address") == "on"
            teaching = self.request.POST.get("teaching") == "on"
            property = self.request.POST.get("property") == "on"
            debits = self.request.POST.get("debits") == "on"
            health = self.request.POST.get("health") == "on"
            if year is None or year == "":
                raise Exception("O campo <b>Ano</b> deve ser preenchido.")
            if employee is None or employee == "":
                raise Exception("O campo <b>Membro</b> deve ser preenchido.")
            if ControlInformation.objects.filter(employee=employee, year=year).exists():
                raise Exception("SRDIR já existe!")
            else:
                previous_srdir = ControlInformation.objects.filter(
                    employee_id=int(employee), year=(int(year) - 1)
                ).first()
                controlinformation = ControlInformation()
                controlinformation.employee_id = int(employee)
                controlinformation.year = int(year)
                controlinformation.previous_controlinformation = previous_srdir
                cfg = Configuration.get_or_create("corregedoria")
                controlinformation.open_date_address = datetime(
                    int(year),
                    int(cfg.get("var_open_date_address").split("/")[1]),
                    int(cfg.get("var_open_date_address").split("/")[0]),
                )
                controlinformation.close_date_address = datetime(
                    int(year),
                    int(cfg.get("var_close_date_address").split("/")[1]),
                    int(cfg.get("var_close_date_address").split("/")[0]),
                )
                controlinformation.open_date_teaching_1st_semestry = datetime(
                    int(year),
                    int(cfg.get("var_open_date_teaching_1st_semestry").split("/")[1]),
                    int(cfg.get("var_open_date_teaching_1st_semestry").split("/")[0]),
                )
                controlinformation.close_date_teaching_1st_semestry = datetime(
                    int(year),
                    int(cfg.get("var_close_date_teaching_1st_semestry").split("/")[1]),
                    int(cfg.get("var_close_date_teaching_1st_semestry").split("/")[0]),
                )
                controlinformation.open_date_teaching_2nd_semestry = datetime(
                    int(year),
                    int(cfg.get("var_open_date_teaching_2nd_semestry").split("/")[1]),
                    int(cfg.get("var_open_date_teaching_2nd_semestry").split("/")[0]),
                )
                controlinformation.close_date_teaching_2nd_semestry = datetime(
                    int(year),
                    int(cfg.get("var_close_date_teaching_2nd_semestry").split("/")[1]),
                    int(cfg.get("var_close_date_teaching_2nd_semestry").split("/")[0]),
                )
                controlinformation.open_date_property = datetime(
                    int(year),
                    int(cfg.get("var_open_date_property").split("/")[1]),
                    int(cfg.get("var_open_date_property").split("/")[0]),
                )
                controlinformation.close_date_property = datetime(
                    int(year),
                    int(cfg.get("var_close_date_property").split("/")[1]),
                    int(cfg.get("var_close_date_property").split("/")[0]),
                )
                controlinformation.open_date_debits = datetime(
                    int(year),
                    int(cfg.get("var_open_date_debits").split("/")[1]),
                    int(cfg.get("var_open_date_debits").split("/")[0]),
                )
                controlinformation.close_date_debits = datetime(
                    int(year),
                    int(cfg.get("var_close_date_debits").split("/")[1]),
                    int(cfg.get("var_close_date_debits").split("/")[0]),
                )
                controlinformation.open_date_health = datetime(
                    int(year),
                    int(cfg.get("var_open_date_health").split("/")[1]),
                    int(cfg.get("var_open_date_health").split("/")[0]),
                )
                controlinformation.close_date_health = datetime(
                    int(year),
                    int(cfg.get("var_close_date_health").split("/")[1]),
                    int(cfg.get("var_close_date_health").split("/")[0]),
                )
                controlinformation.closed_address = True
                controlinformation.closed_teaching_1st_semestry = True
                controlinformation.closed_teaching_2nd_semestry = True
                controlinformation.closed_property = True
                controlinformation.closed_debits = True
                controlinformation.closed_health = True
                controlinformation.save()
                if address:
                    for data in Address.objects.filter(
                        controlinformation=previous_srdir
                    ):
                        previous_addr = data.pk
                        data.pk = None
                        data.controlinformation = controlinformation
                        data.previous_address_id = previous_addr
                        data.save()
                if teaching:
                    for data in Teaching.objects.filter(
                        controlinformation=previous_srdir
                    ):
                        list_schedule = data.schedule.all()
                        data.pk = None
                        data.controlinformation = controlinformation
                        data.save()
                        for schedule in list_schedule:
                            data.schedule.add(schedule)
                if property:
                    for data in Property.objects.filter(
                        controlinformation=previous_srdir
                    ):
                        data.pk = None
                        data.controlinformation = controlinformation
                        data.last_value = data.current_value
                        data.save()
                if debits:
                    for data in Debits.objects.filter(
                        controlinformation=previous_srdir
                    ):
                        data.pk = None
                        data.controlinformation = controlinformation
                        data.last_value = data.current_value
                        data.save()
                if health:
                    for data in Health.objects.filter(
                        controlinformation_id=previous_srdir
                    ):
                        data.pk = None
                        data.controlinformation = controlinformation
                        data.save()
        except Exception as e:
            rst.update(
                success=False,
                message=str(e),
            )
        else:
            rst.update(
                success=True,
                message="SRDIR foi adicionado com sucesso.",
            )
        return self.renderer(rst)

    def delete_employeeyear(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:

            year = self.request.POST.get("year", None)
            employee = self.request.POST.get("employee", None)

            if year and employee:
                control = ControlInformation.objects.get(year=year, employee=employee)
                control.delete()
            else:
                raise Exception("Informe o Ano e o Integrante.")

        except Exception as e:
            rst.update(
                success=False,
                message=str(e),
            )
        else:
            rst.update(
                success=True,
                message="Concluído com sucesso.",
                count=1,
            )
        return self.renderer(rst)

    def has_perm_to(self, user=None, apply_to=None):
        has_perm = False
        if user.has_perm("cirdir.super_administrator"):
            has_perm = True
        else:
            if user.has_perm("cirdir.can_management_member") and apply_to == "M":
                has_perm = True
            elif user.has_perm("cirdir.can_management_employee") and apply_to == "S":
                has_perm = True
        return has_perm

    def schedule_action(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            user = get_current_user()
            apply_to = self.request.POST.get("apply_to")
            employee = self.request.POST.get("employee")
            action_type = self.request.POST.get("action_type")
            action_date = self.request.POST.get("action_date")
            criteria = self.request.POST.get("criteria")
            year = (
                int(self.request.POST.get("year"))
                if self.request.POST.get("year")
                else 0
            )

            if employee:
                employee = int(employee)
                apply_to = Servidor.objects.get(pk=employee).tipo
            elif apply_to == "ONE" and not employee:
                raise Exception(
                    "Informe para qual pessoa será realizado o agendamento."
                )

            if action_type not in ["2", "3"]:
                raise Exception("Selecione uma ação para agendamento.")
            if action_date is None:
                raise Exception("Informe uma data para agendamento.")
            if criteria not in ["2", "3", "4", "5", "6", "7", "8"]:
                raise Exception("Selecione um critério para agendamento.")
            if year == 0:
                raise Exception("Selecione um ano para agendamento.")

            if apply_to == "ALL":
                apply_to = None

            if self.has_perm_to(user=user, apply_to=apply_to):

                Task.start(
                    schedule_action,
                    action_type=action_type,
                    action_date=action_date,
                    criteria=criteria,
                    year=year,
                    employee=employee,
                    user=user.pk,
                    apply_to=apply_to,
                )
            else:
                raise Exception("Você não possui permissão para executar essa ação.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Agendamento no SRDIR foi solicitado com sucesso.<br />Logo você será notificado do término da operação.",
            )
        return self.renderer(rst)

    def submit(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:

            controlinformation = ControlInformation.objects.filter(
                pk=int(self.request.POST.get("controlinformation"))
            ).first()
            criteria = self.request.POST.get("criteria")
            if criteria == "teaching":
                if controlinformation.closed_teaching_1st_semestry is False:
                    criteria = "teaching_1st_semestry"
                else:
                    if controlinformation.closed_teaching_2nd_semestry is False:
                        criteria = "teaching_2nd_semestry"
            health_area = (
                True
                if self.request.POST.get("authorization_health") == "true"
                else False
            )
            empty = True if self.request.POST.get("emptySubmit") == "true" else False
            controlinformation.authorization_health = health_area

            controlinformation.pre_submit_validation(
                criteria=criteria, check_empty=empty
            )

            controlinformation.submit(criteria=criteria, health_area=health_area)
        except self.Model.DoesNotExist:
            rst.update(message="SRDIR não foi encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Submetido com sucesso!")
        return self.renderer(rst)

    def send_search(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            list_employees = []
            employees = Servidor.objects.filter(
                pk__in=params.get("employee", 0).split(",")
            )
            for employee in employees:
                list_employees.append(employee.pessoa_fisica.pk)
            subject = "Pesquisa Institucional - Projeto Você é Único"
            cfg = Configuration.get_or_create("corregedoria")
            loc_origin = Lotacao.objects.get(pk=44164)
            resp_origin = loc_origin.responsavel
            data = [loader.get_template("send_search.html").render({})]
            message = "".join(data).replace("\n", "")
            protocol = Protocolo.docketing(
                subject=subject,
                document_type=TipoDocumento.objects.get(pk=94),
                interested=person_from_user(resp_origin.user),
                home_court=loc_origin,
                content=message,
            )
            current = Movimentacao.inbox_queryset().get(protocolo=protocol)
            current.do_send(
                person_destination=list_employees,
                employee_origin=employee_from_user(get_current_user()),
                physical=False,
                opinion=True,
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Pesquisa enviada com sucesso.",
            )
        return self.renderer(rst)

    def years(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }

        try:
            years = (
                self._model.objects.order_by("-year")
                .distinct("year")
                .values_list("year", flat=True)
            )
        except Exception as e:
            rst.update(message=str(e.message))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=years.count(),
                collection=[{"year": v} for v in years],
            )

        self.renderer(rst)
