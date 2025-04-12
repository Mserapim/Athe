# -*- coding: utf-8 -*-
from django.db import models, transaction
from django.template import loader

from contrib.utils import getLogger
from edocs.protocolo.models import Attachment
from edocs.protocolo.models import Protocolo as Protocol
from ged.models import Arquivo as File
from rh.models import Localidade as City

log = getLogger()


class APIProtocol(Protocol):
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def docketing(cls, ip_address, files={}, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(*args, **kwargs)
            instance.ip_address = ip_address
            instance.save()

            movement = instance.movimentacoes.first()

            for name, upfile in files.items():
                title = name

                Attachment.objects.create(
                    title=title,
                    protocol=instance,
                    moviment=movement,
                    attach=File.create_ged(upfile),
                )

            movement.do_send(
                location_destination=[instance.orgao_geral_origem.pk],
                employee_origin=instance.servidor_origem,
            )

        return instance

    @property
    def params(self):
        params = super().params

        return params

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.special_type = self._meta.model_name

        super().save(
            force_insert=force_insert, force_update=force_update, *args, **kwargs
        )


class OmbudsmanAnonymous(APIProtocol):
    pass


class OmbudsmanCitizen(APIProtocol):
    live_in_referenced_city = models.BooleanField(default=True)
    referenced_city = models.ForeignKey(
        City,
        related_name="ombudsmancitizen_manifestations",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    @property
    def _template_renderer(self):
        return loader.get_template("apiprotocol/ombudsman-citizen-manifestation.html")

    @property
    def params(self):
        from edocs.protocolo.apiprotocol.forms import CHOICES

        params = super().params
        params.update(
            {
                "zipcode": self.interessado.address.last().cep or "Não Informado",
                "phone_number": self.interessado.pessoafisica.phone.last()
                or "Não Informado",
                "cpf": self.interessado.pessoafisica.cpf,
                "genre": dict(CHOICES["GENRE"]).get(
                    self.interessado.pessoafisica.sexo, "Não informado"
                ),
                "education_level": dict(CHOICES["EDUCATION_LEVEL"]).get(
                    self.interessado.pessoafisica.grau_instrucao, "Não Informado"
                ),
                "live_in_referenced_city": (
                    "Sim" if self.live_in_referenced_city else "Não"
                ),
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        ip_address,
        live_in_referenced_city,
        referenced_city,
        files={},
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(ip_address, files=files, *args, **kwargs)
            instance.live_in_referenced_city = live_in_referenced_city
            instance.referenced_city = referenced_city
            instance.save()

        return instance


class OmbudsmanLegalPerson(APIProtocol):
    @property
    def _template_renderer(self):
        return loader.get_template(
            "apiprotocol/ombudsman-legal-person-manifestation.html"
        )

    @property
    def params(self):
        params = super().params

        params.update(
            {
                "zipcode": self.interessado.address.last().cep or "Não Informado",
                "phone_number": self.interessado.pessoajuridica.phone.last()
                or "Não Informado",
                "cnpj": self.interessado.pessoajuridica.cnpj,
            }
        )

        return params


class OnlineProtocolCitizen(APIProtocol):
    subject_detail = models.CharField(max_length=255)
    document_number = models.CharField(max_length=100)
    live_in_referenced_city = models.BooleanField(default=True)
    referenced_city = models.ForeignKey(
        City,
        related_name="onlineprotocolcitizen_manifestations",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    @property
    def _template_renderer(self):
        return loader.get_template(
            "apiprotocol/online-protocol-citizen-manifestation.html"
        )

    @property
    def params(self):
        from edocs.protocolo.apiprotocol.forms import ONLINE_PROTOCOL_CHOICES

        params = super().params
        params.update(
            {
                "zipcode": self.interessado.address.last().cep or "Não Informado",
                "phone_number": self.interessado.pessoafisica.phone.last()
                or "Não Informado",
                "cpf": self.interessado.pessoafisica.cpf,
                "genre": dict(ONLINE_PROTOCOL_CHOICES["GENRE"]).get(
                    self.interessado.pessoafisica.sexo, "Não informado"
                ),
                "education_level": dict(ONLINE_PROTOCOL_CHOICES["EDUCATION_LEVEL"]).get(
                    self.interessado.pessoafisica.grau_instrucao, "Não Informado"
                ),
                "city": self.interessado.address.last().municipio,
                "live_in_referenced_city": (
                    "Sim" if self.live_in_referenced_city else "Não"
                ),
                "referenced_city": self.referenced_city or "Não Informado",
                "subject_detail": self.subject_detail or "Não Informado",
                "document_number": self.document_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(
        cls,
        ip_address,
        subject_detail,
        document_number,
        live_in_referenced_city,
        referenced_city,
        files={},
        *args,
        **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(ip_address, files=files, *args, **kwargs)
            instance.subject_detail = subject_detail
            instance.document_number = document_number
            instance.live_in_referenced_city = live_in_referenced_city
            instance.referenced_city = referenced_city
            instance.save()

        return instance


class OnlineProtocolLegalPerson(APIProtocol):
    subject_detail = models.CharField(max_length=255)
    document_number = models.CharField(max_length=100)

    @property
    def _template_renderer(self):
        return loader.get_template(
            "apiprotocol/online-protocol-legal-person-manifestation.html"
        )

    @property
    def params(self):

        params = super().params
        params.update(
            {
                "zipcode": self.interessado.address.last().cep or "Não Informado",
                "phone_number": self.interessado.pessoajuridica.phone.last()
                or "Não Informado",
                "cnpj": self.interessado.pessoajuridica.cnpj,
                "city": self.interessado.address.last().municipio,
                "subject_detail": self.subject_detail or "Não Informado",
                "document_number": self.document_number or "Não informado",
            }
        )

        return params

    @classmethod
    def docketing(
        cls, ip_address, subject_detail, document_number, files={}, *args, **kwargs
    ):
        with transaction.atomic():
            instance = super().docketing(ip_address, files=files, *args, **kwargs)
            instance.subject_detail = subject_detail
            instance.document_number = document_number
            instance.save()

        return instance


class OnlineCertificateCitizen(APIProtocol):
    @property
    def _template_renderer(self):
        return loader.get_template("apiprotocol/online-certificate.html")

    @property
    def params(self):

        params = super().params
        email = (
            self.interessado.pessoafisica.email
            or self.interessado.pessoafisica.email_institucional
        )
        params.update(
            {
                "cpf": self.interessado.pessoafisica.cpf,
                "name": self.interessado.pessoafisica.nome,
                "email": email.lower() if email else "Não Informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, ip_address, files={}, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(ip_address, files=files, *args, **kwargs)
            instance.save()

        return instance


class OnlineCertificateLegalPerson(APIProtocol):
    @property
    def _template_renderer(self):
        return loader.get_template("apiprotocol/online-certificate.html")

    @property
    def params(self):

        params = super().params
        email = self.interessado.pessoajuridica.email
        params.update(
            {
                "cnpj": self.interessado.pessoajuridica.cnpj,
                "name": self.interessado.pessoajuridica.razao_social
                or self.interessado.pessoajuridica.nome,
                "email": email.lower() if email else "Não Informado",
            }
        )

        return params

    @classmethod
    def docketing(cls, ip_address, files={}, *args, **kwargs):
        with transaction.atomic():
            instance = super().docketing(ip_address, files=files, *args, **kwargs)
            instance.save()

        return instance
