# -*- coding: utf-8 -*-
from ast import arg
import datetime
import locale
from num2words import num2words

from django.db import models
from django.template import loader
from django.db import transaction
from django.contrib.auth.models import User

from contrib.middleware import get_current_user
from contrib.utils import getLogger, DateUtils, employee_from_user
from edocs.protocolo.models import Protocolo as Protocol
from edocs.protocolo.requestform.helpers import (
    get_employee_job_position,
    get_employee_number,
    get_employee_rg,
    get_employee_cpf,
    get_employee_birth_date,
    get_employee_exercise_date,
    get_employee_blood,
    get_employee_donor,
    get_employee_rg_origin,
    get_employee_rg_date,
    get_employee_father_name,
    get_employee_mother_name,
    get_employee_address,
    get_employee_work_email,
)
from rh.const import TYPE_PHONE_INSTITUTIONAL
from rh.models import (
    MovimentacaoPosse as PossessionMovement,
    Servidor as Employee,
    Estado as State,
    Dependente,
)
from standard.models import Choice


log = getLogger()


class VacationDaySell(Protocol):
    days = models.PositiveIntegerField(
        default=0, verbose_name="Dias para vender", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/vacation-day-sell.html")

    @property
    def params(self):
        params = super().params

        pas = self.servidor_origem.periodos_aquisitivos.exclude(
            self.servidor_origem.query_pas_day_sell
        )

        params.update(
            {
                "employee": self.servidor_origem,
                "job_position": get_employee_job_position(self.servidor_origem),
                "pas": pas,
                "days": self.days,
                "days_as_words": num2words(self.days, lang="pt-BR").upper(),
            }
        )

        return params

    @classmethod
    def docketing(cls, days=0, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.days = days
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class MobileLiabilityStatement(Protocol):
    """Termo de Entrega e Responsabilidade (Celular)"""

    imei = models.CharField(max_length=50, verbose_name="Imei")
    phone_number = models.CharField(max_length=50, verbose_name="Nº da Linha")
    phone_description = models.TextField(verbose_name="Descrição do Bem")

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/mobile-liability-statement.html")

    @property
    def params(self):
        params = super().params

        job_position = get_employee_job_position(self.servidor_origem)

        params.update(
            {
                "job_position": job_position,
                "imei": self.imei or "Não informado",
                "phone_number": self.phone_number or "Não informado",
                "phone_description": self.phone_description or "Não informada",
            }
        )

        return params

    @classmethod
    def docketing(cls, imei, phone_number, phone_description, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.imei = imei
            instance.phone_number = phone_number
            instance.phone_description = phone_description
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class DebitAuthorization(Protocol):
    """Formulário para autorização de débito (Parceria Solidária II)"""

    debit_percentage = models.DecimalField(
        verbose_name="Débito em porcentagem", max_digits=5, decimal_places=2, default=0
    )
    suspended_by = models.ForeignKey(
        User,
        verbose_name="Suspenso por",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    suspended_at = models.DateTimeField(
        verbose_name="Suspenso em", null=True, blank=True
    )
    suspension_reason = models.TextField(
        verbose_name="Motivo da suspensão", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/debit-authorization.html")

    @property
    def params(self):
        params = super().params
        params.update(
            {
                "debit_percentage": str(self.debit_percentage).rstrip("0").rstrip("."),
                "job_position": get_employee_job_position(self.servidor_origem),
            }
        )
        return params

    @classmethod
    def docketing(cls, debit_percentage, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.debit_percentage = debit_percentage
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class ElectoralLicense(Protocol):
    """Formulário para Requerimento de Licença Eleitoral"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    description = models.TextField(
        verbose_name="Informe uma ou mais datas de licença", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/electoral-license.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "description": self.description or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, description, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.description = description
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class EmployeeRequest(Protocol):
    """Requerimento Servidor Administrativo"""

    request_type = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("requestform", "EMPLOYEE_REQUEST_TYPE"),
        verbose_name="Tipo requerimento",
        null=True,
        blank=True,
    )

    @classmethod
    def request_type_query(cls):
        return Choice.objects.filter(
            app_label="requestform", name="EMPLOYEE_REQUEST_TYPE"
        )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/employee-request.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "request_type": self.request_type,
                "request_type_query": self.request_type_query(),
                "description": self.resumo or "Não informada",
            }
        )

        return params

    @classmethod
    def docketing(cls, request_type, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.request_type = request_type
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class MemberRequest(Protocol):
    """Requerimento Promotor e Procurador de Justiça"""

    request_type = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("requestform", "MEMBER_REQUEST_TYPE"),
        verbose_name="Tipo requerimento",
        null=True,
        blank=True,
    )

    @classmethod
    def request_type_query(cls):
        return Choice.objects.filter(
            app_label="requestform", name="MEMBER_REQUEST_TYPE"
        )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/member-request.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "request_type": self.request_type,
                "request_type_query": self.request_type_query(),
                "description": self.resumo or "Não informada",
            }
        )

        return params

    @classmethod
    def docketing(cls, request_type, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.request_type = request_type
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class WeddingDayOff(Protocol):
    """Formulário para Requerimento Concessão por Motivo de Casamento"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    start_date = models.DateTimeField(
        verbose_name="Data de início", null=True, blank=True
    )
    end_date = models.DateTimeField(
        verbose_name="Data de término", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/wedding-day-off.html")

    @property
    def params(self):
        params = super().params

        start_date = "Não informada"
        if self.start_date:
            start_date = DateUtils.date_to_str(self.start_date)

        end_date = "Não informada"
        if self.end_date:
            end_date = DateUtils.date_to_str(self.end_date)

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, start_date, end_date, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.start_date = start_date
            instance.end_date = end_date
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class ChildbirthDayOff(Protocol):
    """Formulário para Requerimento Concessão ao Pai por Motivo de Nascimento do Filho"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/childbirth-day-off.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class ChildbirthAllowance(Protocol):
    """Formulário para Requerimento Auxílio Natalidade"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    child_name = models.CharField(
        max_length=100, verbose_name="Nome da criança", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/childbirth-allowance.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "child_name": self.child_name or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, child_name, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.child_name = child_name
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class FinalPaperDayOff(Protocol):
    """Formulário para Requerimento Concessão para Conclusão de TCC"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    start_date = models.DateTimeField(
        verbose_name="Data de início", null=True, blank=True
    )
    end_date = models.DateTimeField(
        verbose_name="Data de término", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/final-paper-day-off.html")

    @property
    def params(self):
        params = super().params

        start_date = "Não informada"
        if self.start_date:
            start_date = DateUtils.date_to_str(self.start_date)

        end_date = "Não informada"
        if self.end_date:
            end_date = DateUtils.date_to_str(self.end_date)

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, start_date, end_date, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.start_date = start_date
            instance.end_date = end_date
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class BloodDonationDayOff(Protocol):
    """Formulário para Requerimento Concessão para Doação de Sangue"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/blood-donation-day-off.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class ElectoralEnlistment(Protocol):
    """Formulário para Requerimento Concessão para Alistamento Eleitoral"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/electoral-enlistment.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class TransitPass(Protocol):
    """Formulário para Requerimento para Inclusão ou Exclusão de Vale Transporte"""

    INCLUSION = 0
    EXCLUSION = 1

    REQUEST_TYPE = [
        (INCLUSION, "Autorização de desconto"),
        (EXCLUSION, "Suspensão de desconto"),
    ]

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    request_type = models.PositiveSmallIntegerField(
        choices=REQUEST_TYPE, verbose_name="Tipo requerimento", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/transit-pass.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "request_type": self.request_type,
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, request_type, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.request_type = request_type
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class BereavementLeave(Protocol):
    """Formulário para Requerimento Concessão pelo Falecimento de Pessoa da Família"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    degree_of_kinship = models.CharField(
        max_length=50, verbose_name="Grau de parentesco", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/bereavement-leave.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "degree_of_kinship": self.degree_of_kinship or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, degree_of_kinship, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.degree_of_kinship = degree_of_kinship
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class FuneralAllowance(Protocol):
    """Formulário para Requerimento Auxílio Funeral"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    degree_of_kinship = models.CharField(
        max_length=50, verbose_name="Grau de parentesco", null=True, blank=True
    )
    deceased_name = models.CharField(
        max_length=100, verbose_name="Nome do(a) falecido(a)", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/funeral-allowance.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "degree_of_kinship": self.degree_of_kinship or "Não informado",
                "deceased_name": self.deceased_name or "Não informado",
                "employee_rg": get_employee_rg(self.servidor_origem),
                "employee_cpf": get_employee_cpf(self.servidor_origem),
            }
        )

        return params

    @classmethod
    def docketing(
        cls, contact_number, degree_of_kinship, deceased_name, *args, **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.degree_of_kinship = degree_of_kinship
            instance.deceased_name = deceased_name
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class VacancyDeclaration(Protocol):
    """Formulário para Requerimento de Declaração de Vacância"""

    start_date = models.DateTimeField(
        verbose_name="Data de início", null=True, blank=True
    )
    possession = models.ForeignKey(
        PossessionMovement,
        verbose_name="Cargo",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/vacancy-declaration.html")

    @property
    def params(self):
        params = super().params

        start_date = "Não informada"
        if self.start_date:
            start_date = DateUtils.date_to_str(self.start_date)

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "start_date": start_date,
                "possession": (
                    str(self.possession.quadro) if self.possession else "Não informado"
                ),
            }
        )

        return params

    @classmethod
    def docketing(cls, start_date, possession, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.start_date = start_date
            instance.possession = possession
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class Resignation(Protocol):
    """Formulário para Requerimento de Exoneração"""

    start_date = models.DateTimeField(
        verbose_name="Data de início", null=True, blank=True
    )
    possession = models.ForeignKey(
        PossessionMovement,
        verbose_name="Cargo",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/resignation.html")

    @property
    def params(self):
        params = super().params

        start_date = "Não informada"
        if self.start_date:
            start_date = DateUtils.date_to_str(self.start_date)

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "start_date": start_date,
                "possession": (
                    str(self.possession.quadro) if self.possession else "Não informado"
                ),
            }
        )

        return params

    @classmethod
    def docketing(cls, start_date, possession, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.start_date = start_date
            instance.possession = possession
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class MealAllowance(Protocol):
    """Requerimento para Concessão de Auxílio Alimentação"""

    working_time = models.CharField(
        max_length=50, verbose_name="Carga horária", null=True, blank=True
    )
    email = models.CharField(
        max_length=100, verbose_name="Email", null=True, blank=True
    )
    previous_public_institution = models.CharField(
        max_length=100, verbose_name="Órgão de origem", null=True, blank=True
    )
    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    option_term = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("requestform", "MEALALLOWANCE_OPTION_TERM"),
        verbose_name="Termo de opção",
        null=True,
        blank=True,
    )

    @classmethod
    def option_term_query(cls):
        return Choice.objects.filter(
            app_label="requestform", name="MEALALLOWANCE_OPTION_TERM"
        )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/meal-allowance.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "option_term": self.option_term,
                "option_term_query": self.option_term_query(),
                "working_time": self.working_time or "Não informada",
                "email": self.email or "Não informado",
                "previous_public_institution": self.previous_public_institution
                or "Não informado",
                "contact_number": self.contact_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        working_time,
        email,
        previous_public_institution,
        contact_number,
        option_term,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.working_time = working_time
            instance.email = email
            instance.previous_public_institution = previous_public_institution
            instance.contact_number = contact_number
            instance.option_term = option_term
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class ChildcareAllowance(Protocol):
    """Requerimento Auxílio Creche"""

    BIOLOGICAL_CHILD = 0
    DEPENDENT_CHILD = 1

    CHILD_TYPE = [(BIOLOGICAL_CHILD, "Filho(a)"), (DEPENDENT_CHILD, "Dependente")]

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    bank = models.CharField(max_length=40, verbose_name="Banco", null=True, blank=True)
    agency = models.CharField(
        max_length=25, verbose_name="Agência", null=True, blank=True
    )
    account = models.CharField(
        max_length=25, verbose_name="Conta", null=True, blank=True
    )
    child_name = models.CharField(
        max_length=100, verbose_name="Nome da criança", null=True, blank=True
    )
    child_type = models.PositiveSmallIntegerField(
        choices=CHILD_TYPE, verbose_name="Tipo vínculo", null=True, blank=True
    )
    child_birth_date = models.DateTimeField(
        verbose_name="Data de nascimento da criança", null=True, blank=True
    )
    child_cpf = models.CharField(
        max_length=20, verbose_name="CPF da criança", null=True, blank=True
    )
    spouse = models.ForeignKey(
        Employee,
        verbose_name="Cônjuge",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    receiver = models.ForeignKey(
        Employee,
        verbose_name="Recebedor",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/childcare-allowance.html")

    @property
    def params(self):
        params = super().params

        child_birth_date = "Não informada"
        if self.child_birth_date:
            child_birth_date = DateUtils.date_to_str(self.child_birth_date)

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "contact_number": self.contact_number or "Não informado",
                "bank": self.bank or "Não informado",
                "agency": self.agency or "Não informado",
                "account": self.account or "Não informado",
                "child_type": self.child_type,
                "child_name": self.child_name or "Não informado",
                "child_birth_date": child_birth_date,
                "child_cpf": self.child_cpf or "Não informado",
                "spouse_name": (
                    self.spouse.pessoa_fisica.nome if self.spouse else "Não informado"
                ),
                "receiver_name": (
                    self.receiver.pessoa_fisica.nome
                    if self.receiver
                    else "Não informado"
                ),
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        contact_number,
        bank,
        agency,
        account,
        child_name,
        child_type,
        child_birth_date,
        child_cpf,
        spouse,
        receiver,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.bank = bank
            instance.agency = agency
            instance.account = account
            instance.child_name = child_name
            instance.child_type = child_type
            instance.child_birth_date = child_birth_date
            instance.child_cpf = child_cpf
            instance.spouse = spouse if isinstance(spouse, Employee) else None
            instance.receiver = receiver if isinstance(receiver, Employee) else None
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class SpecialNeedsAllowance(Protocol):
    """Requerimento de Auxílio-Especial"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    spouse = models.ForeignKey(
        Employee,
        verbose_name="Cônjuge",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    receiver = models.ForeignKey(
        Employee,
        verbose_name="Recebedor",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    dependent_name = models.CharField(
        max_length=100, verbose_name="Nome do dependente", null=True, blank=True
    )
    dependent_birth_date = models.DateTimeField(
        verbose_name="Data de nascimento do dependente", null=True, blank=True
    )
    dependent_cpf = models.CharField(
        max_length=20, verbose_name="CPF do dependente", null=True, blank=True
    )
    dependent_rg = models.CharField(
        max_length=40, verbose_name="RG do dependente", null=True, blank=True
    )
    dependent_uf = models.ForeignKey(
        State,
        verbose_name="UF",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    dependent_address = models.CharField(
        max_length=150, verbose_name="Endereço", null=True, blank=True
    )
    icd = models.CharField(
        max_length=10,
        verbose_name="CID-10 (Código Internacional da Doença)",
        null=True,
        blank=True,
    )
    disability_type = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for(
            "requestform", "SPECIALNEEDSALLOWANCE_DISABILITY_TYPE"
        ),
        verbose_name="Tipo de deficiência",
        null=True,
        blank=True,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/special-needs-allowance.html")

    @property
    def params(self):
        params = super().params

        dependent_birth_date = "Não informada"
        if self.dependent_birth_date:
            dependent_birth_date = DateUtils.date_to_str(self.dependent_birth_date)

        disability_type_display = "Não informada"
        if self.disability_type:
            disability_type_display = self.get_disability_type_display()

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "dependent_name": self.dependent_name or "Não informado",
                "dependent_birth_date": dependent_birth_date,
                "dependent_cpf": self.dependent_cpf or "Não informado",
                "dependent_rg": self.dependent_rg or "Não informado",
                "dependent_uf": (
                    self.dependent_uf.sigla if self.dependent_uf else "Não informado"
                ),
                "dependent_address": self.dependent_address or "Não informado",
                "disability_type_display": disability_type_display,
                "icd": self.icd or "Não informado",
                "spouse_name": (
                    self.spouse.pessoa_fisica.nome if self.spouse else "Não informado"
                ),
                "receiver_name": (
                    self.receiver.pessoa_fisica.nome
                    if self.receiver
                    else "Não informado"
                ),
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        contact_number,
        spouse,
        receiver,
        dependent_name,
        dependent_birth_date,
        dependent_cpf,
        dependent_rg,
        dependent_uf,
        dependent_address,
        disability_type,
        icd,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)

            if not isinstance(dependent_birth_date, datetime.date):
                dependent_birth_date = None

            instance.contact_number = contact_number
            instance.spouse = spouse if isinstance(spouse, Employee) else None
            instance.receiver = receiver if isinstance(receiver, Employee) else None
            instance.dependent_name = dependent_name
            instance.dependent_birth_date = dependent_birth_date
            instance.dependent_cpf = dependent_cpf
            instance.dependent_rg = dependent_rg
            instance.dependent_uf = (
                dependent_uf if isinstance(dependent_uf, State) else None
            )
            instance.dependent_address = dependent_address
            instance.disability_type = disability_type
            instance.icd = icd
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class FunctionalIdentity(Protocol):
    """Requerimento Solicitação de Emissão de Cédula de Identidade Funcional"""

    is_reissue = models.BooleanField(
        default=False, verbose_name="2ª via", null=True, blank=True
    )
    reissue_reason = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for(
            "requestform", "FUNCTIONALIDENTITY_REISSUE_REASON"
        ),
        verbose_name="Motivo da 2ª via",
        null=True,
        blank=True,
    )

    # Servidor à disposição:
    original_public_institution = models.CharField(
        max_length=150, verbose_name="Órgão de origem", null=True, blank=True
    )
    original_employment_date = models.DateTimeField(
        verbose_name="Data admissão origem", null=True, blank=True
    )
    original_job_position = models.CharField(
        max_length=150, verbose_name="Cargo de origem", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/functional-identity.html")

    @property
    def params(self):
        params = super().params

        reissue_reason_display = "Não informada"
        if self.reissue_reason:
            reissue_reason_display = self.get_reissue_reason_display()

        original_employment_date = "Não informada"
        if self.original_employment_date:
            original_employment_date = DateUtils.date_to_str(
                self.original_employment_date
            )

        params.update(
            {
                "name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "number": get_employee_number(self.servidor_origem),
                "birth_date": get_employee_birth_date(self.servidor_origem),
                "exercise_date": get_employee_exercise_date(self.servidor_origem),
                "blood": get_employee_blood(self.servidor_origem),
                "donor": get_employee_donor(self.servidor_origem),
                "rg": get_employee_rg(self.servidor_origem),
                "rg_origin": get_employee_rg_origin(self.servidor_origem),
                "rg_date": get_employee_rg_date(self.servidor_origem),
                "cpf": get_employee_cpf(self.servidor_origem),
                "father_name": get_employee_father_name(self.servidor_origem),
                "mother_name": get_employee_mother_name(self.servidor_origem),
                "is_reissue": self.is_reissue,
                "reissue_reason_display": reissue_reason_display,
                "original_public_institution": self.original_public_institution
                or "Não informado",
                "original_employment_date": original_employment_date,
                "original_job_position": self.original_job_position or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        is_reissue,
        reissue_reason,
        original_public_institution,
        original_employment_date,
        original_job_position,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)

            if not isinstance(original_employment_date, datetime.date):
                original_employment_date = None

            instance.is_reissue = is_reissue
            instance.reissue_reason = reissue_reason
            instance.original_public_institution = original_public_institution
            instance.original_employment_date = original_employment_date
            instance.original_job_position = original_job_position
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class IdBadge(Protocol):
    """Requerimento para Confecção de Crachá"""

    is_reissue = models.BooleanField(
        default=False, verbose_name="2ª via", null=True, blank=True
    )
    reissue_reason = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for(
            "requestform", "FUNCTIONALIDENTITY_REISSUE_REASON"
        ),
        verbose_name="Motivo da 2ª via",
        null=True,
        blank=True,
    )

    display_name = models.CharField(
        max_length=100,
        verbose_name="Nome para constar no crachá",
        null=True,
        blank=True,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/id-badge.html")

    @property
    def params(self):
        params = super().params

        reissue_reason_display = "Não informada"
        if self.reissue_reason:
            reissue_reason_display = self.get_reissue_reason_display()

        params.update(
            {
                "name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "number": get_employee_number(self.servidor_origem),
                "birth_date": get_employee_birth_date(self.servidor_origem),
                "blood": get_employee_blood(self.servidor_origem),
                "rg": get_employee_rg(self.servidor_origem),
                "rg_origin": get_employee_rg_origin(self.servidor_origem),
                "cpf": get_employee_cpf(self.servidor_origem),
                "is_reissue": self.is_reissue,
                "reissue_reason_display": reissue_reason_display,
                "display_name": self.display_name or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, is_reissue, reissue_reason, display_name, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.is_reissue = is_reissue
            instance.reissue_reason = reissue_reason
            instance.display_name = display_name
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class AnticipationThirteenth(Protocol):
    """Requerimento de Antecipação de 50% do 13º Salário"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/anticipation-thirteenth.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "birth_date": get_employee_birth_date(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class NonAnticipationThirteenth(Protocol):
    """Requerimento de Não Recebimento da Antecipação de 50% do 13º Salário"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/non-anticipation-thirteenth.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "birth_date": get_employee_birth_date(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class DependentInclusion(Protocol):
    """Requerimento Inclusão de Dependentes"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    def validate(self):
        if self.dependents.filter(unimpeded_as_taxpayer_dependent=False).exists():
            raise Exception(
                "Ao menos uma das pessoas para quem se pede inclusão, não foi declarada desempedida para efeitos de tributação de imposto de renda."
            )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/dependent-inclusion.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "dependents": self.dependents.all(),
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.validate()
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class Dependent(models.Model):
    """Dependente"""

    dependent_inclusion = models.ForeignKey(
        DependentInclusion,
        verbose_name="Inclusão",
        related_name="dependents",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100, verbose_name="Nome do dependente")
    cpf = models.CharField(max_length=14, verbose_name="CPF do dependente")
    degree_of_kinship = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("rh", "DEPENDENT_TYPE"),
        verbose_name="Grau de Parentesco",
    )
    unimpeded_as_taxpayer_dependent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Dados de Dependentes"

    def __str__(self):
        return self.name


class DependentExclusion(Protocol):
    """Requerimento Exclusão de Dependentes"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )

    def validate(self):
        if self.dependent_exclusion_items.filter(
            income_tax=False, post_mortem_pension=False
        ).exists():
            raise Exception(
                "Em ao menos um dos dependentes não foi apontada nenhuma finalidade de exclusão"
            )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/dependent-exclusion.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "exclusion_items": self.dependent_exclusion_items.all(),
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.validate()
            instance.contact_number = contact_number
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class DependentExclusionItem(models.Model):
    """Dependente a ser Excluido"""

    dependent_exclusion = models.ForeignKey(
        DependentExclusion,
        verbose_name="Exclusão",
        related_name="dependent_exclusion_items",
        on_delete=models.CASCADE,
    )
    dependent = models.ForeignKey(
        Dependente,
        verbose_name="Dependente",
        related_name="dependent_exclusion_items",
        on_delete=models.CASCADE,
    )
    income_tax = models.BooleanField(default=False)
    post_mortem_pension = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Dependente a ser Excluido"

    def __str__(self):
        return self.dependent.pessoa_fisica.nome


class FullTimeHomeOffice(Protocol):
    """Full-time Home Office Application Form - Risk Groups (COVID-19)

    Formulário para Requerimento de Teletrabalho Integral - Grupo de Risco
    """

    boss = models.ForeignKey(
        Employee,
        verbose_name="Chefia imediata",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    start_date = models.DateField(verbose_name="Data de início", null=True, blank=True)

    # Condition (Risk Group):
    elderly = models.BooleanField(default=False, verbose_name="Idosos")
    pregnant = models.BooleanField(default=False, verbose_name="Gestantes")
    chronic_diseases = models.BooleanField(
        default=False, verbose_name="Doenças crônicas"
    )
    pneumopathy_diseases = models.BooleanField(
        default=False, verbose_name="Portadores de pneumopatias"
    )
    kidney_diseases = models.BooleanField(
        default=False, verbose_name="Portadores de doenças renais"
    )
    cardiovascular_diseases = models.BooleanField(
        default=False, verbose_name="Portadores de doenças cardiovasculares"
    )
    obese = models.BooleanField(default=False, verbose_name="Pessoas com obesidades")

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/fulltime-homeoffice.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "job_position": get_employee_job_position(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "boss_name": self.boss.pessoa_fisica.nome,
                "boss_job_position": get_employee_job_position(self.boss),
                "start_date": self.start_date,
                "elderly": self.elderly,
                "pregnant": self.pregnant,
                "chronic_diseases": self.chronic_diseases,
                "pneumopathy_diseases": self.pneumopathy_diseases,
                "kidney_diseases": self.kidney_diseases,
                "cardiovascular_diseases": self.cardiovascular_diseases,
                "obese": self.obese,
            }
        )

        return params

    @classmethod
    def boss_from_current_employee(cls):
        current_employee = employee_from_user(get_current_user())

        if current_employee and current_employee.chefe_imediato:
            return current_employee.chefe_imediato

        return None

    @classmethod
    def validate_boss(cls):
        if not cls.boss_from_current_employee():
            raise Exception(
                "Não consegui encontrar a chefia imediata do usuário corrente."
            )

    @classmethod
    def docketing(
        cls,
        start_date,
        elderly,
        pregnant,
        chronic_diseases,
        pneumopathy_diseases,
        kidney_diseases,
        cardiovascular_diseases,
        obese,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            cls.validate_boss()

            instance.boss = cls.boss_from_current_employee()
            instance.start_date = start_date
            instance.elderly = elderly
            instance.pregnant = pregnant
            instance.chronic_diseases = chronic_diseases
            instance.pneumopathy_diseases = pneumopathy_diseases
            instance.kidney_diseases = kidney_diseases
            instance.cardiovascular_diseases = cardiovascular_diseases
            instance.obese = obese
            instance.save()

            return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class ComeByBike(Protocol):
    """Come By Bike Application Form

    Termo de Adesão ao Programa "Vem de Bike"
    """

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/come-by-bike.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
            }
        )

        return params

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class MobileReturnStatement(Protocol):
    """Termo de Devolução (Celular)"""

    imei = models.CharField(max_length=50, verbose_name="Imei")
    phone_number = models.CharField(max_length=50, verbose_name="Nº da Linha")
    phone_description = models.CharField(
        max_length=256, verbose_name="Descrição do bem"
    )
    successor = models.ForeignKey(
        Employee,
        verbose_name="Sucessor",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    returned_battery_charger = models.BooleanField(
        default=False, verbose_name="Carregador de bateria devolvido"
    )
    returned_headphone = models.BooleanField(
        default=False, verbose_name="Fone de ouvido devolvido"
    )
    returned_sim_ejector = models.BooleanField(
        default=False, verbose_name="Extrator de SIM card devolvido"
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/mobile-return-statement.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "imei": self.imei or "Não informado",
                "phone_number": self.phone_number or "Não informado",
                "phone_description": self.phone_description or "Não informada",
                "successor": (
                    self.successor.pessoa_fisica.nome if self.successor else ""
                ),
                "returned_battery_charger": self.returned_battery_charger,
                "returned_headphone": self.returned_headphone,
                "returned_sim_ejector": self.returned_sim_ejector,
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        imei,
        phone_number,
        phone_description,
        successor,
        returned_battery_charger,
        returned_headphone,
        returned_sim_ejector,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.imei = imei
            instance.phone_number = phone_number
            instance.phone_description = phone_description
            instance.successor = successor if isinstance(successor, Employee) else None
            instance.returned_battery_charger = returned_battery_charger
            instance.returned_headphone = returned_headphone
            instance.returned_sim_ejector = returned_sim_ejector
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class ThirteenthAnticipation(Protocol):
    """REQUERIMENTO DE ANTECIPAÇÃO DE 13º SALÁRIO (70%/90%)"""

    contact_number = models.CharField(
        max_length=50, verbose_name="Telefone de contato", null=True, blank=True
    )
    option_term = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for(
            "requestform", "THIRTEENTHANTICIPATION_OPTION_TERM"
        ),
        verbose_name="Termo de opção",
        null=True,
        blank=True,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/thirteenth-anticipation.html")

    @property
    def params(self):
        params = super().params

        option_term_display = "Não informado"
        if self.option_term is not None:
            option_term_display = self.get_option_term_display()

        params.update(
            {
                "employee_name": str(self.interessado),
                "job_position": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "birth_date": get_employee_birth_date(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "contact_number": self.contact_number or "Não informado",
                "option_term": self.option_term,
                "option_term_display": option_term_display,
            }
        )

        return params

    @classmethod
    def docketing(cls, contact_number, option_term, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.contact_number = contact_number
            instance.option_term = option_term
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class HealthcareAllowanceForActiveEmployee(Protocol):
    """Requerimento de Auxílio Saúde para Servidores Ativos"""

    request_type = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("requestform", "HEALTHCARE_ACTIVE_EMP_REQTYPE"),
        verbose_name="Tipo de requerimento",
        null=True,
        blank=True,
    )

    @classmethod
    def request_type_query(cls):
        return Choice.objects.filter(
            app_label="requestform", name="HEALTHCARE_ACTIVE_EMP_REQTYPE"
        )

    @property
    def _template_renderer(self):
        return loader.get_template(
            "edocs/requestform/healthcare-allowance-active-employee.html"
        )

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
                "job_position": get_employee_job_position(self.servidor_origem),
                "department": self.orgao_geral_origem,
                "request_type": self.request_type,
                "request_type_display": self.get_request_type_display(),
                "request_type_query": self.request_type_query(),
            }
        )

        return params

    @classmethod
    def docketing(cls, request_type, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.request_type = request_type
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class HealthcareAllowanceForInactiveEmployee(Protocol):
    """Requerimento de Auxílio Saúde para Servidores Inativos ou Pensionistas"""

    BENEFICIARY_TYPE_CHOICES = [
        (1, "Aposentado(a)"),
        (2, "Pensionista"),
    ]

    address = models.CharField(
        max_length=166, verbose_name="Endereço", null=True, blank=True
    )
    contact_number = models.CharField(
        max_length=50, verbose_name="Número de contato", null=True, blank=True
    )
    beneficiary_type = models.PositiveSmallIntegerField(
        choices=BENEFICIARY_TYPE_CHOICES,
        verbose_name="Tipo de beneficiário",
        null=True,
        blank=True,
    )
    request_type = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for(
            "requestform", "HEALTHCARE_INACTIVE_EMP_REQTYPE"
        ),
        verbose_name="Tipo de requerimento",
        null=True,
        blank=True,
    )

    @classmethod
    def request_type_query(cls):
        return Choice.objects.filter(
            app_label="requestform", name="HEALTHCARE_INACTIVE_EMP_REQTYPE"
        )

    @property
    def _template_renderer(self):
        return loader.get_template(
            "edocs/requestform/healthcare-allowance-inactive-employee.html"
        )

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "address": self.address or "Não informado",
                "contact_number": self.contact_number or "Não informado",
                "beneficiary_type": self.beneficiary_type,
                "beneficiary_type_display": self.get_beneficiary_type_display(),
                "request_type": self.request_type,
                "request_type_display": self.get_request_type_display(),
                "request_type_query": self.request_type_query(),
            }
        )

        return params

    @classmethod
    def docketing(
        cls, address, contact_number, beneficiary_type, request_type, *args, **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.address = address
            instance.contact_number = contact_number
            instance.beneficiary_type = beneficiary_type
            instance.request_type = request_type
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class TermoCompromissoManutencaoSigilo(Protocol):
    """Termo de Compromisso de Manutenção do Sigilo"""

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/termo-compromisso-sigilo.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "employee_rg": get_employee_rg(self.servidor_origem),
                "employee_address": get_employee_address(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "employee_number": get_employee_number(self.servidor_origem),
            }
        )

        return params

    @classmethod
    def docketing(cls, *args, **kwargs):
        instance = super().docketing(*args, **kwargs)
        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class Evaluation(Protocol):
    """Relatório de Avaliação de Trabalho Remoto"""

    employee = models.ForeignKey(
        Employee,
        verbose_name="Servidor",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    cumpliance_activities_goals = models.TextField(
        verbose_name="Cumprimento das atividades e metas"
    )
    employee_date_established = models.BooleanField(
        null=True, verbose_name="O servidor cumpriu os prazos estabelecidos?"
    )
    employee_working_established = models.BooleanField(
        null=True, verbose_name="O servidor cumpriu a jornada estabelecida?"
    )
    employee_available = models.BooleanField(
        null=True,
        verbose_name="O servidor estava disponível através dos canais de comunicação no horário habitual de expediente?",
    )
    employee_addaption_working = models.BooleanField(
        null=True, verbose_name="O servidor se adaptou ao teletrabalho?"
    )
    employee_disobey_working = models.BooleanField(
        null=True,
        verbose_name="O servidor descumpriu algum dever a si estabelecido durante o teletrabalho?",
    )
    ask_affirmation_working = models.TextField(
        verbose_name="Em caso afirmativo da pergunta acima, elencar quais deveres foram descumpridos:"
    )
    note = models.TextField(verbose_name="Observações")
    start_date = models.DateTimeField(
        verbose_name="Data de início", null=True, blank=True
    )
    end_date = models.DateTimeField(
        verbose_name="Data de término", null=True, blank=True
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/evaluation.html")

    @property
    def params(self):
        params = super().params

        start_date = "Não informada"
        if self.start_date:
            start_date = DateUtils.date_to_str(self.start_date)

        end_date = "Não informada"
        if self.end_date:
            end_date = DateUtils.date_to_str(self.end_date)

        params.update(
            {
                "employee": self.employee.pessoa_fisica.nome if self.employee else "",
                "job_position": get_employee_job_position(self.employee),
                "department": self.my_origin.employee.work_locations.filter(
                    servidores_lotacao__ativo=True,
                    servidores_lotacao__designacao=False,
                    organograma=True,
                )[0],
                # 'department': self.my_origin.employee.work_locations.filter(acesso_protocolo_geral=True),
                # 'department': self.my_origin.employee.work_locations_effective_exercise.last(),
                "employee_work_email": get_employee_work_email(self.employee),
                "employee_number": get_employee_number(self.employee),
                # 'boss_name': self.employee.chefe_imediato,
                "boss_name": str(self.employee.chefe_imediato),
                "boss_job_position": get_employee_job_position(
                    self.employee.chefe_imediato
                ),
                "cumpliance_activities_goals": self.cumpliance_activities_goals
                or "Não informado",
                "employee_date_established": self.employee_date_established,
                "employee_working_established": self.employee_working_established,
                "employee_available": self.employee_available,
                "employee_addaption_working": self.employee_addaption_working,
                "employee_disobey_working": self.employee_disobey_working,
                "ask_affirmation_working": self.ask_affirmation_working
                or "Não informado",
                "note": self.note or "Não informado",
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        employee,
        cumpliance_activities_goals,
        employee_date_established,
        employee_working_established,
        employee_available,
        employee_addaption_working,
        employee_disobey_working,
        ask_affirmation_working,
        note,
        start_date,
        end_date,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.employee = employee if isinstance(employee, Employee) else None
            instance.cumpliance_activities_goals = cumpliance_activities_goals
            instance.employee_date_established = employee_date_established
            instance.employee_working_established = employee_working_established
            instance.employee_available = employee_available
            instance.employee_addaption_working = employee_addaption_working
            instance.employee_disobey_working = employee_disobey_working
            instance.ask_affirmation_working = ask_affirmation_working
            instance.note = note
            instance.start_date = start_date
            instance.end_date = end_date
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class HomeOfficeForEmployee(Protocol):
    """Requerimento de Teletrabalho para Servidor"""

    request_type = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for(
            "requestform", "HOME_OFFICE_FOR_EMPLOYEE_REQTYPE"
        ),
        verbose_name="Tipo de requerimento",
        null=True,
        blank=True,
    )

    justification = models.TextField(verbose_name="Justificativa")
    activities_goals = models.TextField(verbose_name="Atividades e Objetivos")
    schedule = models.TextField(verbose_name="Cronograma")

    @classmethod
    def request_type_query(cls):
        return Choice.objects.filter(
            app_label="requestform", name="HOME_OFFICE_FOR_EMPLOYEE_REQTYPE"
        )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/home-office-for-employee.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "justification": self.justification or "Não informado",
                "activities_goals": self.activities_goals or "Não informado",
                "schedule": self.schedule or "Não informado",
                "request_type": self.request_type,
                "request_type_display": self.get_request_type_display(),
                "request_type_query": self.request_type_query(),
                "home_court_unicode": str(self.orgao_geral_origem),
            }
        )

        return params

    @classmethod
    def docketing(
        cls, request_type, justification, activities_goals, schedule, *args, **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.justification = justification
            instance.activities_goals = activities_goals
            instance.schedule = schedule
            instance.request_type = request_type
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class RemoveNotificationApplication(Protocol):
    """Inscrição Edital de Remoção n. 02/2022"""

    position_start_concurso = models.CharField(
        max_length=100,
        verbose_name="Posição no concurso de ingresso",
        null=True,
        blank=True,
    )
    option_interest = models.TextField(verbose_name="Vagas de interesse")

    @property
    def _template_renderer(self):
        return loader.get_template(
            "edocs/requestform/remove-notification_application.html"
        )

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "exercise_date": DateUtils.date_to_str(
                    self.servidor_origem.exercise_date
                ),
                "position_start_concurso": self.position_start_concurso
                or "Não informado",
                "option_interest": self.option_interest or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, position_start_concurso, option_interest, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.position_start_concurso = position_start_concurso
            instance.option_interest = option_interest
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class RemoveNotificationResistance(Protocol):
    """Desistência Edital de Remoção n. 02/2022"""

    cancellation_vacancies = models.TextField(verbose_name="Vagas de desistência")
    resistance_declaration = models.TextField(verbose_name="Declaração de desistência")

    @property
    def _template_renderer(self):
        return loader.get_template(
            "edocs/requestform/remove-notification_resistance.html"
        )

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "cancellation_vacancies": self.cancellation_vacancies
                or "Não informado",
                # 'resistance_declaration': self.resistance_declaration or 'Não informado',
            }
        )

        return params

    @classmethod
    def docketing(cls, cancellation_vacancies, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.cancellation_vacancies = cancellation_vacancies
            # instance.resistance_declaration = resistance_declaration
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class IntimationWhatsAppAuthenticityVerifiable(Protocol):
    """Intimição por WhatsApp com Autenticidade Verificável"""

    name_intimate = models.CharField(max_length=100, verbose_name="Nome do indiciado")
    cpf_intimate = models.CharField(max_length=20, verbose_name="CPF do indiciado")
    name_victim = models.CharField(max_length=100, verbose_name="Nome da vítima")
    cpf_victim = models.CharField(max_length=20, verbose_name="CPF da vítima")
    number_inquiry_police = models.CharField(
        max_length=50,
        verbose_name="Número do Inquérito Policial",
        null=True,
        blank=True,
    )
    is_victim = models.BooleanField(default=False)

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/intimationwhatsapp.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_address": get_employee_address(
                    self.servidor_origem
                ).municipio,
                "employee_workplace": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.comarca
                or "Não informado",
                "workplace_hours": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.office_hours
                or "Não informado",
                "employee_ramal": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.phone.filter(publico=True)
                .last()
                or self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.phone.filter(publico=False)
                .last()
                or "Não informado",
                "name_intimate": self.name_intimate or "Não informado",
                "cpf_intimate": self.cpf_intimate or "Não informado",
                "name_victim": self.name_victim or "Não informado",
                "cpf_victim": self.cpf_victim or "Não informado",
                "number_inquiry_police": self.number_inquiry_police or "Não informado",
                "is_victim": self.is_victim,
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        name_intimate,
        cpf_intimate,
        name_victim,
        cpf_victim,
        number_inquiry_police,
        is_victim,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.name_intimate = name_intimate
            instance.cpf_intimate = cpf_intimate
            instance.name_victim = name_victim
            instance.cpf_victim = cpf_victim
            instance.number_inquiry_police = number_inquiry_police
            instance.is_victim = False if is_victim == False else True
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class IntimationWhatsAppAuthenticityVerifiableVictim(Protocol):
    """Intimição por WhatsApp com Autenticidade Verificável da Vítima"""

    name_intimate = models.CharField(max_length=100, verbose_name="Nome do indiciado")
    cpf_intimate = models.CharField(max_length=20, verbose_name="CPF do indiciado")
    name_victim = models.CharField(max_length=100, verbose_name="Nome da vítima")
    cpf_victim = models.CharField(max_length=20, verbose_name="CPF da vítima")
    number_inquiry_police = models.CharField(
        max_length=50,
        verbose_name="Número do Inquérito Policial",
        null=True,
        blank=True,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/intimationwhatsappvictim.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_address": get_employee_address(
                    self.servidor_origem
                ).municipio,
                "employee_workplace": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.comarca
                or "Não informado",
                "workplace_hours": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.office_hours
                or "Não informado",
                "employee_ramal": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.phone.filter(publico=True)
                .last()
                or self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.phone.filter(publico=False)
                .last()
                or "Não informado",
                "name_intimate": self.name_intimate or "Não informado",
                "cpf_intimate": self.cpf_intimate or "Não informado",
                "name_victim": self.name_victim or "Não informado",
                "cpf_victim": self.cpf_victim or "Não informado",
                "number_inquiry_police": self.number_inquiry_police or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        name_intimate,
        cpf_intimate,
        name_victim,
        cpf_victim,
        number_inquiry_police,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.name_intimate = name_intimate
            instance.cpf_intimate = cpf_intimate
            instance.name_victim = name_victim
            instance.cpf_victim = cpf_victim
            instance.number_inquiry_police = number_inquiry_police
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class IntimationWhatsAppAuthenticityVerifiableIntimate(Protocol):
    """Intimição por WhatsApp com Autenticidade Verificável do Indiciado"""

    name_intimate = models.CharField(max_length=100, verbose_name="Nome do indiciado")
    cpf_intimate = models.CharField(max_length=20, verbose_name="CPF do indiciado")
    number_inquiry_police = models.CharField(
        max_length=50,
        verbose_name="Número do Inquérito Policial",
        null=True,
        blank=True,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/intimationwhatsappintimate.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_address": get_employee_address(
                    self.servidor_origem
                ).municipio,
                "employee_workplace": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.comarca
                or "Não informado",
                "workplace_hours": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.office_hours
                or "Não informado",
                "employee_ramal": self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.phone.filter(publico=True)
                .last()
                or self.servidor_origem.work_assignment_effective_exercise.filter(
                    lotacao=self.orgao_geral_origem
                )
                .first()
                .lotacao.phone.filter(publico=False)
                .last()
                or "Não informado",
                "name_intimate": self.name_intimate or "Não informado",
                "cpf_intimate": self.cpf_intimate or "Não informado",
                "number_inquiry_police": self.number_inquiry_police or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(
        cls, name_intimate, cpf_intimate, number_inquiry_police, *args, **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.name_intimate = name_intimate
            instance.cpf_intimate = cpf_intimate
            instance.number_inquiry_police = number_inquiry_police
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class MedicalLicense(Protocol):
    """Licença Junta Médica"""

    grade_familiar = models.CharField(
        max_length=100, verbose_name="Parentesco familiar"
    )
    is_familiar = models.BooleanField(default=False)

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/medicallicense.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "employee_address": get_employee_address(self.servidor_origem),
                "employee_city": get_employee_address(self.servidor_origem).municipio,
                "employee_cep": get_employee_address(self.servidor_origem).cep,
                "employee_phone": self.servidor_origem.pessoa_fisica.phone.filter(
                    tipo_telefone__in=(1, 2, 3)
                ).first()
                or "Não informado",
                "grade_familiar": self.grade_familiar or "Não informado",
                "is_familiar": self.is_familiar,
            }
        )

        return params

    @classmethod
    def docketing(cls, grade_familiar, is_familiar, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.grade_familiar = grade_familiar
            instance.is_familiar = is_familiar
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class MedicalLicenseEmployee(Protocol):
    """Licença Junta Médica Servidor"""

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/medicallicense.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "employee_address": get_employee_address(self.servidor_origem),
                "employee_city": get_employee_address(self.servidor_origem).municipio,
                "employee_cep": get_employee_address(self.servidor_origem).cep,
                "employee_phone": self.servidor_origem.pessoa_fisica.phone.filter(
                    tipo_telefone__in=(1, 2, 3)
                ).first()
                or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class MedicalLicenseFamiliar(Protocol):
    """Licença Junta Médica Familiar"""

    grade_familiar = models.CharField(
        max_length=100, verbose_name="Parentesco familiar"
    )

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/medicallicense.html")

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "employee_cpf": get_employee_cpf(self.servidor_origem),
                "employee_address": get_employee_address(self.servidor_origem),
                "employee_city": get_employee_address(self.servidor_origem).municipio,
                "employee_cep": get_employee_address(self.servidor_origem).cep,
                "employee_phone": self.servidor_origem.pessoa_fisica.phone.filter(
                    tipo_telefone__in=(1, 2, 3)
                ).first()
                or "Não informado",
                "grade_familiar": self.grade_familiar or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, grade_familiar, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.grade_familiar = grade_familiar
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class CompensateExpense(Protocol):
    """Requerimento de Ressarcimento de Despesas"""

    # finality
    finality = models.TextField(verbose_name="Finalidade")
    output_date = models.DateField(verbose_name="Saída", null=True, blank=True)
    return_date = models.DateField(verbose_name="Retorno", null=True, blank=True)
    # Compensate
    total_compensate = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    material = models.TextField(verbose_name="Material")
    service = models.TextField(verbose_name="Serviço")
    combustible = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    note = models.TextField(verbose_name="Observação")

    @property
    def _template_renderer(self):
        return loader.get_template("edocs/requestform/compensate-expense.html")

    def validate(self):
        if self.compensate_item.filter(
            nota=None,
            company=None,
            venc_date_nf=None,
            nota_material=False,
            nota_service=False,
            value=0,
        ).exists():
            raise Exception(
                "Em ao menos um dos ressarcimentos não foi apontada nenhuma finalidade"
            )

    @property
    def params(self):
        params = super().params
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        params.update(
            {
                "employee_name": str(self.interessado),
                "employee_number": get_employee_number(self.servidor_origem),
                "employee_job_title": get_employee_job_position(self.servidor_origem),
                "home_court_unicode": str(self.orgao_geral_origem),
                "employee_work_email": get_employee_work_email(self.servidor_origem),
                "finality": self.finality or "Não informado",
                "output_date": DateUtils.date_to_str(self.output_date)
                or "Não informado",
                "return_date": DateUtils.date_to_str(self.return_date)
                or "Não informado",
                "total_compensate": str(
                    locale.currency(self.total_compensate, grouping=True, symbol=None)
                )
                or 0,
                "material": self.material or "Não informado",
                "service": self.service or "Não informado",
                "combustible": str(self.combustible) or 0,
                "note": self.note or "Não informado",
                "compensate_expense_items": self.compensate_item.all(),
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        finality,
        output_date,
        return_date,
        total_compensate,
        material,
        service,
        combustible,
        note,
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.validate()
            instance.finality = finality
            instance.output_date = output_date
            instance.return_date = return_date
            instance.total_compensate = total_compensate
            instance.material = material
            instance.service = service
            instance.combustible = combustible
            instance.note = note
            instance.save()

        return instance

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class CompensateExpenseItem(models.Model):
    """Requerimento de Ressarcimento de Despesas Item"""

    compensate_item = models.ForeignKey(
        CompensateExpense,
        verbose_name="Ressarcimento",
        related_name="compensate_item",
        on_delete=models.CASCADE,
    )
    nota = models.CharField(db_index=True, max_length=100, default="", blank=True)
    company = models.TextField(
        verbose_name="Nome da empresa ou do prestador do serviço",
        default="",
        blank=True,
    )
    venc_date_nf = models.DateField(
        verbose_name="Vencimento da nota fiscal", null=True, blank=True
    )
    nota_material = models.BooleanField(default=False, verbose_name="Nota de material")
    nota_service = models.BooleanField(default=False, verbose_name="Nota de serviço")
    value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
