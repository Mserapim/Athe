# -*- coding: utf-8 -*-

import re
import enum

from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template import loader
from django.db import models, transaction
from django.contrib.auth.models import User, Group
from django.db.models import Q

from engine.models import ControllerPermission
from standard.models import AuditTimestampModel, Choice, Configuration
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user

from ged.models import Arquivo
from rh.models import Servidor, Lotacao, Endereco, Localidade, PessoaJuridica, Pais


log = getLogger(__name__)


class Category(enum.Enum):
    address = 1
    teaching = 2
    property = 3
    debits = 4
    health = 5
    irpf = 6


class ControlInformation(AuditTimestampModel):
    """
    Controle de informacoes
    """

    previous_controlinformation = models.ForeignKey(
        "ControlInformation",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        Servidor, related_name="controlinformations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    year = models.PositiveSmallIntegerField()

    closed_teaching_1st_semestry = models.BooleanField(null=True, blank=True)
    open_date_teaching_1st_semestry = models.DateTimeField(null=True, blank=True)
    close_date_teaching_1st_semestry = models.DateTimeField(null=True, blank=True)
    teaching_1st_semestry_submitted_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    teaching_1st_semestry_submitted_at = models.DateTimeField(null=True, blank=True)
    closed_teaching_2nd_semestry = models.BooleanField(null=True, blank=True)
    open_date_teaching_2nd_semestry = models.DateTimeField(null=True, blank=True)
    close_date_teaching_2nd_semestry = models.DateTimeField(null=True, blank=True)
    teaching_2nd_semestry_submitted_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    teaching_2nd_semestry_submitted_at = models.DateTimeField(null=True, blank=True)
    closed_address = models.BooleanField(null=True, blank=True)
    open_date_address = models.DateTimeField(null=True, blank=True)
    close_date_address = models.DateTimeField(null=True, blank=True)
    address_submitted_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    address_submitted_at = models.DateTimeField(null=True, blank=True)
    closed_property = models.BooleanField(null=True, blank=True)
    open_date_property = models.DateTimeField(null=True, blank=True)
    close_date_property = models.DateTimeField(null=True, blank=True)
    property_submitted_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    property_submitted_at = models.DateTimeField(null=True, blank=True)
    closed_debits = models.BooleanField(null=True, blank=True)
    open_date_debits = models.DateTimeField(null=True, blank=True)
    close_date_debits = models.DateTimeField(null=True, blank=True)
    debits_submitted_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    debits_submitted_at = models.DateTimeField(null=True, blank=True)
    closed_health = models.BooleanField(null=True, blank=True)
    open_date_health = models.DateTimeField(null=True, blank=True)
    close_date_health = models.DateTimeField(null=True, blank=True)
    health_submitted_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    health_submitted_at = models.DateTimeField(null=True, blank=True)
    authorization_health = models.BooleanField(null=True, blank=True)
    pendency_address = models.BooleanField(default=False)
    pendency_address_msg = models.TextField(null=True, blank=True)
    pendency_teaching_1st_semestry = models.BooleanField(default=False)
    pendency_teaching_1st_semestry_msg = models.TextField(null=True, blank=True)
    pendency_teaching_2nd_semestry = models.BooleanField(default=False)
    pendency_teaching_2nd_semestry_msg = models.TextField(null=True, blank=True)
    pendency_property = models.BooleanField(default=False)
    pendency_property_msg = models.TextField(null=True, blank=True)
    pendency_debits = models.BooleanField(default=False)
    pendency_debits_msg = models.TextField(null=True, blank=True)
    pendency_health = models.BooleanField(default=False)
    pendency_health_msg = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    open_date_irpf = models.DateTimeField(null=True, blank=True)
    close_date_irpf = models.DateTimeField(null=True, blank=True)
    closed_irpf = models.BooleanField(default=True)
    pendency_irpf = models.BooleanField(default=False)
    pendency_irpf_msg = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-year", "employee__pessoa_fisica__nome"]
        verbose_name = "Controle de Informações sobre Docência, Residência e Finanças"
        permissions = (
            ("can_management_member", "Pode gerenciar o CIRDIR dos Membros"),
            ("can_management_employee", "Pode gerenciar o CIRDIR dos Servidores"),
            ("can_management_health_area", "Pode gerenciar o Você é Único"),
        )

    @property
    def refer_year(self):
        return self.year - 1

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        msg = ""
        cnt = 0
        if (
            (self.closed_address == False and self.check_access_criteria("address"))
            or (
                self.closed_teaching_1st_semestry == False
                and self.check_access_criteria("teaching")
            )
            or (
                self.closed_teaching_2nd_semestry == False
                and self.check_access_criteria("teaching")
            )
            or (
                self.closed_property == False and self.check_access_criteria("property")
            )
            or (self.closed_debits == False and self.check_access_criteria("debits"))
            or (self.closed_health == False and self.check_access_criteria("health"))
        ):
            if self.closed_address == False and self.check_access_criteria("address"):
                cnt += 1
                msg = msg + "Aberto (<b>Residência</b>)" + ("" if cnt < 1 else "<br />")
            if (
                self.closed_teaching_1st_semestry == False
                and self.check_access_criteria("teaching")
            ):
                cnt += 1
                msg = (
                    msg
                    + "Aberto (<b>Docência 1º Semestre</b>)"
                    + ("" if cnt < 1 else "<br />")
                )
            if (
                self.closed_teaching_2nd_semestry == False
                and self.check_access_criteria("teaching")
            ):
                cnt += 1
                msg = (
                    msg
                    + "Aberto (<b>Docência 2º Semestre</b>)"
                    + ("" if cnt < 1 else "<br />")
                )
            if self.closed_property == False and self.check_access_criteria("property"):
                cnt += 1
                msg = (
                    msg
                    + "Aberto (<b>Bens e Direitos</b>)"
                    + ("" if cnt < 1 else "<br />")
                )
            if self.closed_debits == False and self.check_access_criteria("debits"):
                cnt += 1
                msg = (
                    msg
                    + "Aberto (<b>Dívidas e Ônus Reais</b>)"
                    + ("" if cnt < 1 else "<br />")
                )
            if self.closed_irpf == False and self.check_access_criteria("irpf"):
                cnt += 1
                msg = (
                    msg
                    + "Aberto (<b>Envio da Declaração do IRPF</b>)"
                    + ("" if cnt < 1 else "<br />")
                )
            if self.closed_health == False and self.check_access_criteria("health"):
                cnt += 1
                msg = msg + "Aberto (<b>Saúde</b>)"
            item = {"title": msg, "iconCls": "icon-crgmpe icon-crgmpe-open"}
        else:
            item = {"title": "Fechado", "iconCls": "icon-crgmpe icon-crgmpe-close"}
        rst.append(item)
        if self.check_access_criteria("address"):
            if datetime.now().date() >= self.open_date_address.date():
                if Address.objects.filter(controlinformation=self).exists():
                    if self.address_submitted_by:
                        item = {
                            "title": "Residência informada",
                            "iconCls": "icon-crgmpe icon-crgmpe-go-home",
                        }
                    else:
                        item = {
                            "title": "Residência informada, mas não submetida",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                        }
                else:
                    if self.address_submitted_by:
                        item = {
                            "title": "Não possui Residência",
                            "iconCls": "icon-crgmpe icon-crgmpe-arrows",
                        }
                    else:
                        item = {
                            "title": "Sem informação de Residência",
                            "iconCls": "icon-crgmpe icon-crgmpe-exclamation-circle",
                        }
                if self.pendency_address:
                    item = {
                        "title": self.pendency_address_msg,
                        "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                    }
                rst.append(item)
        if self.check_access_criteria("teaching"):
            if datetime.now().date() >= self.open_date_teaching_1st_semestry.date():
                if Teaching.objects.filter(controlinformation=self, period=1).exists():
                    if self.teaching_1st_semestry_submitted_by:
                        item = {
                            "title": "Exerce Docência (1º Semestre)",
                            "iconCls": "icon-crgmpe icon-crgmpe-book",
                        }
                    else:
                        item = {
                            "title": "Docência informada (1º Semestre), mas não submetida",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                        }
                else:
                    if self.teaching_1st_semestry_submitted_by:
                        item = {
                            "title": "Não exerce Docência (1º Semestre)",
                            "iconCls": "icon-crgmpe icon-crgmpe-report",
                        }
                    else:
                        item = {
                            "title": "Sem informação de Docência (1º Semestre)",
                            "iconCls": "icon-crgmpe icon-crgmpe-exclamation-circle",
                        }
                if self.pendency_teaching_1st_semestry:
                    item = {
                        "title": self.pendency_teaching_1st_semestry_msg,
                        "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                    }
                rst.append(item)
        if self.check_access_criteria("teaching"):
            if datetime.now().date() >= self.open_date_teaching_2nd_semestry.date():
                if Teaching.objects.filter(controlinformation=self, period=2).exists():
                    if self.teaching_2nd_semestry_submitted_by:
                        item = {
                            "title": "Exerce Docência (2º Semestre)",
                            "iconCls": "icon-crgmpe icon-crgmpe-open-bookmark",
                        }
                    else:
                        item = {
                            "title": "Docência informada (2º Semestre), mas não submetida",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                        }
                else:
                    if self.teaching_2nd_semestry_submitted_by:
                        item = {
                            "title": "Não exerce  (2º Semestre)",
                            "iconCls": "icon-crgmpe icon-crgmpe-report",
                        }
                    else:
                        item = {
                            "title": "Sem informação de Docência (2º Semestre)",
                            "iconCls": "icon-crgmpe icon-crgmpe-exclamation-circle",
                        }
                if self.pendency_teaching_2nd_semestry:
                    item = {
                        "title": self.pendency_teaching_2nd_semestry_msg,
                        "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                    }
                rst.append(item)
        if self.check_access_criteria("property"):
            if datetime.now().date() >= self.open_date_property.date():
                if Property.objects.filter(controlinformation=self).exists():
                    if self.property_submitted_by:
                        item = {
                            "title": "Bens e Direitos informados",
                            "iconCls": "icon-crgmpe icon-crgmpe-table-money",
                        }
                    else:
                        item = {
                            "title": "Bens e Direitos informados, mas não submetida",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                        }
                else:
                    if self.property_submitted_by:
                        item = {
                            "title": "Não possui Bens e Direitos",
                            "iconCls": "icon-crgmpe icon-crgmpe-detalhes",
                        }
                    else:
                        item = {
                            "title": "Sem informação de Bens e Direitos",
                            "iconCls": "icon-crgmpe icon-crgmpe-exclamation-circle",
                        }
                if self.pendency_property:
                    item = {
                        "title": self.pendency_property_msg,
                        "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                    }
                rst.append(item)
        if self.check_access_criteria("debits"):
            if datetime.now().date() >= self.open_date_debits.date():
                if Debits.objects.filter(controlinformation=self).exists():
                    if self.debits_submitted_by:
                        item = {
                            "title": "Dívidas e Ônus Reais informados",
                            "iconCls": "icon-crgmpe icon-crgmpe-minus",
                        }
                    else:
                        item = {
                            "title": "Dívidas e Ônus Reais informados, mas não submetida",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                        }
                else:
                    if self.debits_submitted_by:
                        item = {
                            "title": "Não possui Dívidas e Ônus Reais",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-busy",
                        }
                    else:
                        item = {
                            "title": "Sem informação de Dívidas e Ônus Reais",
                            "iconCls": "icon-crgmpe icon-crgmpe-exclamation-circle",
                        }
                if self.pendency_debits:
                    item = {
                        "title": self.pendency_debits_msg,
                        "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                    }
                rst.append(item)

        if self.check_access_criteria("irpf"):
            try:
                item = {}
                if datetime.now().date() >= self.open_date_irpf.date():
                    irpf = self.in_irpf.get()
                    if irpf.validated:
                        item = {
                            "title": "Declaração do IPRF submetida",
                            "iconCls": "icon-crgmpe icon-crgmpe-minus",
                        }
                    else:
                        item = {
                            "title": "Declaração do IPRF é inválida",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                        }
            except Exception as e:
                item = {
                    "title": "Declaração do IPRF não submetida",
                    "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                }
            finally:
                if self.pendency_irpf:
                    item = {
                        "title": self.pendency_irpf_msg,
                        "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                    }

                rst.append(item)

        if self.check_access_criteria("health"):
            if datetime.now().date() >= self.open_date_health.date():
                if Health.objects.filter(controlinformation=self).exists():
                    if self.health_submitted_by:
                        item = {
                            "title": "Saúde informada",
                            "iconCls": "icon-crgmpe icon-crgmpe-health",
                        }
                    else:
                        item = {
                            "title": "Saúde informada, mas não submetida",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-block",
                        }
                else:
                    if self.health_submitted_by:
                        item = {
                            "title": "Não possui Saúde",
                            "iconCls": "icon-crgmpe icon-crgmpe-status-busy",
                        }
                    else:
                        item = {
                            "title": "Sem informação de Saúde",
                            "iconCls": "icon-crgmpe icon-crgmpe-exclamation-circle",
                        }
                if self.pendency_health:
                    item = {
                        "title": self.pendency_health_msg,
                        "iconCls": "icon-crgmpe icon-crgmpe-exclamation-red",
                    }
                rst.append(item)
        return rst

    @property
    def rendered(self):
        tpl = loader.get_template("controlinformation.html")
        return tpl.render(
            {
                "controlinformation": self,
                "status_address_rendered": self.submit_status_part_rendered(
                    Address.codename
                ),
                "status_teaching_one_rendered": self.submit_status_part_rendered(
                    "teaching_1st_semestry"
                ),
                "status_teaching_two_rendered": self.submit_status_part_rendered(
                    "teaching_2nd_semestry"
                ),
                "status_property_rendered": self.submit_status_part_rendered(
                    Property.codename
                ),
                "status_debits_rendered": self.submit_status_part_rendered(
                    Debits.codename
                ),
                "status_irpf_rendered": self.submit_status_part_rendered(Irpf.codename),
                "check_address": self.check_access_criteria("address"),
                "check_teaching": self.check_access_criteria("teaching"),
                "check_property": self.check_access_criteria("property"),
                "check_debits": self.check_access_criteria("debits"),
                "check_health": self.check_access_criteria("health"),
                "check_irpf": self.check_access_criteria("irpf"),
                "title_app": "SRDIR" if self.employee.tipo == "M" else "DBVR",
                "pendency_address_rendered": self.pendency_part_rendered(
                    Address.codename
                ),
                "pendency_teaching_one_rendered": self.pendency_part_rendered(
                    "teaching_1st_semestry"
                ),
                "pendency_teaching_two_rendered": self.pendency_part_rendered(
                    "teaching_2nd_semestry"
                ),
                "pendency_property_rendered": self.pendency_part_rendered(
                    Property.codename
                ),
                "pendency_debits_rendered": self.pendency_part_rendered(
                    Debits.codename
                ),
                "pendency_irpf_rendered": self.pendency_part_rendered(Irpf.codename),
            }
        )

    def pendency_part_rendered(self, codename):
        try:
            return Pendency.rendered(self, codename)
        except Exception as e:
            return e

    @property
    def rendered_healtharea(self):
        tpl = loader.get_template("healtharea.html")
        return tpl.render({})

    @property
    def address_status(self):
        status = ""
        if Address.objects.filter(controlinformation=self).exists():
            if self.address_submitted_by:
                status = "Residência informada"
            else:
                status = "Residência informada, mas não submetida"
        else:
            if self.address_submitted_by:
                status = "Não possui Residência"
            else:
                status = "Sem informação de Residência"
        return status

    @property
    def teaching_1st_semestry_status(self):
        status = ""
        if Teaching.objects.filter(controlinformation=self, period=1).exists():
            if self.teaching_1st_semestry_submitted_by:
                status = "Exerce Docência (1º Semestre)"
            else:
                status = "Docência informada (1º Semestre), mas não submetida"
        else:
            if self.teaching_1st_semestry_submitted_by:
                status = "Não exerce Docência (1º Semestre)"
            else:
                status = "Sem informação de Docência (1º Semestre)"
        return status

    @property
    def teaching_2nd_semestry_status(self):
        status = ""
        if Teaching.objects.filter(controlinformation=self, period=2).exists():
            if self.teaching_2nd_semestry_submitted_by:
                status = "Exerce Docência (2º Semestre)"
            else:
                status = "Docência informada (2º Semestre), mas não submetida"
        else:
            if self.teaching_2nd_semestry_submitted_by:
                status = "Não exerce Docência (2º Semestre)"
            else:
                status = "Sem informação de Docência (2º Semestre)"
        return status

    @property
    def property_status(self):
        status = ""
        if Property.objects.filter(controlinformation=self).exists():
            if self.property_submitted_by:
                status = "Bens e Direitos informados"
            else:
                status = "Bens e Direitos informados, mas não submetida"
        else:
            if self.property_submitted_by:
                status = "Não possui Bens e Direitos"
            else:
                status = "Sem informação de Bens e Direitos"
        return status

    @property
    def debits_status(self):
        status = ""
        if Debits.objects.filter(controlinformation=self).exists():
            if self.debits_submitted_by:
                status = "Dívidas e Ônus Reais informados"
            else:
                status = "Dívidas e Ônus Reais informados, mas não submetida"
        else:
            if self.debits_submitted_by:
                status = "Não possui Dívidas e Ônus Reais"
            else:
                status = "Sem informação de Dívidas e Ônus Reais"
        return status

    @property
    def irpf_status(self):
        try:
            irpf = self.in_irpf.get()
            return irpf.status
        except Exception as e:
            return "Declaração do imposto de renda não foi informada."

    @property
    def health_status(self):
        status = ""
        if Health.objects.filter(controlinformation=self).exists():
            if self.health_submitted_by:
                status = "Saúde informada"
            else:
                status = "Saúde informada, mas não submetida"
        else:
            if self.health_submitted_by:
                status = "Não possui Saúde"
            else:
                status = "Sem informação de Saúde"
        return status

    def check_access_criteria(self, criteria=None):

        cfg = Configuration.get_or_create("corregedoria")

        profile = "member" if self.employee.tipo == "M" else "employee"

        group_permisison = {
            "address": int(cfg.get("var_" + profile + "_address", 0)),
            "teaching": int(cfg.get("var_" + profile + "_teaching", 0)),
            "property": int(cfg.get("var_" + profile + "_property", 0)),
            "debits": int(cfg.get("var_" + profile + "_debits", 0)),
            "health": int(cfg.get("var_" + profile + "_health", 0)),
            "irpf": int(cfg.get("var_" + profile + "_irpf", 0)),
        }

        permission = group_permisison.get(criteria, 0) == 1

        # FIX-ME: Anos anteriores a 2021 exibir property, debits
        # e onus. A partir de 2022 nao exibi-los e exibit IRPF
        # ISSO deve ser melhorado.

        if self.year <= 2021:
            if criteria in ["property", "debits"]:
                permission = True

            if criteria == "irpf":
                permission = False
        else:
            if criteria in ["property", "debits"]:
                permission = False

            if criteria == "irpf":
                permission = True

        return permission

    def open(self, criteria):
        if criteria == "address":
            self.open_date_address = datetime.now()
        if criteria == "teaching_1st_semestry":
            self.open_date_teaching_1st_semestry = datetime.now()
        if criteria == "teaching_2nd_semestry":
            self.open_date_teaching_2nd_semestry = datetime.now()
        if criteria == "property":
            self.open_date_property = datetime.now()
        if criteria == "debits":
            self.open_date_debits = datetime.now()
        if criteria == "irpf":
            self.open_date_irpf = datetime.now()
        if criteria == "health":
            self.open_date_health = datetime.now()
        self.nusubmit(criteria)
        self.save()

    def close(self, criteria):
        if criteria == "address":
            self.close_date_address = datetime.now()
        if criteria == "teaching_1st_semestry":
            self.close_date_teaching_1st_semestry = datetime.now()
        if criteria == "teaching_2nd_semestry":
            self.close_date_teaching_2nd_semestry = datetime.now()
        if criteria == "property":
            self.close_date_property = datetime.now()
        if criteria == "debits":
            self.close_date_debits = datetime.now()
        if criteria == "irpf":
            self.close_date_irpf = datetime.now()
        if criteria == "health":
            self.close_date_health = datetime.now()
        self.save()

    def part_name_by_criteria(self, criteria="", all=False):

        names = {
            "address": Address.codename,
            "teaching_1st_semestry": "teaching_1st_semestry",
            "teaching_2nd_semestry": "teaching_2nd_semestry",
            "property": Property.codename,
            "debits": Debits.codename,
            "irpf": Irpf.codename,
        }

        if all:
            return names
        else:
            return names.get(criteria)

    def nusubmit(self, criteria=None):

        if criteria is None:
            pass
        else:
            SubmitStatus.initial_status(
                control_information=self,
                part=self.part_name_by_criteria(criteria=criteria),
            )

        if criteria == "address":
            self.address_submitted_by = None
            self.address_submitted_at = None
        if criteria == "teaching_1st_semestry":
            self.teaching_1st_semestry_submitted_by = None
            self.teaching_1st_semestry_submitted_at = None
        if criteria == "teaching_2nd_semestry":
            self.teaching_2nd_semestry_submitted_by = None
            self.teaching_2nd_semestry_submitted_at = None
        if criteria == "property":
            self.property_submitted_by = None
            self.property_submitted_at = None
        if criteria == "debits":
            self.debits_submitted_by = None
            self.debits_submitted_at = None
        if criteria == "health":
            self.health_submitted_by = None
            self.health_submitted_at = None
        if criteria is None:
            self.address_submitted_by = None
            self.address_submitted_at = None
            self.teaching_1st_semestry_submitted_by = None
            self.teaching_1st_semestry_submitted_at = None
            self.teaching_2nd_semestry_submitted_by = None
            self.teaching_2nd_semestry_submitted_at = None
            self.property_submitted_by = None
            self.property_submitted_at = None
            self.debits_submitted_by = None
            self.debits_submitted_at = None
            self.health_submitted_by = None
            self.health_submitted_at = None

    def has_information_outdated(self, klass):
        return (
            klass.objects.filter(controlinformation=self)
            .filter(updated_at__lte=self.created_at)
            .exists()
        )

    def check_has_information_outdated(self, klass):
        has = self.has_information_outdated(klass)
        if has:
            raise Exception("Há informação desatualizada.")

    def _add_for_audit(self, queryset):
        has_audit = False
        for obj in queryset:
            if obj.is_auditable:
                InformationEvaluation.add_to_audit(obj)
                has_audit = True

        return has_audit

    def _submit_criteria(self, klass, objects, category, part_name, criteria):

        try:
            self.check_has_information_outdated(klass)

            has_audit = False
            for obj in objects:
                if obj.is_auditable:
                    has_audit = True

            SubmitStatus.register(
                control_information=self,
                part=self.part_name_by_criteria(criteria=criteria),
                objects=objects,
                category=category,
                is_auditable=has_audit,
            )

            self.register_history(criteria=category, action=f"{part_name}: Submetido.")

        except Exception as e:
            log.error("erro ao submter informação no SRDIR")
            raise e

    def submit(self, criteria, health_area=False):
        employee = employee_from_user(get_current_user())
        if self.employee == employee:

            if criteria == "address":
                self._submit_criteria(
                    klass=Address,
                    objects=self.in_address.all(),
                    category=Category.address.value,
                    part_name="Endereço",
                    criteria="address",
                )

            if criteria == "teaching_1st_semestry":
                self._submit_criteria(
                    Teaching,
                    self.in_teaching.filter(period=1),
                    Category.teaching.value,
                    "Docência 1° semestre",
                    criteria="teaching_1st_semestry",
                )

            if criteria == "teaching_2nd_semestry":
                self._submit_criteria(
                    Teaching,
                    self.in_teaching.filter(period=2),
                    Category.teaching.value,
                    "Docência 2° semestre",
                    criteria="teaching_2nd_semestry",
                )

            if criteria == "property":
                self._submit_criteria(
                    Property,
                    self.in_property.all(),
                    Category.property.value,
                    "Bens e Direitos",
                    criteria="property",
                )

            if criteria == "debits":
                self._submit_criteria(
                    Debits,
                    self.in_debits.all(),
                    Category.debits.value,
                    "Dívidas e Ônus Reais",
                    criteria="debits",
                )

            if criteria == "health":
                self.health_submitted_by = get_current_user()
                self.health_submitted_at = datetime.now()
                self.register_history(
                    criteria=Category.health.value, action="Submetendo Saúde"
                )
                if health_area is True:
                    # self.distribute_to_evaluators()
                    self.register_history(
                        criteria=Category.health.value,
                        action="Submetendo questionário de saúde a área da saúde",
                    )
            self.save()
        else:
            raise Exception(
                "Somente o membro/servidor vinculado pode submeter a informação."
            )

    @property
    def _can_exec_close_address(self):
        if self.check_access_criteria("address"):
            if self.closed_address is False and self.close_date_address is not None:
                if datetime.now().date() > self.close_date_address.date():
                    return True
        return False

    @property
    def _can_exec_close_teaching_1st(self):
        if self.check_access_criteria("teaching"):
            if (
                self.closed_teaching_1st_semestry is False
                and self.close_date_teaching_1st_semestry is not None
            ):
                if datetime.now().date() > self.close_date_teaching_1st_semestry.date():
                    return True
        return False

    @property
    def _can_exec_close_teaching_2nd(self):
        if self.check_access_criteria("teaching"):
            if (
                self.closed_teaching_2nd_semestry is False
                and self.close_date_teaching_2nd_semestry is not None
            ):
                if datetime.now().date() > self.close_date_teaching_2nd_semestry.date():
                    return True
        return False

    @property
    def _can_exec_close_property(self):
        if self.check_access_criteria("property"):
            if self.closed_property is False and self.close_date_property is not None:
                if datetime.now().date() > self.close_date_property.date():
                    return True
        return False

    @property
    def _can_exec_close_debits(self):
        if self.check_access_criteria("debits"):
            if self.closed_debits is False and self.close_date_debits is not None:
                if datetime.now().date() > self.close_date_debits.date():
                    return True
        return False

    @property
    def _can_exec_close_irpf(self):
        if self.check_access_criteria("irpf"):
            if self.closed_irpf is False and self.close_date_irpf is not None:
                if datetime.now().date() > self.close_date_irpf.date():
                    return True
        return False

    @property
    def _can_exec_close_health(self):
        if self.check_access_criteria("health"):
            if self.closed_health is False and self.close_date_health is not None:
                if datetime.now().date() > self.close_date_health.date():
                    return True
        return False

    def exec_schedule(self, saving=True, signal=True):
        if saving and not self.hidden:
            if self.check_access_criteria("address"):
                if self.closed_address is True and (
                    datetime.now().date() >= self.open_date_address.date()
                    and (
                        datetime.now().date() < self.close_date_address.date()
                        or self.close_date_address is None
                    )
                ):
                    self.closed_address = False
                    self.register_history(
                        criteria=Category.address.value, action="Abrindo Residência"
                    )
            if self.check_access_criteria("teaching"):
                if self.closed_teaching_1st_semestry is True and (
                    datetime.now().date() >= self.open_date_teaching_1st_semestry.date()
                    and (
                        datetime.now().date()
                        < self.close_date_teaching_1st_semestry.date()
                        or self.close_date_teaching_1st_semestry is None
                    )
                ):
                    self.closed_teaching_1st_semestry = False
                    self.register_history(
                        criteria=Category.teaching.value,
                        action="Abrindo Docência (1º Semestre)",
                    )
            if self.check_access_criteria("teaching"):
                if self.closed_teaching_2nd_semestry is True and (
                    datetime.now().date() >= self.open_date_teaching_2nd_semestry.date()
                    and (
                        datetime.now().date()
                        < self.close_date_teaching_2nd_semestry.date()
                        or self.close_date_teaching_2nd_semestry is None
                    )
                ):
                    self.closed_teaching_2nd_semestry = False
                    self.register_history(
                        criteria=Category.teaching.value,
                        action="Abrindo Docência (2º Semestre)",
                    )
            if self.check_access_criteria("property"):
                if self.closed_property is True and (
                    datetime.now().date() >= self.open_date_property.date()
                    and (
                        datetime.now().date() < self.close_date_property.date()
                        or self.close_date_property is None
                    )
                ):
                    self.closed_property = False
                    self.register_history(
                        criteria=Category.property.value,
                        action="Abrindo Bens e Direitos",
                    )
            if self.check_access_criteria("debits"):
                if self.closed_debits is True and (
                    datetime.now().date() >= self.open_date_debits.date()
                    and (
                        datetime.now().date() < self.close_date_debits.date()
                        or self.close_date_debits is None
                    )
                ):
                    self.closed_debits = False
                    self.register_history(
                        criteria=Category.debits.value,
                        action="Abrindo Dívidas e Ônus Reais",
                    )
            if self.check_access_criteria("irpf"):
                if self.open_date_irpf:
                    if self.closed_irpf is True and (
                        datetime.now().date() >= self.open_date_irpf.date()
                        and (
                            datetime.now().date() < self.close_date_irpf.date()
                            or self.close_date_irpf is None
                        )
                    ):
                        self.closed_irpf = False
                        self.register_history(
                            criteria=Category.irpf.value,
                            action="Abrindo Declaração do IRPF",
                        )
            if self.check_access_criteria("health"):
                if self.closed_health is True and (
                    datetime.now().date() >= self.open_date_health.date()
                    and (
                        datetime.now().date() < self.close_date_health.date()
                        or self.close_date_health is None
                    )
                ):
                    self.closed_health = False
                    self.register_history(
                        criteria=Category.health.value, action="Abrindo Saúde"
                    )

            if self._can_exec_close_address:
                self.closed_address = True
                self.register_history(
                    criteria=Category.address.value, action="Fechando Residência"
                )

            if self._can_exec_close_teaching_1st:
                self.closed_teaching_1st_semestry = True
                self.register_history(
                    criteria=Category.teaching.value,
                    action="Fechando Docência (1º Semestre)",
                )

            if self._can_exec_close_teaching_2nd:
                self.closed_teaching_2nd_semestry = True
                self.register_history(
                    criteria=Category.teaching.value,
                    action="Fechando Docência (2º Semestre)",
                )

            if self._can_exec_close_property:
                self.closed_property = True
                self.register_history(
                    criteria=Category.property.value, action="Fechando Bens e Direitos"
                )

            if self._can_exec_close_debits:
                self.closed_debits = True
                self.register_history(
                    criteria=Category.debits.value,
                    action="Fechando Dívidas e Ônus Reais",
                )

            if self._can_exec_close_irpf:
                self.closed_irpf = True
                self.register_history(
                    criteria=Category.irpf.value, action="Fechando Declaração do IRPF"
                )

            if self._can_exec_close_health:
                self.closed_health = True
                self.register_history(
                    criteria=Category.health.value, action="Fechando Saúde"
                )

            self._run_signal = signal

            # self.check_pendincies(saving)
            self.save(saving=False)
            self.pendencies_check()

    def part_was_submitted(self, part):
        return (
            SubmitStatus.current_status_by_part(control_information=self, part=part)
            == SubmitStatus.SUBMITTED
        )

    def _pendencies_submitted_address(self):
        try:
            if (
                self.check_access_criteria(Address.codename)
                and datetime.now().date() >= self.open_date_address.date()
            ):
                submitted = self.part_was_submitted(Address.codename)

                if not submitted and (
                    self.close_date_address is not None
                    and datetime.now().date() > self.close_date_address.date()
                ):
                    Pendency.register(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Address.codename,
                        message="Pendência: Informação sobre <b>Residência</b> não foi submetido.",
                    )
                else:
                    Pendency.unregister(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Address.codename,
                    )
        except Exception as e:
            log.error("Erro ao criar pendencia de submissão do endereço")
            raise e

    def _pendencies_submitted_teaching_one(self):
        try:
            if (
                self.check_access_criteria("teaching")
                and datetime.now().date() >= self.open_date_teaching_1st_semestry.date()
            ):
                submitted = self.part_was_submitted("teaching_1st_semestry")

                if not submitted and (
                    self.close_date_teaching_1st_semestry is not None
                    and datetime.now().date()
                    > self.close_date_teaching_1st_semestry.date()
                ):
                    Pendency.register(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part="teaching_1st_semestry",
                        message="Pendência: Informação sobre <b>Docência do 1º semestre</b> não foi submetido.",
                    )
                else:
                    Pendency.unregister(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part="teaching_1st_semestry",
                    )

        except Exception as e:
            log.error("Erro ao criar pendencia de submissão da docência do 1º semestre")
            raise e

    def _pendencies_submitted_teaching_two(self):
        try:
            if (
                self.check_access_criteria("teaching")
                and datetime.now().date() >= self.open_date_teaching_2nd_semestry.date()
            ):

                submitted = self.part_was_submitted("teaching_2nd_semestry")

                if not submitted and (
                    self.close_date_teaching_2nd_semestry is not None
                    and datetime.now().date()
                    > self.close_date_teaching_2nd_semestry.date()
                ):
                    Pendency.register(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part="teaching_2nd_semestry",
                        message="Pendência: Informação sobre <b>Docência do 2° semestre</b> não foi submetido.",
                    )
                else:
                    Pendency.unregister(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part="teaching_2nd_semestry",
                    )
        except Exception as e:
            log.error("Erro ao criar pendencia de submissão da docência do 2º semestre")
            raise e

    def _pendencies_submitted_property(self):
        try:
            if (
                self.check_access_criteria(Property.codename)
                and datetime.now().date() >= self.open_date_property.date()
            ):
                submitted = self.part_was_submitted(Property.codename)

                if not submitted and (
                    self.close_date_property is not None
                    and datetime.now().date() > self.close_date_property.date()
                ):
                    Pendency.register(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Property.codename,
                        message="Pendência: Informação sobre <b>Bens e Direitos</b> não foi submetido.",
                    )
                else:
                    Pendency.unregister(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Property.codename,
                    )

        except Exception as e:
            log.error("Erro ao criar pendencia de submissão de Bens e Direitos")
            raise e

    def _pendencies_submitted_debits(self):
        try:
            if (
                self.check_access_criteria(Debits.codename)
                and datetime.now().date() >= self.open_date_debits.date()
            ):
                submitted = self.part_was_submitted(Debits.codename)

                if not submitted and (
                    self.close_date_debits is not None
                    and datetime.now().date() > self.close_date_debits.date()
                ):
                    Pendency.register(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Debits.codename,
                        message="Pendência: Informação sobre <b>Dívidas e Ônus</b> não foi submetido.",
                    )
                else:
                    Pendency.unregister(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Debits.codename,
                    )

        except Exception as e:
            log.error("Erro ao criar pendencia de submissão de Dívidas e Ônus")
            raise e

    def _pendencies_submitted_irpf(self):
        try:
            if self.check_access_criteria(Irpf.codename) and (
                self.open_date_irpf
                and datetime.now().date() >= self.open_date_irpf.date()
            ):
                submitted = self.part_was_submitted(Irpf.codename)

                if not submitted and (
                    self.close_date_irpf is not None
                    and datetime.now().date() > self.close_date_irpf.date()
                ):
                    Pendency.register(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Irpf.codename,
                        message="Pendência: Informação sobre <b>IRPF</b> não foi submetido.",
                    )
                else:
                    Pendency.unregister(
                        kind=Pendency.DEADLINE,
                        control_information=self,
                        part=Irpf.codename,
                    )
        except Exception as e:
            raise e

    def _pendencies_information_address(self):
        if (
            self.check_access_criteria(Address.codename)
            and self.in_address.all()
            .filter(validate_reside_outside=False)
            .exclude(authorization_reside_outside=True)
            .exists()
        ):
            Pendency.register(
                kind=Pendency.INFORMATION,
                control_information=self,
                part=Address.codename,
                message="Conflito: <b>Endereço/Comarca</b>.",
            )
        else:
            Pendency.unregister(
                kind=Pendency.INFORMATION, control_information=self, part=Irpf.codename
            )

    def _pendencies_information_teaching_one(self):
        if (
            self.check_access_criteria("teaching_1st_semestry")
            and self.in_teaching.filter(Q(schedule__isnull=True, period=1)).exists()
        ):
            Pendency.register(
                kind=Pendency.INFORMATION,
                control_information=self,
                part="teaching_1st_semestry",
                message="Horário não informado",
            )
        else:
            Pendency.unregister(
                kind=Pendency.INFORMATION,
                control_information=self,
                part="teaching_1st_semestry",
            )

    def _pendencies_information_teaching_two(self):
        if (
            self.check_access_criteria("teaching_2nd_semestry")
            and self.in_teaching.filter(Q(schedule__isnull=True, period=2)).exists()
        ):
            Pendency.register(
                kind=Pendency.INFORMATION,
                control_information=self,
                part="teaching_2nd_semestry",
                message="Horário não informado",
            )
        else:
            Pendency.unregister(
                kind=Pendency.INFORMATION,
                control_information=self,
                part="teaching_2nd_semestry",
            )

    def _pendencies_information_irpf(self):
        if self.check_access_criteria(Irpf.codename) and self.in_irpf.first():
            invalid_file = self.in_irpf.filter(validated=False).exists()
            principal_not_exists = not self.in_irpf.filter(of_who=1).exists()

            msg = ""

            if invalid_file:
                msg = "Arquivo da declaração não é válido. "
            if principal_not_exists:
                msg = msg + "Declaracão individual não informada."

            if principal_not_exists or invalid_file:

                Pendency.register(
                    kind=Pendency.INFORMATION,
                    control_information=self,
                    part=Irpf.codename,
                    message=msg,
                )
        else:
            Pendency.unregister(
                kind=Pendency.INFORMATION, control_information=self, part=Irpf.codename
            )

    def _pendencies_submitted_check(self):
        self._pendencies_submitted_address()
        self._pendencies_submitted_teaching_one()
        self._pendencies_submitted_teaching_two()
        self._pendencies_submitted_property()
        self._pendencies_submitted_debits()
        self._pendencies_submitted_irpf()

    def _pendencies_information_check(self):
        self._pendencies_information_address()
        self._pendencies_information_teaching_one()
        self._pendencies_information_teaching_two()
        self._pendencies_information_irpf()

    def pendencies_check(self):
        self._pendencies_submitted_check()
        self._pendencies_information_check()

    def save(self, saving=True, health_area=False, *args, **kargs):
        if health_area:
            super(ControlInformation, self).save(*args, **kargs)
        else:
            creating = False
            if self.pk is None:
                creating = True
            super(ControlInformation, self).save(*args, **kargs)
            if creating is True:
                self.register_history(criteria=None, action="Criando SRDIR/DBVR")
            self.exec_schedule(saving)

    def register_history(self, criteria, action):
        history = History()
        history.controlinformation = self
        history.criteria = criteria
        history.action = action
        history.save()

    def distribute_to_evaluators(self):
        with transaction.atomic():
            Health.distribute_to_evaluators(controlinformation=self)

    @classmethod
    def create_control_information_to_employee(
        cls, employee, year=None, user=None, closed=True
    ):
        year = year if year else datetime.now().year

        try:
            if not employee:
                raise Exception("Servidor nao foi informado.")

            if cls.objects.filter(employee=employee, year=year).exists():
                log.info("SRDIR de %s já existe!" % (str(employee)))
            else:
                log.info("Criando SRDIR para %s!" % (str(employee)))

                previous_information = cls.objects.filter(
                    employee=employee, year=(year - 1)
                ).first()

                cfg = Configuration.get_or_create("corregedoria")

                def format_date_config(year, config, flag):
                    return datetime(
                        int(year),
                        int(config.get(flag).split("/")[1]),
                        int(config.get(flag).split("/")[0]),
                    )

                params = {
                    "employee": employee,
                    "year": year,
                    "previous_controlinformation_id": (
                        previous_information.pk if previous_information else None
                    ),
                    "open_date_address": format_date_config(
                        year, cfg, "var_open_date_address"
                    ),
                    "close_date_address": format_date_config(
                        year, cfg, "var_close_date_address"
                    ),
                    "open_date_teaching_1st_semestry": format_date_config(
                        year, cfg, "var_open_date_teaching_1st_semestry"
                    ),
                    "close_date_teaching_1st_semestry": format_date_config(
                        year, cfg, "var_close_date_teaching_1st_semestry"
                    ),
                    "open_date_teaching_2nd_semestry": format_date_config(
                        year, cfg, "var_open_date_teaching_2nd_semestry"
                    ),
                    "close_date_teaching_2nd_semestry": format_date_config(
                        year, cfg, "var_close_date_teaching_2nd_semestry"
                    ),
                    "open_date_property": format_date_config(
                        year, cfg, "var_open_date_property"
                    ),
                    "close_date_property": format_date_config(
                        year, cfg, "var_close_date_property"
                    ),
                    "open_date_debits": format_date_config(
                        year, cfg, "var_open_date_debits"
                    ),
                    "close_date_debits": format_date_config(
                        year, cfg, "var_close_date_debits"
                    ),
                    "open_date_health": format_date_config(
                        year, cfg, "var_open_date_health"
                    ),
                    "close_date_health": format_date_config(
                        year, cfg, "var_close_date_health"
                    ),
                    "closed_address": False,
                    "closed_teaching_1st_semestry": False,
                    "closed_teaching_2nd_semestry": False,
                    "closed_property": False,
                    "closed_debits": False,
                    "closed_irpf": False,
                    "closed_health": False,
                }

                controlinformation = ControlInformation(**params)
                controlinformation.nusubmit()

                if previous_information:
                    controlinformation.save(saving=False)

                    controlinformation.copy_address_from(previous_information)
                    controlinformation.copy_teaching_from(previous_information)
                    controlinformation.copy_property_from(previous_information)
                    controlinformation.copy_debits_from(previous_information)

                if closed:
                    controlinformation.closed_address = True
                    controlinformation.closed_teaching_1st_semestry = True
                    controlinformation.closed_teaching_2nd_semestry = True
                    controlinformation.closed_property = True
                    controlinformation.closed_debits = True
                    controlinformation.closed_health = True
                    controlinformation.closed_irpf = True
                controlinformation.save(saving=True)

        except Exception as err:
            log.exception(str(err))
            raise err

    def copy_address_from(self, previous_information):
        log.info("Copiando dados de Enderecos!")
        for data in Address.objects.filter(controlinformation=previous_information):
            previous_addr = data.pk
            data.pk = None
            data.controlinformation = self
            data.previous_address_id = previous_addr
            data.updated_at = data.modified_at
            setattr(data, "originated_from_the_copy", True)
            data.save()

    def copy_teaching_from(self, previous_information):
        log.info("Copiando dados de Docencia!")
        for data in Teaching.objects.filter(controlinformation=previous_information):
            list_schedule = data.schedule.all()
            data.pk = None
            data.controlinformation = self
            data.updated_at = data.modified_at
            setattr(data, "originated_from_the_copy", True)
            data.save()
            for schedule in list_schedule:
                data.schedule.add(schedule)

    def copy_property_from(self, previous_information):
        log.info("Copiando dados de Bens!")
        for data in Property.objects.filter(controlinformation=previous_information):
            data.pk = None
            data.controlinformation = self
            data.last_value = data.current_value
            data.updated_at = data.modified_at
            setattr(data, "originated_from_the_copy", True)
            data.save()

    def copy_debits_from(self, previous_information):
        log.info("Copiando dados de Dividas!")
        for data in Debits.objects.filter(controlinformation=previous_information):
            data.pk = None
            data.controlinformation = self
            data.last_value = data.current_value
            data.updated_at = data.modified_at
            setattr(data, "originated_from_the_copy", True)
            data.save()

    def copy_health_from(self, previous_information):
        log.info("Copiando dados de Saude!")
        for data in Health.objects.filter(controlinformation=previous_information):
            data.pk = None
            data.controlinformation = self
            data.updated_at = data.modified_at
            setattr(data, "originated_from_the_copy", True)
            data.save()

    def pre_submit_validation(self, criteria, check_empty=False):

        msg = "Você está informando que <b>{}</b>, porém há registros de {} informados nesse período."

        def teaching_1nd():
            if (
                Teaching.query_1nd_from(controlinformation=self).exists()
                and check_empty
            ):
                raise Exception(
                    msg.format("não exerce docência no primeiro semestre", "docência")
                )

        def teaching_2nd():
            if (
                Teaching.query_2nd_from(controlinformation=self).exists()
                and check_empty
            ):
                raise Exception(
                    msg.format("não exerce docência no segundo semestre", "docência")
                )

        def property():
            if (
                Property.query_property_from(controlinformation=self).exists()
                and check_empty
            ):
                raise Exception(
                    msg.format("não possui Bens e Direitos", "Bens e Direitos")
                )

        def debits():
            if (
                Debits.query_debits_from(controlinformation=self).exists()
                and check_empty
            ):
                raise Exception(
                    msg.format(
                        "não possui Dívidas e Ônus Reais", "Dívidas e Ônus Reais"
                    )
                )

        options = {
            "teaching_1nd_semestry": teaching_1nd,
            "teaching_2nd_semestry": teaching_2nd,
            "property": property,
            "debits": debits,
        }

        options.get(criteria, lambda: None)()

    def has_perm_to(self, user=None, apply_to=None):

        if user.has_perm("cirdir.can_management_member") and apply_to == "M":
            return True
        elif user.has_perm("cirdir.can_management_employee") and apply_to == "S":
            return True

        return False

    def delete(self, *args, **kwargs):

        commit = False

        if (
            self.has_perm_to(user=get_current_user(), apply_to="M")
            and self.employee.tipo == "M"
        ):
            commit = True

        if (
            self.has_perm_to(user=get_current_user(), apply_to="S")
            and self.employee.tipo == "S"
        ):
            commit = True

        if commit:
            self.hidden = True
            self.save(saving=False)
        else:
            raise Exception("Você não possui permissão para realizar essa ação.")

    @classmethod
    def _mount_queryset_criteria(cls, criteria_list=[]):

        query_q = {
            "address": lambda: Q(address_submitted_by=None),
            "teaching": lambda: Q(
                Q(teaching_1st_semestry_submitted_by=None)
                | Q(teaching_2nd_semestry_submitted_by=None)
            ),
            "debits": lambda: Q(debits_submitted_by=None),
            "property": lambda: Q(property_submitted_by=None),
        }

        options = []

        for i in criteria_list:
            for j in query_q.keys():
                if j in i:
                    options.append(j)

        query = Q()

        for c in options:
            query = query | query_q.get(c)()

        return query

    @classmethod
    def get_all_controlinformation_not_submitted(cls, employee=None):

        criteria_list = cls.list_access_criteria_from_employee(employee=employee)
        query = cls._mount_queryset_criteria(criteria_list=criteria_list)

        return cls.objects.exclude(hidden=True).filter(query).filter(employee=employee)

    @classmethod
    def list_access_criteria_from_employee(cls, employee=None):
        cfg = Configuration.get_or_create("corregedoria")
        criteria_list = []
        if employee:
            if employee.type_by_possession in cfg.get("autoCreateForTypeEmployee"):
                criteria_list = cls.list_access_criteria_from_type_employee(kind=["S"])
            elif employee.type_by_possession in cfg.get("autoCreateForTypeMember"):
                criteria_list = cls.list_access_criteria_from_type_employee(kind=["M"])

        return criteria_list

    @classmethod
    def list_access_criteria_from_type_employee(cls, kind=[]):
        criteria = []

        if kind:
            cfg = Configuration.get_or_create("corregedoria")
            query = Q()
            if "M" in kind:
                query = Q(key__icontains="var_member")

            if "S" in kind:
                query = query | Q(key__icontains="var_employee")

            for item in cfg.items.filter(query):
                if int(item.value) == 1:
                    criteria.append(item.key)

        return criteria

    @property
    def get_close_date_address(self):
        return self.close_date_address

    @property
    def get_close_date_teaching_one(self):
        return self.close_date_teaching_1st_semestry

    @property
    def get_close_date_teaching_two(self):
        return self.close_date_teaching_2nd_semestry

    @property
    def get_close_date_property(self):
        return self.close_date_property

    @property
    def get_close_date_debits(self):
        return self.close_date_debits

    @property
    def get_close_date_health(self):
        return self.close_date_health

    @property
    def get_close_date_irpf(self):
        return self.close_date_irpf

    @classmethod
    def can_change_instance(cls, instance=None):
        try:
            current_user = get_current_user()
            if current_user and instance:
                to_user = instance.employee.user
                if current_user.pk == to_user.pk:
                    return True
                else:
                    return current_user.has_perm("cirdir.super_administrator")
            else:
                return False
        except Exception as e:
            return False

    @classmethod
    def can_create_year(cls):
        current_user = get_current_user()
        if current_user:
            return current_user.has_perm("cirdir.super_administrator")
        else:
            return False

    @classmethod
    def query_all_only_open(cls):
        query = Q(
            Q(closed_health=False)
            | Q(closed_debits=False)
            | Q(closed_property=False)
            | Q(closed_address=False)
            | Q(closed_teaching_1st_semestry=False)
            | Q(closed_teaching_2nd_semestry=False)
        )
        return cls.objects.filter(hidden=False).filter(query).distinct()

    @classmethod
    def get_default_config_date(cls, year=None):
        year = year if year else datetime.now().year
        cfg = Configuration.get_or_create("corregedoria")

        def format_date_config(year, config, flag):
            return datetime(
                int(year),
                int(config.get(flag).split("/")[1]),
                int(config.get(flag).split("/")[0]),
            )

        resp = {
            "open_date_address": format_date_config(year, cfg, "var_open_date_address"),
            "close_date_address": format_date_config(
                year, cfg, "var_close_date_address"
            ),
            "open_date_teaching_1st_semestry": format_date_config(
                year, cfg, "var_open_date_teaching_1st_semestry"
            ),
            "close_date_teaching_1st_semestry": format_date_config(
                year, cfg, "var_close_date_teaching_1st_semestry"
            ),
            "open_date_teaching_2nd_semestry": format_date_config(
                year, cfg, "var_open_date_teaching_2nd_semestry"
            ),
            "close_date_teaching_2nd_semestry": format_date_config(
                year, cfg, "var_close_date_teaching_2nd_semestry"
            ),
            "open_date_property": format_date_config(
                year, cfg, "var_open_date_property"
            ),
            "close_date_property": format_date_config(
                year, cfg, "var_close_date_property"
            ),
            "open_date_debits": format_date_config(year, cfg, "var_open_date_debits"),
            "close_date_debits": format_date_config(year, cfg, "var_close_date_debits"),
            "open_date_health": format_date_config(year, cfg, "var_open_date_health"),
            "close_date_health": format_date_config(year, cfg, "var_close_date_health"),
        }

        # isso nao eh certo, deve haver uma gestao personalizada para cada ano.
        ## FIXME:
        if int(year) == 2021:
            resp.update({"close_date_address": datetime(2021, 3, 19)})
            resp.update({"close_date_teaching_1st_semestry": datetime(2021, 3, 19)})
            resp.update({"close_date_property": datetime(2021, 6, 30)})
            resp.update({"close_date_debits": datetime(2021, 6, 30)})

        if int(year) == 2020:
            resp.update({"close_date_property": datetime(2020, 7, 15)})
            resp.update({"close_date_debits": datetime(2020, 7, 15)})

        return resp

    @classmethod
    def get_debits_submitted_after_deadline(
        cls, year=None, employee_kind=None, deadline=None
    ):
        if deadline is None:
            conf = cls.get_default_config_date(year=year)
            deadline = conf.get("close_date_debits")
        deadline = deadline.replace(hour=23, minute=59, second=59)
        return cls.objects.filter(year=year, employee__tipo=employee_kind).filter(
            debits_submitted_at__gt=deadline
        )

    @classmethod
    def get_property_submitted_after_deadline(
        cls, year=None, employee_kind=None, deadline=None
    ):
        if deadline is None:
            conf = cls.get_default_config_date(year=year)
            deadline = conf.get("close_date_property")
        deadline = deadline.replace(hour=23, minute=59, second=59)
        return cls.objects.filter(year=year, employee__tipo=employee_kind).filter(
            property_submitted_at__gt=deadline
        )

    @classmethod
    def get_address_submitted_after_deadline(
        cls, year=None, employee_kind=None, deadline=None
    ):
        if deadline is None:
            conf = cls.get_default_config_date(year=year)
            deadline = conf.get("close_date_address")
        deadline = deadline.replace(hour=23, minute=59, second=59)
        return cls.objects.filter(year=year, employee__tipo=employee_kind).filter(
            address_submitted_at__gt=deadline
        )

    @classmethod
    def get_teaching_one_submitted_after_deadline(
        cls, year=None, employee_kind=None, deadline=None
    ):
        if deadline is None:
            conf = cls.get_default_config_date(year=year)
            deadline = conf.get("close_date_teaching_1st_semestry")
        deadline = deadline.replace(hour=23, minute=59, second=59)
        return cls.objects.filter(year=year, employee__tipo=employee_kind).filter(
            teaching_1st_semestry_submitted_at__gt=deadline
        )

    @classmethod
    def get_teaching_two_submitted_after_deadline(
        cls, year=None, employee_kind=None, deadline=None
    ):
        if deadline is None:
            conf = cls.get_default_config_date(year=year)
            deadline = conf.get("close_date_teaching_2nd_semestry")
        deadline = deadline.replace(hour=23, minute=59, second=59)
        return cls.objects.filter(year=year, employee__tipo=employee_kind).filter(
            teaching_2nd_semestry_submitted_at__gt=deadline
        )

    @property
    def status_irpf_template(self):
        irpf = self.in_irpf.first()

        return {
            "is_closed": self.closed_irpf,
            "submitted_by": irpf.created_by if irpf else None,
            "submitted_at": irpf.created_at if irpf else None,
            "status": self.irpf_status,
        }

    def submit_status_part_rendered(self, codename):
        try:
            return self.in_submit_status.get(part=codename).rendered
        except Exception:
            return "Não foi possível carregar algumas informações"


class Part(AuditTimestampModel):

    class Meta:
        abstract = True

    controlinformation = models.ForeignKey(
        ControlInformation, related_name="in_%(class)s", on_delete=models.PROTECT
    )

    @property
    def codename(self):
        return ""

    @property
    def is_auditable(self):
        return False

    @property
    def rendered(self):
        return ""

    def __str__(self) -> str:
        return f"{self.controlinformation.employee}"


class Address(Part):
    """
    Cadastro de enderecos de residencia
    """

    previous_address = models.ForeignKey(
        "Address", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    ref_address = models.ForeignKey(
        Endereco, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    start_date = models.DateField(
        null=True,
        blank=True,
    )
    end_date = models.DateField(
        null=True,
        blank=True,
    )
    authorization_reside_outside = models.BooleanField(default=False)
    type_residence = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "TYPE_RESIDENCE"),
    )
    validate_reside_outside = models.BooleanField(null=True, blank=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    codename = "address"

    class Meta:
        verbose_name = "Cadastro de endereços de residência"

    @property
    def is_auditable(self):
        return True if self.authorization_reside_outside else False

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        status = []
        if self.is_updated:
            status.append(
                {"title": "Atualizado", "iconCls": "icon-core icon-core-success"}
            )
        else:
            status.append(
                {"title": "Desatualizado", "iconCls": "icon-core icon-core-error"}
            )

        return status

    @property
    def is_updated(self):
        if self.updated_at < self.controlinformation.created_at:
            return False
        else:
            return True

    @property
    def rendered(self):
        tpl = loader.get_template("address.html")
        return tpl.render({"address": self})

    def confirm_information(self):
        self.save()

    def valide_reside_outside(self, *args, **kargs):
        municipios = []
        proviment = self.controlinformation.employee.posses_ativas.last().quadro.cargo
        if proviment:
            for l in self.controlinformation.employee._raw_locations(
                date=datetime.now()
            ).filter(
                lotacao=proviment.lotacao_responsavel, designacao=True, ativo=True
            ):
                for c in l.lotacao.localidade.counties.all():
                    for local in c.locations.all():
                        if local.pk not in municipios:
                            municipios.append(local.pk)
            if (
                self.controlinformation.employee._raw_locations(date=datetime.now())
                .filter(
                    lotacao__executionorgan__isnull=False, designacao=True, ativo=True
                )
                .exists()
            ):
                for l in self.controlinformation.employee._raw_locations(
                    date=datetime.now()
                ).filter(
                    lotacao__executionorgan__isnull=False, designacao=True, ativo=True
                ):
                    for c in l.lotacao.localidade.counties.all():
                        for local in c.locations.all():
                            if local.pk not in municipios:
                                municipios.append(local.pk)
            else:
                if (
                    self.controlinformation.employee._raw_locations(date=datetime.now())
                    .filter(designacao=True, ativo=True)
                    .exists()
                ):
                    for l in self.controlinformation.employee._raw_locations(
                        date=datetime.now()
                    ).filter(designacao=True, ativo=True):
                        for c in l.lotacao.localidade.counties.all():
                            for local in c.locations.all():
                                if local.pk not in municipios:
                                    municipios.append(local.pk)
                else:
                    if proviment.lotacao_responsavel:
                        if proviment.lotacao_responsavel.localidade:
                            for (
                                c
                            ) in (
                                proviment.lotacao_responsavel.localidade.counties.all()
                            ):
                                for local in c.locations.all():
                                    if local.pk not in municipios:
                                        municipios.append(local.pk)

        if self.ref_address.municipio:
            reside_outside = (
                True if self.ref_address.municipio.pk in municipios else False
            )
        else:
            reside_outside = False
        return reside_outside

    def save(self, *args, **kargs):
        creating = False
        if self.pk is None:
            creating = True

        if self.controlinformation.in_address.exclude(pk=self.pk).exists():
            raise Exception("Mais de um endereço informado. Informe apenas um.")

        if self.start_date is None:
            raise Exception("Informe a data de Início da residência. ")

        if not getattr(self, "originated_from_the_copy", False):
            self.updated_at = datetime.now()

        self.validate_reside_outside = self.valide_reside_outside()

        if self.controlinformation.closed_address:
            raise Exception(
                "Não permitida a alteração nos dados de Residência. Fechado para alteração."
            )
        else:
            if (
                ControlInformation.can_change_instance(instance=self.controlinformation)
                is False
            ):
                raise Exception(
                    "Você não possui permissão para realizar essa operação."
                )

            super(Address, self).save(*args, **kargs)
            if creating:
                self.controlinformation.register_history(
                    criteria=Category.address.value,
                    action="Adicionada nova informação de residência. [COD: %s]"
                    % self.pk,
                )
            else:
                self.controlinformation.register_history(
                    criteria=Category.address.value,
                    action="Alterada informação de residência. [COD: %s]" % self.pk,
                )
            self.controlinformation.nusubmit("address")
            self.controlinformation.save(saving=False)

    def delete(self, *args, **kargs):
        if self.controlinformation.closed_address:
            raise Exception(
                "Não permitida a alteração nos dados de Residência. Fechado para alteração."
            )
        else:
            if (
                ControlInformation.can_change_instance(instance=self.controlinformation)
                is False
            ):
                raise Exception(
                    "Você não possui permissão para realizar essa operação."
                )
            self.controlinformation.register_history(
                criteria=Category.address.value,
                action="Removida informação de residência. [%s]" % self.ref_address,
            )
            super(Address, self).delete(*args, **kargs)
            self.controlinformation.nusubmit("address")
            self.controlinformation.save(saving=False)


class Institution(PessoaJuridica):
    """
    Cadastro das Instituicoes de Ensino
    """

    county = models.ForeignKey(
        Localidade, related_name="+", null=True, blank=False, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Cadastro das Instituições de Ensino"

    def save(self, *args, **kwargs):
        if self.pk and Teaching.objects.filter(institution=self.pk).exists():
            raise Exception(
                "Alteração não permitida. Instituição Vinculada a um ou mais registros de docência."
            )
        super(Institution, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if Teaching.objects.filter(institution=self.pk).exists():
            raise Exception(
                "Remoção não permitida. Instituição vinculada a um ou mais registros de docência."
            )
        super(Institution, self).delete(*args, **kwargs)


class Discipline(AuditTimestampModel):
    """
    Cadastro das Disciplinas
    """

    name = models.TextField(unique=True)

    class Meta:
        verbose_name = "Cadastro das Disciplinas"

    def __str__(self):
        return "%s" % (self.name)

    def save(self, *args, **kwargs):
        if self.pk and Teaching.objects.filter(discipline=self.pk).exists():
            raise Exception(
                "Alteração não permitida. Disciplina Vinculada a um ou mais registros de docência."
            )
        super(Discipline, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if Teaching.objects.filter(discipline=self.pk).exists():
            raise Exception(
                "Remoção não permitida. Disciplina vinculada a um ou mais registros de docência."
            )
        super(Discipline, self).delete(*args, **kwargs)


class Schedule(AuditTimestampModel):
    """
    Cadastro dos horarios de docencia
    """

    day_week = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "DAY_WEEK"),
    )
    date_module = models.DateField(
        null=True,
        blank=True,
    )
    start_time = models.CharField(max_length=8, null=True, blank=True)
    end_time = models.CharField(max_length=8, null=True, blank=True)
    type_schedule = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=Choice.get_choices_for("cirdir", "TYPE_SCHEDULE"),
    )

    class Meta:
        verbose_name = "Cadastro dos horários de docência"

    def __str__(self):
        return "%s | %s (%s - %s)" % (
            self.get_type_schedule_display(),
            (
                self.date_module.strftime("%d/%m/%Y")
                if self.date_module
                else self.get_day_week_display()
            ),
            self.start_time,
            self.end_time,
        )

    @property
    def get_schedule_time(self):
        return "%s (%s - %s); " % (
            (
                self.date_module.strftime("%d/%m/%Y")
                if self.date_module
                else self.get_day_week_display()
            ),
            self.start_time,
            self.end_time,
        )

    def regex_date(self, value):
        regex = "^(?:[01]\d|2[0-3]):(?:[0-5]\d):(?:[0-5]\d)$"
        result = re.search(regex, value)
        return result

    def validation(self):
        error = False
        msg_error = "Os seguintes campos não foram preenchidos corretamente:"

        if self.type_schedule is None:
            error = True
            msg_error += "<br />-<b>TIPO</b>"

        if self.day_week is None and self.type_schedule == 1:
            error = True
            msg_error += "<br />-<b>DIA DA SEMANA</b>"

        if self.date_module is None and self.type_schedule == 2:
            error = True
            msg_error += "<br />-<b>DATA</b>"

        if self.regex_date(self.start_time) is None:
            error = True
            msg_error += "<br />-<b>HORÁRIO DE INÍCIO</b>"

        if self.regex_date(self.end_time) is None:
            error = True
            msg_error += "<br />-<b>HORÁRIO DE TÉRMINO</b>"

        if error:
            raise Exception(msg_error)

    def save(self, *args, **kwargs):
        if self.pk and self.in_teaching.exists():
            raise Exception(
                "Alteração não permitida. Horário vinculado a uma ou mais docência."
            )
        self.validation()

        super(Schedule, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.in_teaching.exists():
            raise Exception(
                "Remoção não permitida. Horário vinculado a uma ou mais docência."
            )
        super(Schedule, self).delete(*args, **kwargs)


class Teaching(Part):
    """
    Registro de docencias no periodo
    """

    institution = models.ForeignKey(
        Institution, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    discipline = models.ForeignKey(
        Discipline, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    schedule = models.ManyToManyField(Schedule, related_name="teachings")
    work_hours = models.SmallIntegerField(default="0", null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    authorization_teaching = models.BooleanField(default=True)
    period = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "PERIOD"),
    )
    modality = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "MODALITY"),
    )
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Registro de docências no período"

    @property
    def codename(self):
        if self.period == 1:
            return "teaching_1st_semestry"
        elif self.period == 2:
            return "teaching_2nd_semestry"
        else:
            return super().codename

    @property
    def is_auditable(self):
        return True if self.authorization_teaching else False

    @property
    def get_schedules_time(self):
        rst = ""
        for s in self.schedule.all():
            rst += s.get_schedule_time
        return rst

    @property
    def rendered(self):
        tpl = loader.get_template("teaching.html")
        return tpl.render({"teaching": self})

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        status = []
        if self.is_updated:
            status.append(
                {"title": "Atualizado", "iconCls": "icon-core icon-core-success"}
            )
        else:
            status.append(
                {"title": "Desatualizado", "iconCls": "icon-core icon-core-error"}
            )

        return status

    @property
    def is_updated(self):
        if self.updated_at < self.controlinformation.created_at:
            return False
        else:
            return True

    def validate_form(self):
        if not self.discipline:
            raise Exception("Informe a disciplina.")
        if not self.modality:
            raise Exception("Informe a modalidade.")
        if not self.institution:
            raise Exception("Informe a Instituição de Ensino.")
        if not (self.start_date and self.end_date):
            raise Exception("Data de início ou data de término não informada.")

    def confirm_information(self):
        self.save()

    def save(self, *args, **kargs):

        self.validate_form()
        creating = True if self.pk is None else False

        if self.start_date.year != self.controlinformation.year:
            raise Exception(
                "Verifique a data de início da docência. O ano informado não corresponde ao ano base."
            )

        if self.end_date.year != self.controlinformation.year:
            raise Exception(
                "Verifique a data de término da docência. O ano informado não corresponde ao ano base."
            )

        _1st_semestry = self.start_date.replace(
            month=1, day=1
        ), self.start_date.replace(month=6, day=30)

        self.period = (
            1 if _1st_semestry[0] <= self.start_date <= _1st_semestry[1] else 2
        )

        if not getattr(self, "originated_from_the_copy", False):
            self.updated_at = datetime.now()

        if self.controlinformation.closed_teaching_1st_semestry and self.period == 1:
            raise Exception(
                "Não permitida a alteração nos dados de Docência (1º Semestre). Fechado para alteração."
            )
        if self.controlinformation.closed_teaching_2nd_semestry and self.period == 2:
            raise Exception(
                "Não permitida a alteração nos dados de Docência (2º Semestre). Fechado para alteração."
            )

        if creating is False and self.schedule.count() == 0:
            raise Exception(
                "Não é possível salvar a informações de docência.<br />Especifique os horários de docência."
            )

        if (
            ControlInformation.can_change_instance(instance=self.controlinformation)
            is False
        ):
            raise Exception("Você não possui permissão para realizar essa operação.")

        super(Teaching, self).save(*args, **kargs)

        msg_log = ""
        if creating:
            msg_log = "Adicionada nova informação de docência. [COD: {}]".format(
                self.pk
            )
        else:
            msg_log = "Alterada informação de docência. [COD: {}]".format(self.pk)

        self.controlinformation.register_history(
            criteria=Category.teaching.value, action=msg_log
        )
        self.controlinformation.nusubmit(
            "teaching_1st_semestry" if self.period == 1 else "teaching_2nd_semestry"
        )
        self.controlinformation.save(saving=False)

    def delete(self, *args, **kargs):

        if (
            self.controlinformation.closed_teaching_1st_semestry
            and self.period == 1
            and self.is_updated
        ):
            raise Exception(
                "Não permitida a alteração nos dados de Docência (1º Semestre). Fechado para alteração."
            )

        if (
            self.controlinformation.closed_teaching_2nd_semestry
            and self.period == 2
            and self.is_updated
        ):
            raise Exception(
                "Não permitida a alteração nos dados de Docência (2º Semestre). Fechado para alteração."
            )

        if (
            ControlInformation.can_change_instance(instance=self.controlinformation)
            is False
        ):
            raise Exception("Você não possui permissão para realizar essa operação.")

        self.controlinformation.nusubmit(
            "teaching_1st_semestry" if self.period == 1 else "teaching_2nd_semestry"
        )
        self.controlinformation.save(saving=False)

        self.controlinformation.register_history(
            criteria=Category.teaching.value,
            action="Removida informação de docência. [%s | %s | %s]"
            % (self.institution, self.discipline, self.get_period_display()),
        )
        super(Teaching, self).delete(*args, **kargs)

    @classmethod
    def query_2nd_from(cls, controlinformation=None):
        initial_date = datetime(controlinformation.year, 7, 1)
        final_date = datetime(controlinformation.year, 12, 31)
        return cls.objects.filter(controlinformation=controlinformation).filter(
            start_date__gte=initial_date, end_date__lte=final_date
        )

    @classmethod
    def query_1nd_from(cls, controlinformation=None):
        initial_date = datetime(controlinformation.year, 1, 1)
        final_date = datetime(controlinformation.year, 6, 30)
        return cls.objects.filter(controlinformation=controlinformation).filter(
            start_date__gte=initial_date, end_date__lte=final_date
        )

    def validate_exercises_teaching(self):
        is_valid = self.is_updated
        return is_valid


class IRSCode(AuditTimestampModel):
    """
    Codigo de classificacao da Receita Federal
    """

    code = models.SmallIntegerField(default="0", null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    type_irscode = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "TYPE_IRSCODE"),
    )

    class Meta:
        verbose_name = "Código de classificação da Receita Federal"
        ordering = ["type_irscode", "code"]

    def __str__(self):
        return "%s - %s" % (self.code, self.title)


class Property(Part):
    """
    Regristo de Bens, Rendas e Valores
    """

    # controlinformation = models.ForeignKey(ControlInformation, related_name='properties', on_delete=models.PROTECT)
    irscode = models.ForeignKey(
        IRSCode, null=True, blank=True, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    country = models.ForeignKey(
        Pais, null=True, blank=True, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.TextField(null=True, blank=True)
    kind = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "KIND"),
    )
    last_value = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, default=0
    )
    current_value = models.DecimalField(max_digits=18, decimal_places=2)
    updated_at = models.DateTimeField(blank=True, null=True)

    codename = "property"

    class Meta:
        verbose_name = "Regirsto de Bens, Rendas e Valores"

    @property
    def rendered(self):
        tpl = loader.get_template("property.html")
        return tpl.render({"property": self})

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        status = []
        if self.is_updated:
            status.append(
                {"title": "Atualizado", "iconCls": "icon-core icon-core-success"}
            )
        else:
            status.append(
                {"title": "Desatualizado", "iconCls": "icon-core icon-core-error"}
            )

        return status

    @property
    def is_updated(self):
        if self.updated_at < self.controlinformation.created_at:
            return False
        else:
            return True

    def confirm_information(self):
        self.save()

    def save(self, *args, **kargs):
        if self.kind is None:
            raise Exception("O campo <b>TIPO</b> deve ser preenchido.")
        if self.irscode is None:
            raise Exception("O campo <b>CLASSIFICAÇÃO</b> deve ser preenchido.")
        if self.description == "":
            raise Exception("O campo <b>DESCRIÇÃO</b> deve ser preenchido.")
        if self.current_value is None:
            raise Exception("O campo <b>VALOR</b> deve ser preenchido.")
        if self.country is None:
            raise Exception("O campo <b>PAÍS</b> deve ser preenchido.")
        creating = False
        if self.pk is None:
            creating = True
        if not getattr(self, "originated_from_the_copy", False):
            self.updated_at = datetime.now()
        if self.controlinformation.closed_property:
            raise Exception(
                "Não permitida a alteração nos dados de Bens e Direitos. Fechado para alteração."
            )
        else:
            if (
                ControlInformation.can_change_instance(instance=self.controlinformation)
                is False
            ):
                raise Exception(
                    "Você não possui permissão para realizar essa operação."
                )

            super(Property, self).save(*args, **kargs)
            if creating:
                self.controlinformation.register_history(
                    criteria=Category.property.value,
                    action="Adicionada nova informação de Bens e Direitos. [COD: %s]"
                    % self.pk,
                )
            else:
                self.controlinformation.register_history(
                    criteria=Category.property.value,
                    action="Alterada informação de Bens e Direitos. [COD: %s]"
                    % self.pk,
                )
            self.controlinformation.nusubmit("property")
            self.controlinformation.save(saving=False)

    def delete(self, *args, **kargs):
        if self.controlinformation.closed_property:
            raise Exception(
                "Não permitida a alteração nos dados de Bens e Direitos. Fechado para alteração."
            )
        else:
            if (
                ControlInformation.can_change_instance(instance=self.controlinformation)
                is False
            ):
                raise Exception(
                    "Você não possui permissão para realizar essa operação."
                )
            self.controlinformation.register_history(
                criteria=Category.property.value,
                action="Removida informação de Bens e Direitos. [%s]"
                % self.description,
            )
            super(Property, self).delete(*args, **kargs)
            self.controlinformation.nusubmit("property")
            self.controlinformation.save(saving=False)

    @classmethod
    def query_property_from(cls, controlinformation=None):
        initial_date = datetime(controlinformation.year, 1, 1)
        final_date = datetime(controlinformation.year, 6, 30)
        return cls.objects.filter(controlinformation=controlinformation)


class Debits(Part):
    """
    Registro de Dividas e Onus em Reis
    """

    # controlinformation = models.ForeignKey(ControlInformation, related_name='debitss', on_delete=models.PROTECT)
    irscode = models.ForeignKey(
        IRSCode, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.TextField(null=True, blank=True)
    kind = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "KIND"),
    )
    last_value = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, default=0
    )
    current_value = models.DecimalField(max_digits=18, decimal_places=2)
    updated_at = models.DateTimeField(blank=True, null=True)

    codename = "debits"

    class Meta:
        verbose_name = "Registros de Dívidas e Ônus em Reais"

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        status = []
        if self.is_updated:
            status.append(
                {"title": "Atualizado", "iconCls": "icon-core icon-core-success"}
            )
        else:
            status.append(
                {"title": "Desatualizado", "iconCls": "icon-core icon-core-error"}
            )

        return status

    @property
    def is_updated(self):
        if self.updated_at < self.controlinformation.created_at:
            return False
        else:
            return True

    @property
    def rendered(self):
        tpl = loader.get_template("debits.html")
        return tpl.render({"debits": self})

    def confirm_information(self):
        self.save()

    def save(self, *args, **kargs):
        if self.kind is None:
            raise Exception("O campo <b>TIPO</b> deve ser preenchido.")
        if self.irscode is None:
            raise Exception("O campo <b>CLASSIFICAÇÃO</b> deve ser preenchido.")
        if self.description == "":
            raise Exception("O campo <b>DESCRIÇÃO</b> deve ser preenchido.")
        if self.current_value is None:
            raise Exception("O campo <b>VALOR</b> deve ser preenchido.")
        creating = False
        if self.pk is None:
            creating = True
        if not getattr(self, "originated_from_the_copy", False):
            self.updated_at = datetime.now()
        if self.controlinformation.closed_debits:
            raise Exception(
                "Não permitida a alteração nos dados de Dívidas e Ônus Reais. Fechado para alteração."
            )
        else:
            if (
                ControlInformation.can_change_instance(instance=self.controlinformation)
                is False
            ):
                raise Exception(
                    "Você não possui permissão para realizar essa operação."
                )
            super(Debits, self).save(*args, **kargs)
            if creating:
                self.controlinformation.register_history(
                    criteria=Category.debits.value,
                    action="Adicionada nova informação de Dívidas e Ônus Reais. [COD: %s]"
                    % self.pk,
                )
            else:
                self.controlinformation.register_history(
                    criteria=Category.debits.value,
                    action="Alterada informação de Dívidas e Ônus Reais. [COD: %s]"
                    % self.pk,
                )
            self.controlinformation.nusubmit("debits")
            self.controlinformation.save(saving=False)

    def delete(self, *args, **kargs):
        if self.controlinformation.closed_property:
            raise Exception(
                "Não permitida a alteração nos dados de Dívidas e Ônus Reais. Fechado para alteração."
            )
        else:
            if (
                ControlInformation.can_change_instance(instance=self.controlinformation)
                is False
            ):
                raise Exception(
                    "Você não possui permissão para realizar essa operação."
                )
            self.controlinformation.register_history(
                criteria=Category.debits.value,
                action="Removida informação de Dívidas e Ônus Reais. [%s]"
                % self.description,
            )
            super(Debits, self).delete(*args, **kargs)
            self.controlinformation.nusubmit("debits")
            self.controlinformation.save(saving=False)

    @classmethod
    def query_debits_from(cls, controlinformation=None):
        return cls.objects.filter(controlinformation=controlinformation)


class Evaluator(AuditTimestampModel):
    """
    Cadastro de Avaliadores
    """

    employee = models.OneToOneField(
        Servidor, on_delete=models.PROTECT, related_name="in_evaluator"
    )
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cadastro de Avaliadores"
        ordering = ["-enabled", "created_at"]

    def __str__(self):
        return "{}".format(self.employee)

    @classmethod
    def query_to_delivery(cls, instance):
        return cls.objects.exclude(health_assessments__health=instance).filter(
            enabled=True, employee__user__isnull=False
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        status = []
        if self.enabled:
            status.append(
                {"title": "Habilitado", "iconCls": "icon-core icon-core-success"}
            )
        else:
            status.append(
                {"title": "Desabilitado", "iconCls": "icon-core icon-core-error"}
            )
        return status

    def delete(self, *args, **kwargs):
        if self.health_assessments.exists():
            raise Exception(
                "Não é possível remover o avaliador, pois existem avaliações vinculadas a ele."
            )
        else:
            self.change_permission(action="remove")
            super(Evaluator, self).delete(*args, **kwargs)

    def change_permission(self, action="empty"):
        try:

            cfg = Configuration.get_or_create("corregedoria")
            group = Group.objects.get(
                pk=int(cfg.get("evaluator_health_group_permission", 0))
            )
            controller = ControllerPermission.objects.get(
                pk=int(cfg.get("evaluator_health_group_menu", 0))
            )

            def add():
                if not self.employee.user.groups.filter(pk=group.pk).exists():
                    self.employee.user.groups.add(group)

                if not self.employee.user.controllerpermission_set.filter(
                    pk=controller.pk
                ).exists():
                    self.employee.user.controllerpermission_set.add(controller)

            def remove():
                if self.employee.user.groups.filter(pk=group.pk).exists():
                    self.employee.user.groups.remove(group)

                if self.employee.user.controllerpermission_set.filter(
                    pk=controller.pk
                ).exists():
                    self.employee.user.controllerpermission_set.remove(controller)

            def empty():
                raise Exception("Erro ao atribuir/remover permissão ao avaliador.")

            resp = {"add": add, "remove": remove, "empty": empty}.get(action, "empty")()

        except Exception as e:
            raise e

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old = self.__class__.objects.get(pk=self.pk)
            if old.employee != self.employee:
                raise Exception("Operação não permitida.")

            if (
                self.enabled is False
                and self.health_assessments.filter(signed_at__isnull=True).exists()
            ):
                raise Exception(
                    "O avaliador possui Avaliações pendentes. Não é possível desabilita-lo."
                )

        if self.employee.user is None:
            raise Exception("O Avaliador não possui usuário para acessar o athenas.")

        action = "add" if self.enabled else "remove"
        self.change_permission(action=action)

        super(Evaluator, self).save(*args, **kwargs)


class Health(AuditTimestampModel):
    """
    Registro das Informacoes de Saude
    """

    controlinformation = models.ForeignKey(
        ControlInformation, related_name="healths", on_delete=models.PROTECT
    )
    location = models.ManyToManyField(
        Lotacao, related_name="srdir_health_locations", blank=True
    )
    physical_exam_blood_pressure = models.CharField(
        max_length=50, null=True, blank=True
    )
    physical_exam_imc = models.CharField(max_length=50, null=True, blank=True)
    physical_exam_abdominal_circumference = models.CharField(
        max_length=50, null=True, blank=True
    )
    physical_exam_pulse = models.CharField(max_length=50, null=True, blank=True)
    physical_exam_other = models.TextField(null=True, blank=True)
    ingestion_candy = models.CharField(max_length=50, null=True, blank=True)
    ingestion_pasta = models.CharField(max_length=50, null=True, blank=True)
    ingestion_fruit = models.CharField(max_length=50, null=True, blank=True)
    ingestion_vegetable = models.CharField(max_length=50, null=True, blank=True)
    ingestion_beef = models.CharField(max_length=50, null=True, blank=True)
    ingestion_fry = models.CharField(max_length=50, null=True, blank=True)
    ingestion_supplement = models.CharField(max_length=50, null=True, blank=True)
    family_health_problems = models.CharField(max_length=50, null=True, blank=True)
    family_health_problems_other = models.TextField(null=True, blank=True)
    health_problems = models.CharField(max_length=50, null=True, blank=True)
    health_problems_other = models.TextField(null=True, blank=True)
    life_habits = models.CharField(max_length=50, null=True, blank=True)
    life_habits_other = models.TextField(null=True, blank=True)
    immunization = models.CharField(max_length=50, null=True, blank=True)
    medicament = models.CharField(max_length=50, null=True, blank=True)
    medicament_other = models.TextField(null=True, blank=True)
    physical_activity = models.CharField(max_length=50, null=True, blank=True)
    has_pain = models.CharField(max_length=50, null=True, blank=True)
    local_pain = models.CharField(max_length=50, null=True, blank=True)
    local_pain_other = models.TextField(null=True, blank=True)
    strength_at_work = models.CharField(max_length=50, null=True, blank=True)
    work_chair_seat_adjustment = models.CharField(max_length=50, null=True, blank=True)
    work_chair_height_adjustment = models.CharField(
        max_length=50, null=True, blank=True
    )
    work_chair_tilt_adjustment = models.CharField(max_length=50, null=True, blank=True)
    work_chair_has_rod = models.CharField(max_length=50, null=True, blank=True)
    work_chair_foot_support = models.CharField(max_length=50, null=True, blank=True)
    work_chair_regulates_when_sitting = models.CharField(
        max_length=50, null=True, blank=True
    )
    work_chair_supports_back = models.CharField(max_length=50, null=True, blank=True)
    work_chair_use_rods = models.CharField(max_length=50, null=True, blank=True)
    uses_2_screens = models.CharField(max_length=50, null=True, blank=True)
    pause_for_rest = models.CharField(max_length=50, null=True, blank=True)
    sitting_time = models.CharField(max_length=50, null=True, blank=True)
    dental_evaluation = models.CharField(max_length=50, null=True, blank=True)
    medical_consultation = models.CharField(max_length=50, null=True, blank=True)
    medical_consultation_specialty = models.TextField(null=True, blank=True)
    conducted_examinations = models.CharField(max_length=50, null=True, blank=True)
    conducted_examinations_which = models.TextField(null=True, blank=True)
    medical_license_higher_3_days_last_2_years = models.CharField(
        max_length=50, null=True, blank=True
    )
    medical_license_less_3_days_last_year = models.CharField(
        max_length=50, null=True, blank=True
    )
    medical_license_family_support = models.CharField(
        max_length=50, null=True, blank=True
    )
    job_satisfaction = models.CharField(max_length=50, null=True, blank=True)
    job_exhaustion = models.CharField(max_length=50, null=True, blank=True)
    job_relationship = models.CharField(max_length=50, null=True, blank=True)
    job_relationship_boss = models.CharField(max_length=50, null=True, blank=True)
    better_at_work = models.TextField(null=True, blank=True)
    less_at_work = models.TextField(null=True, blank=True)
    leisure_actions = models.CharField(max_length=50, null=True, blank=True)
    difficulty_sleeping = models.CharField(max_length=50, null=True, blank=True)
    planning_future = models.CharField(max_length=50, null=True, blank=True)
    stress_or_anxiety_major_problem = models.CharField(
        max_length=50, null=True, blank=True
    )
    depression_or_frustration_major_problem = models.CharField(
        max_length=50, null=True, blank=True
    )
    enjoyed_the_vacation = models.CharField(max_length=50, null=True, blank=True)
    satisfied_service = models.CharField(max_length=50, null=True, blank=True)
    satisfied_service_justify = models.TextField(null=True, blank=True)
    topics_of_interest = models.TextField(null=True, blank=True)
    observations = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Registros das Informações de Saúde"

    def __str__(self):
        return "%s" % self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    @property
    def icons(self):
        return self.icons_status

    @property
    def show_icon_from_admin(self):
        return get_current_user().has_perm("can_management_health_area")

    @property
    def icons_status(self):
        status = []

        if self.controlinformation.authorization_health:
            if self.health_assessments.filter().exists():
                if self.health_assessments.filter(signed_at__isnull=True).exists():
                    status.append(
                        {
                            "title": "Com avaliação pendente",
                            "iconCls": "icon-core icon-core-waiting",
                        }
                    )
                else:
                    status.append(
                        {
                            "title": "Avaliado",
                            "iconCls": "icon-crgmpe icon-crgmpe-autorizado",
                        }
                    )
            else:
                status.append(
                    {
                        "title": "Enviado para avaliação - Você é Único",
                        "iconCls": "icon-crgmpe icon-crgmpe-health",
                    }
                )
        else:
            status.append({"title": "", "iconCls": "icon-crgmpe icon-crgmpe-activated"})
        return status

    @property
    def assessments_signed(self):
        return self.health_assessments.filter(signed_at__isnull=False)

    @property
    def rendered(self):
        tpl = loader.get_template("health.html")
        return tpl.render({"health": self})

    @property
    def rendered_evaluation(self):
        tpl = loader.get_template("health_evaluation.html")
        check = lambda x: None if (x is None) or (str(x).strip() == "") else x
        return tpl.render(
            {
                "health": self,
                "ingestion_candy": Choice.objects.filter(
                    app_label="cirdir_health",
                    name="FREQUENCY_INGESTION",
                    value=check(self.ingestion_candy),
                ).first(),
                "ingestion_pasta": Choice.objects.filter(
                    app_label="cirdir_health",
                    name="FREQUENCY_INGESTION",
                    value=check(self.ingestion_pasta),
                ).first(),
                "ingestion_fruit": Choice.objects.filter(
                    app_label="cirdir_health",
                    name="FREQUENCY_INGESTION",
                    value=check(self.ingestion_fruit),
                ).first(),
                "ingestion_vegetable": Choice.objects.filter(
                    app_label="cirdir_health",
                    name="FREQUENCY_INGESTION",
                    value=check(self.ingestion_vegetable),
                ).first(),
                "ingestion_beef": Choice.objects.filter(
                    app_label="cirdir_health",
                    name="FREQUENCY_INGESTION",
                    value=check(self.ingestion_beef),
                ).first(),
                "ingestion_fry": Choice.objects.filter(
                    app_label="cirdir_health",
                    name="FREQUENCY_INGESTION",
                    value=check(self.ingestion_fry),
                ).first(),
                "ingestion_supplement": Choice.objects.filter(
                    app_label="cirdir_health",
                    name="FREQUENCY_INGESTION",
                    value=check(self.ingestion_supplement),
                ).first(),
            }
        )

    @property
    def has_recommendation_pending_confirmation(self):
        return HealthAssessment.query_all_recommendation_pending(health=self).exists()

    def save(self, health_area=False, *args, **kargs):
        if health_area:
            super(Health, self).save(*args, **kargs)
            self.controlinformation.authorization_health = True
            self.controlinformation.save(health_area=health_area)
        else:
            creating = False
            if self.pk is None:
                creating = True
            if self.controlinformation.closed_health:
                raise Exception(
                    "Não permitida a alteração nos dados de Saúde. Fechado para alteração."
                )
            else:
                if not getattr(self, "originated_from_the_copy", False):
                    self.updated_at = datetime.now()
                super(Health, self).save(*args, **kargs)
                if creating:
                    self.controlinformation.register_history(
                        criteria=Category.health.value,
                        action="Adicionada nova informação de saúde. [COD: %s]"
                        % self.pk,
                    )
                else:
                    self.controlinformation.register_history(
                        criteria=Category.health.value,
                        action="Alterada informação de saúde. [COD: %s]" % self.pk,
                    )
                self.controlinformation.nusubmit("health")
                self.controlinformation.save(saving=False)
        for data in self.controlinformation.employee._raw_locations(
            date=datetime.now()
        ):
            self.location.add(data.lotacao)
        super(Health, self).save(*args, **kargs)

    def delete(self, health_area=False, *args, **kargs):
        if health_area:
            super(Health, self).delete(*args, **kargs)
        else:
            if self.controlinformation.closed_health:
                raise Exception(
                    "Não permitida a alteração nos dados de saúde. Fechado para alteração."
                )
            else:
                self.controlinformation.register_history(
                    criteria=Category.health.value,
                    action="Removida informação de saúde. [%s]"
                    % self.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                )
                super(Health, self).delete(*args, **kargs)
                self.controlinformation.nusubmit("health")
                self.controlinformation.save(saving=False)

    @classmethod
    def delivery_health_to_evaluators(cls, healths=None, evaluators=None):
        """
        Método responsável por distribuir os questionário para os avaliadores.
        """
        lfn = lambda x: [x] if type(x) == type(int()) else x

        healths = lfn(healths)
        evaluators = lfn(evaluators)

        if not (healths and evaluators):
            raise Exception("Informe o(s) questionário(s) e o(s) avaliador(es)")
        else:

            for h in cls.objects.filter(pk__in=healths):
                h.__distribute_to_evaluators(evaluators=evaluators)

            return True

    def __distribute_to_evaluators(self, evaluators=[]):
        """
        Método responsável por distribuir o questionário para o avaliador.
        """
        with transaction.atomic():

            health_assessments = []
            employee_user = get_current_user()

            for e in Evaluator.query_to_delivery(instance=self).filter(
                pk__in=evaluators
            ):
                health_assessments.append(
                    HealthAssessment(
                        health=self,
                        evaluator=e,
                        created_at=datetime.now(),
                        created_by=employee_user,
                        modified_at=datetime.now(),
                        modified_by=employee_user,
                    )
                )

            HealthAssessment.objects.bulk_create(health_assessments)


class History(AuditTimestampModel):
    """
    Historico de acoes do SRDIR
    """

    controlinformation = models.ForeignKey(
        ControlInformation, related_name="historics", on_delete=models.PROTECT
    )
    criteria = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("cirdir", "CRITERIA"),
    )
    action = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Histório de ações do SRDIR"
        ordering = ["-created_at"]

    @classmethod
    def register(cls, controlinformation=None, criteria=0, action=""):
        history = cls(
            controlinformation=controlinformation, criteria=criteria, action=action
        )

        history.save()


class Attachment(AuditTimestampModel):
    """
    Anexos para o controle de informacoes
    """

    controlinformation = models.ForeignKey(
        ControlInformation,
        related_name="attachments",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    title = models.TextField(blank=False)
    attach = models.ForeignKey(
        Arquivo, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Anexos para o Controle de Informações"


class PrivateLog(AuditTimestampModel):
    """
    Regristo de Log Privado
    """

    controlinformation = models.ForeignKey(
        ControlInformation, related_name="privatelogs", on_delete=models.PROTECT
    )
    information = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Regirsto de Log Privado"


class HealthAssessment(AuditTimestampModel):
    """
    Modelo representa a avaliação realizada pelo profissional de saúde.
    """

    content = models.TextField(blank=True, null=True)
    content_signed = models.TextField(blank=True, null=True)
    evaluator = models.ForeignKey(
        Evaluator, related_name="health_assessments", on_delete=models.CASCADE
    )
    health = models.ForeignKey(
        Health, related_name="health_assessments", on_delete=models.CASCADE
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-signed_at"]

    @property
    def has_permission_signed(self):
        return self.evaluator.employee == employee_from_user(get_current_user())

    @property
    def has_permission_confirmed(self):
        return self.health.controlinformation.employee == employee_from_user(
            get_current_user()
        )

    def sign(self):
        if not self.has_permission_signed:
            raise Exception(
                "Apenas o(a) Senhor(a) {} poderá concluir essa avaliação".format(
                    self.evaluator.employee.pessoa_fisica
                )
            )
        else:
            self.signed_at = datetime.now()
            self.signed_by = get_current_user()
            self.content_signed = self.content
            self.save()

    @classmethod
    def query_all_recommendation_pending(
        cls, control_information=None, health=None, employee=None
    ):
        query = cls.objects.filter(signed_at__isnull=False, confirmed_at__isnull=True)

        if control_information:
            query = query.filter(health__controlinformaion=control_information)

        if health:
            query = query.filter(health=health)

        if employee:
            query = query.filter(health__controlinformation__employee=employee)

        return query

    def confirm(self):
        if not self.has_permission_confirmed:
            raise Exception(
                "Apenas o(a) Senhor(a) {} poderá dar ciêcia da recomendação".format(
                    self.health.controlinformation.employee.pessoa_fisica
                )
            )
        else:
            self.confirmed_at = datetime.now()
            self.confirmed_by = get_current_user()
            self.save()

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        status = []
        if self.signed_by:
            status.append(
                {"title": "Avaliado", "iconCls": "icon-core icon-core-success"}
            )
        else:
            status.append(
                {
                    "title": "Aguardando avaliação",
                    "iconCls": "icon-core icon-core-waiting",
                }
            )
        return status

    @property
    def read_only(self):
        if self.pk is None:
            return False
        else:
            old = self.__class__.objects.get(pk=self.pk)

            if old.signed_by is not None:
                if ((old.confirmed_at and self.confirmed_by) is None) and (
                    (self.confirmed_by and self.confirmed_at) is not None
                ):
                    return False
                else:
                    return True
            else:
                return False

    @property
    def rendered(self):
        tpl = loader.get_template("healthassessment.html")
        return tpl.render({"doc": self})

    def save(self, *args, **kwargs):
        if self.read_only:
            raise Exception("Registro não pode ser modificado. Somente leitura.")
        else:
            super(HealthAssessment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.read_only:
            raise Exception("Registro não pode ser modificado. Somente leitura.")
        else:
            raise Exception("Não é possível remover o registro.")
        super(HealthAssessment, self).delete(*args, **kwargs)


class Irpf(Part):
    """Informações e controle do comprovante do imposto de renda"""

    title = models.TextField(blank=True, null=True)
    file = models.ForeignKey(Arquivo, related_name="+", on_delete=models.CASCADE)
    validated = models.BooleanField(default=False)
    of_who = models.SmallIntegerField(
        default=1,
        choices=Choice.get_choices_for("cirdir", "KIND"),
    )

    codename = "irpf"

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return "" if self.file is None else self.file.title

    def define_permission_file(self):
        if self.file:
            self.file.acesso = Arquivo.GROUP
            self.file.save()

    def validate_file(self):
        try:
            if self.file.mimetype == "application/pdf":
                self.validated = True
            else:
                raise Exception(
                    "O arquivo possui um formato inválido. Informe um arquivo PDF."
                )
        except Exception as e:
            raise e

    def can_upload(self):
        try:
            if self.controlinformation:
                pass
            else:
                raise Exception("Arquivo não foi vinculado corretamente.")
        except Exception as e:
            raise str(e)

    def make_title(self):
        msg = "Comprovante - IRPF/{} - {} / Declaração {}"
        return msg.format(
            self.controlinformation.year,
            self.controlinformation.employee,
            self.get_of_who_display(),
        )

    @property
    def status(self):
        return "Declaração Informada." if self.validated else "Declaração é inválida."

    @property
    def can_change(self):
        return not self.controlinformation.closed_irpf

    def submit(self):
        try:

            SubmitStatus.register(
                control_information=self.controlinformation,
                part=Irpf.codename,
                objects=None,
                category=Category.irpf.value,
            )

            History.register(
                controlinformation=self.controlinformation,
                criteria=Category.irpf.value,
                action=f"Declaração do IRPF submetida.",
            )

        except Exception as e:
            log.error("erro ao submter informação no SRDIR")
            raise e

    def save(self, *args, **kwargs):
        try:
            if not self.can_change:
                raise Exception(
                    "Não permitido adicionar a declaração. Fechado para alteração."
                )

            if (
                self.__class__.objects.exclude(pk=self.pk)
                .filter(controlinformation=self.controlinformation, of_who=self.of_who)
                .exists()
            ):
                raise Exception(
                    "Um arquivo já foi inserido. Você está tentando anexar uma declaração do tipo {}".format(
                        self.get_of_who_display()
                    )
                )

            self.define_permission_file()
            self.validate_file()

            self.title = self.make_title()
            super(Irpf, self).save(*args, **kwargs)

            History.register(
                controlinformation=self.controlinformation,
                criteria=Category.irpf.value,
                action=f"Declaração do IRPF adicionada. Tipo {self.get_of_who_display()}",
            )
            self.submit()
        except Exception as e:
            raise e

    def delete(self, *args, **kwargs):
        try:
            if not self.can_change:
                raise Exception(
                    "Não permitido remover a declaração. Fechado para alteração."
                )
            super(Irpf, self).delete(*args, **kwargs)

            History.register(
                controlinformation=self.controlinformation,
                criteria=Category.irpf.value,
                action=f"Declaração do IRPF removida. Tipo {self.get_of_who_display()}",
            )
            self.controlinformation.nusubmit("irpf")
        except Exception as e:
            raise e


class InformationEvaluation(AuditTimestampModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    checked = models.BooleanField(default=False)
    checked_by_user = models.ForeignKey(
        User, related_name="+", null=True, on_delete=models.CASCADE
    )
    checked_on_date = models.DateTimeField(null=True, blank=True)
    is_true = models.BooleanField(null=True)
    observation = models.TextField(blank=True)

    def __str__(self):
        return self.content_object.__str__()

    class Meta:
        ordering = ["-created_at", "-checked"]

    @classmethod
    def add_to_queue(cls, instance):
        try:
            obj = cls(content_object=instance)
            obj.save()
        except Exception as e:
            raise e

    @classmethod
    def add_to_audit(cls, auditables):

        try:
            auditables = (
                auditables
                if isinstance(auditables, models.query.QuerySet)
                else [auditables]
            )

            for obj in auditables:
                InformationEvaluation.add_to_queue(obj)
        except Exception as e:
            raise e

    @property
    def rendered(self):
        return self.content_object.rendered

    def _to_accept(self, value):
        if not self.checked:
            self.checked_by_user = get_current_user()
            self.checked_on_date = datetime.now()
            self.checked = True
            self.is_true = value
        else:
            raise Exception("Item encontra-se avaliado.")

    def to_accept(self, value):
        try:
            with transaction.atomic():
                self._to_accept(value)
                status = SubmitStatus.SUBMITTED if value else SubmitStatus.ADJUST

                SubmitStatus.audit_register(
                    control_information=self.content_object.controlinformation,
                    part=self.content_object.codename,
                    status=status,
                )

                self.save()

        except Exception as e:
            log.error(f"Não foi possível aceitar o item: {str(e)}")
            raise e


class SubmitStatus(models.Model):
    NO_SUBMITTED = 0
    SUBMITTED = 1
    AUDIT = 2
    ADJUST = 3
    STATUS_CHOICES = (
        (NO_SUBMITTED, "Não submetido"),
        (SUBMITTED, "Submetido"),
        (AUDIT, "Em Análise"),
        (ADJUST, "Revisão"),
    )

    control_information = models.ForeignKey(
        ControlInformation, related_name="in_submit_status", on_delete=models.CASCADE
    )
    part = models.CharField(max_length=25)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=NO_SUBMITTED
    )

    class Meta:
        unique_together = (
            "control_information",
            "part",
        )

    @classmethod
    def get_instance_by_part(cls, control_information, part):
        return cls.objects.filter(
            control_information=control_information, part=part
        ).first()

    @classmethod
    def current_status_by_part(cls, control_information, part):
        obj = cls.get_instance_by_part(
            control_information=control_information, part=part
        )
        if obj:
            return obj.status
        else:
            return cls.NO_SUBMITTED

    @classmethod
    def audit_register(cls, control_information, part, status):
        try:

            obj = cls.objects.get(control_information=control_information, part=part)
            obj.status = status
            obj.save()

        except Exception as e:
            log.error("erro ao alterar estado do registro.")
            raise e

    @classmethod
    def initial_status(cls, control_information, part):
        obj, created = cls.objects.get_or_create(
            control_information=control_information,
            part=part,
            defaults={"status": cls.NO_SUBMITTED},
        )

        if not created and obj.status != cls.AUDIT:
            obj.status = cls.NO_SUBMITTED
            obj.save()

    @classmethod
    def register(cls, control_information, part, objects, category, is_auditable=False):

        try:
            if control_information.employee != employee_from_user(get_current_user()):
                raise Exception("O usuário não pode submeter essa informação.")

            with transaction.atomic():

                status = SubmitStatus.AUDIT if is_auditable else SubmitStatus.SUBMITTED

                obj, created = cls.objects.get_or_create(
                    control_information=control_information,
                    part=part,
                    defaults={"status": status},
                )

                if not created:
                    if obj.status == cls.AUDIT:
                        raise Exception(
                            "Essa informação encontra-se em análise pela Corregedoria."
                        )
                    else:
                        obj.status = status
                        obj.save()

                SubmitTimestamp(
                    submit_status=obj, when=datetime.now(), who=get_current_user()
                ).save()

                if is_auditable:
                    InformationEvaluation.add_to_audit(objects)

                if status == SubmitStatus.AUDIT:
                    History.register(
                        controlinformation=control_information,
                        criteria=category,
                        action="Enviado para auditoria",
                    )

        except Exception as e:
            log.error("erro ao criar próximo passo em submitstatus.")
            raise e

    @property
    def get_message_status(self):
        msg = ""

        if self.status == SubmitStatus.NO_SUBMITTED:
            msg = "Informação NÃO submetida."

        if self.status == SubmitStatus.AUDIT:
            msg = """Informações enviadas para análise. Caso haja alguma inconsistência você será avisado
            sobre. Caso contrário, o status será alterado para SUBMETIDO."""

        if self.status == SubmitStatus.ADJUST:
            msg = "Dados necessitam de ajuste conforme apontamento"

        if self.status == SubmitStatus.SUBMITTED:
            msg = "Informação submetida."

        return msg

    @property
    def rendered(self):
        tpl = loader.get_template("submitstatus.html")
        return tpl.render(
            {
                "submitstatus": self,
                "has_submitted": self.status == SubmitStatus.SUBMITTED,
                "timestamp": self.in_submit_timestamp_user.first(),
                "show_timestamp": self.status == SubmitStatus.SUBMITTED,
                "msg": self.get_message_status,
            }
        )


class RegisterTimestampUser(models.Model):
    when = models.DateTimeField()
    who = models.ForeignKey(User, related_name="+", on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ["-when"]


class SubmitTimestamp(RegisterTimestampUser):
    submit_status = models.ForeignKey(
        SubmitStatus, related_name="in_submit_timestamp_user", on_delete=models.CASCADE
    )


class Pendency(models.Model):
    DEADLINE = 0
    INFORMATION = 1

    KIND_CHOICES = (
        (DEADLINE, "Prazo não respeitado"),
        (INFORMATION, "Informação com pendência"),
    )

    control_information = models.ForeignKey(
        ControlInformation, related_name="pendencies", on_delete=models.CASCADE
    )
    message = models.CharField(max_length=200)
    part = models.CharField(max_length=30)
    kind = models.PositiveSmallIntegerField(choices=KIND_CHOICES)

    class Meta:
        unique_together = ("control_information", "part", "kind")

    @classmethod
    def register(cls, kind, control_information, part, message):
        try:
            obj, created = cls.objects.get_or_create(
                control_information=control_information,
                part=part,
                kind=kind,
                defaults={"message": message},
            )

            if not created:
                obj.message = message
                obj.save()

        except Exception as e:
            raise e

    @classmethod
    def unregister(cls, kind, control_information, part):
        try:
            for obj in cls.objects.filter(
                kind=kind, control_information=control_information, part=part
            ):
                obj.delete()
        except Exception as e:
            raise e

    @classmethod
    def rendered(cls, control_information, part):
        tpl = loader.get_template("pendency.html")
        pendencies = cls.objects.filter(
            control_information=control_information, part=part
        )
        return tpl.render(
            {
                "pendencies": pendencies,
            }
        )
