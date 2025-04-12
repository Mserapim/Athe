# -*- coding: utf-8 -*-
import hashlib
import os
from datetime import datetime

from contrib.middleware import get_current_user
from django.db import models
from django.template import loader
from rh.models import Cargo
from standard.models import Choice, Configuration


class FunctionalId(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Empregado",
        related_name="have_functional_ids",
        on_delete=models.CASCADE,
    )
    functional_type = models.SmallIntegerField(
        verbose_name="Tipo",
        default=1,
        choices=Choice.get_choices_for("functional_id", "FUNCTIONAL_ID_TYPE"),
    )
    # Parametro "on_delete" adicionado. (Django 2)
    photo = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Foto",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # Parametro "on_delete" adicionado. (Django 2)
    employee_sign_image = models.ForeignKey(
        "ged.Arquivo", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    validator_sign_image = models.ForeignKey(
        "ged.Arquivo", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    signed_by = models.ForeignKey(
        "auth.User",
        verbose_name="Assinado por",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # Parametro "on_delete" adicionado. (Django 2)
    signed_at = models.DateTimeField(verbose_name="Assinado", null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    revoked_by = models.ForeignKey(
        "auth.User",
        verbose_name="Revogado por",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    revoked_at = models.DateTimeField(verbose_name="Revogado", null=True, blank=True)
    name = models.CharField(verbose_name="Nome", max_length=200, null=True, blank=True)
    employee_registration = models.CharField(
        verbose_name="Matricula", max_length=60, null=True, blank=True
    )
    ingress_date = models.DateField(
        verbose_name="Data de ingresso", null=True, blank=True
    )
    mother_name = models.CharField(
        verbose_name="Nome da mãe", max_length=200, null=True, blank=True
    )
    father_name = models.CharField(
        verbose_name="Nome do pai", max_length=200, null=True, blank=True
    )
    born_date = models.DateField(
        verbose_name="Data de nascimento", null=True, blank=True
    )
    born_location = models.ForeignKey(
        "rh.Localidade",
        on_delete=models.CASCADE,
        verbose_name="Local de nascimento",
        related_name="+",
        null=True,
        blank=True,
    )  # Parametro "on_delete" adicionado. (Django 2)
    national_id_number = models.CharField(
        verbose_name="CPF", max_length=11, null=True, blank=True
    )
    local_id_number = models.CharField(
        verbose_name="RG", max_length=200, null=True, blank=True
    )
    local_id_issuance = models.CharField(
        verbose_name="RG expedido por", max_length=200, null=True, blank=True
    )
    blood_group = models.CharField(
        verbose_name="Tipo sanguineo", max_length=5, null=True, blank=True
    )
    organ_donor = models.BooleanField(verbose_name="Doador de órgão", default=False)
    job_position = models.CharField(
        verbose_name="Cargo", max_length=100, null=True, blank=True
    )
    version = models.CharField(
        verbose_name="Versão", max_length=10, blank=True, null=True
    )
    signatory = models.ForeignKey(
        "rh.Cargo",
        verbose_name="Signatário",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    delivered_by = models.ForeignKey(
        "auth.User",
        verbose_name="Entregue por",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    delivered_at = models.DateTimeField(
        verbose_name="Entregue em", null=True, blank=True
    )
    status = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("functional_id", "FUNCTIONAL_ID_STATUS"),
        default=1,
        verbose_name="Estado",
    )

    class Meta:
        ordering = ("-revoked_at", "-signed_at", "employee__pessoa_fisica__nome")
        permissions = (
            ("can_sign_functional_id", "Pode assinar carteiras funcionais."),
            ("can_revoke_functional_id", "Pode revogar carteiras funcionais."),
        )

    STATES = [
        None,
        ("editando", (2,)),
        ("confeccionando", (3, 4)),
        ("revogado", []),
        ("entregue", (3,)),
    ]

    def change_status(self, state, input):
        """
        (name, allowed)
               allowed => list of states
        """

        now, allowed = self.STATES[state]

        if input in allowed:
            return input
        else:
            dest = self.STATES[input][0]
            raise Exception("Não é permitido mudar de %s para %s" % (now, dest))

    @property
    def icons(self):
        ICONS_MAP = {
            1: {
                "title": self.get_status_display(),
                "iconCls": "icon-common icon-fid-in-edition",
            },
            2: {
                "title": self.get_status_display(),
                "iconCls": "icon-common icon-fid-waiting-print",
            },
            3: {
                "title": self.get_status_display(),
                "iconCls": "icon-common icon-fid-revoked",
            },
            4: {
                "title": self.get_status_display(),
                "iconCls": "icon-common icon-fid-delivered",
            },
        }

        return [ICONS_MAP.get(self.status)]

    @property
    def content(self):
        return loader.get_template("functional_id/preview.html").render({"fid": self})

    @property
    def read_only(self):
        return not (self.signed_by is None)

    @property
    def is_allowed_sign(self):
        user = get_current_user()
        return user.has_perm("functional_id.can_sign_functional_id")

    @property
    def is_allowed_revoke(self):
        user = get_current_user()
        return user.has_perm("functional_id.can_revoke_functional_id")

    def sign(self):
        if self.signed_by:
            raise Exception("Esta Carteira Funcional já foi assinada.")

        if not self.is_allowed_sign:
            raise Exception("Você não tem autorização para assinar Carteira Funcional.")

        query = self.__class__.objects.filter(
            employee=self.employee, revoked_by=None
        ).exclude(signed_by=None)

        if query.exists():
            raise Exception(
                "O servidor %s já tem uma carteira válida."
                % self.employee.pessoa_fisica
            )

        """
        Possibilita a geração de (1.099.511.627.776) de versões.
        """
        self.version = hashlib.new("sha3-224", os.urandom(8192)).hexdigest()[-10:]
        self.signed_by = get_current_user()
        self.signed_at = datetime.now()
        self.skip_ready_only_validation = True
        self.status = self.change_status(self.status, 2)
        self.save()

    def deliver(self):
        if self.delivered_at:
            raise Exception("Essa Carteira Funcional já foi entregue")

        if not self.signed_by:
            raise Exception(
                "Só posso entregar uma Carteira Funcional que já tenha sido assinada"
            )

        if self.revoked_by:
            raise Exception(
                "Esta Carteira Funcional não pode ser entregue, pois já foi revogada."
            )

        # if not self.is_allowed_revoke and not self.is_allowed_sign:
        #     raise Exception('Você não tem autorização para revogar Carteira Funcional.')

        self.delivered_by = get_current_user()
        self.delivered_at = datetime.now()
        self.skip_ready_only_validation = True
        self.status = self.change_status(self.status, 4)
        self.save()

    def revoke(self):
        if not self.signed_by:
            raise Exception(
                "Só posso revogar uma Carteira Funcional que já tenha sido emitida"
            )

        if self.revoked_by:
            raise Exception("Esta Carteira Funcional já foi revogada.")

        if not self.is_allowed_revoke and not self.is_allowed_sign:
            raise Exception("Você não tem autorização para revogar Carteira Funcional.")

        self.revoked_by = get_current_user()
        self.revoked_at = datetime.now()
        self.skip_ready_only_validation = True
        self.status = self.change_status(self.status, 3)
        self.save()

    @classmethod
    def _job_position(klass, employee, default_value=None):
        job_position = default_value

        if employee.job_position():
            job_position = str(employee.job_position())

        return job_position

    @classmethod
    def _local_id_issuance(klass, person, default_value=None):
        issuance = default_value

        if (
            person.rg_document
            and person.rg_document.dados_especificos.filter(especificidade=13).exists()
        ):
            issuance = person.rg_document.dados_especificos.get(especificidade=13).valor

        return issuance

    def _fill_by_employee(self):
        employee = self.employee
        person = self.employee.pessoa_fisica
        rg_doc = person.rg_document

        self.functional_type = 2 if employee.tipo == "M" else 1
        self.photo = person.foto
        self.name = str(person)
        self.employee_registration = employee.matricula
        self.mother_name = person.nome_mae
        self.father_name = person.nome_pai
        self.born_date = person.data_nascimento
        self.born_location = person.municipio_naturalidade
        self.local_id_number = rg_doc.numero
        self.local_id_issuance = "/".join(
            [
                self._local_id_issuance(person, ""),
                rg_doc.estado_expedicao.sigla if rg_doc.estado_expedicao else "",
            ]
        )
        self.organ_donor = person.doador
        self.blood_group = "".join(
            [person.get_sangue_display(), person.get_fator_rh_display()]
        )
        self.job_position = self._job_position(employee)
        self.ingress_date = employee.data_exercicio
        self.national_id_number = employee.pessoa_fisica.cpf

        cfg = Configuration.get_or_create("fid")
        signatory_job_position = cfg.get("signatory_job_position")
        if signatory_job_position:
            self.signatory = Cargo.objects.get(pk=signatory_job_position)

    def save(self, *args, **kwags):
        if not self.pk:
            self._fill_by_employee()

        if self.read_only and not getattr(self, "skip_ready_only_validation", False):
            raise Exception(
                "Esta Carteira Funcional já foi assinada e não pode ser modificada."
            )

        super(FunctionalId, self).save(*args, **kwags)
