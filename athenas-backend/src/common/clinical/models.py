import os
import hashlib

from base64 import b64encode
from django.db import models
from edocs.protocolo.models import LegalSign
from standard.models import AuditTimestampModel
from rh.models import PessoaFisica, Servidor, Dependente, Endereco
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger
from datetime import date, datetime
from django.template import loader
from django.conf import settings
from contrib.decorator import ilru_cache

log = getLogger(__name__)


class Doctor(AuditTimestampModel):
    person = models.OneToOneField(
        PessoaFisica, related_name="has_doctor", on_delete=models.PROTECT
    )
    medical_identify = models.CharField(max_length=100, db_index=True, blank=True)
    phone = models.CharField(max_length=15, null=True)

    def __str__(self):
        return str(self.person)

    def _fill_medical_identify(self):
        try:
            id_number = str(int(self.person.professional_council.numero))
            id_entity = str(self.person.professional_council.estado_expedicao)

            self.medical_identify = "/".join([id_number, id_entity])
        except:
            pass

    def save(self, *args, **kwargs):
        if not self.medical_identify:
            self._fill_medical_identify()

        super().save(*args, **kwargs)


class Prescription(AuditTimestampModel):
    doctor = models.ForeignKey(
        Doctor,
        related_name="emmited_prescriptions",
        on_delete=models.PROTECT,
        blank=True,
    )
    partner = models.ForeignKey(
        Servidor,
        related_name="my_prescriptions_has_partner",
        on_delete=models.PROTECT,
        blank=True,
    )
    patient = models.ForeignKey(
        PessoaFisica, related_name="my_prescriptions", on_delete=models.PROTECT
    )
    signed_by = models.ForeignKey(
        "auth.User",
        related_name="as_sign_of_prescriptions",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    signed_at = models.DateTimeField(blank=True, null=True)
    prescription = models.TextField(null=True)
    prescription_number = models.IntegerField(blank=True)
    prescription_year = models.IntegerField(blank=True)
    cache_number = models.CharField(max_length=20, unique=True, blank=True)
    cache_rendered = models.TextField(null=True, blank=True)
    delivery_state = models.SmallIntegerField(
        default=1,
        choices=((1, "edit"), (2, "available"), (3, "manufactured"), (4, "dispatched")),
    )
    file_description = models.ForeignKey(
        "ged.Arquivo", null=True, blank=True, on_delete=models.PROTECT
    )
    protocol = models.ForeignKey(
        "protocolo.Protocolo", null=True, blank=True, on_delete=models.PROTECT
    )

    class Meta:
        ordering = (
            "-prescription_year",
            "-prescription_number",
        )

    @property
    def cache_directory(self):
        return os.path.join(settings.CACHE_BASE, "clinical")

    @property
    def cache_filepath(self):
        return os.path.join(
            self.cache_directory,
            "%d.%05d" % (self.prescription_year, self.prescription_number),
        )

    @property
    def cache_lock_filepath(self):
        return "%s.lock" % self.cache_filepath

    def sign(self):
        LegalSignPrescription.sign(self)

        self.cache_rendered = self._render()
        self.signed_by = get_current_user()
        self.signed_at = datetime.now()
        self.delivery_state = 2
        self.save()

    @ilru_cache()
    def _address_by_employee(self, employee):
        if employee:
            query = Endereco.objects.filter(
                models.Q(person=employee.pessoa_fisica) & models.Q(tipo_endereco=1)
            )

            if query.exists():
                return query.first()

        return None

    @property
    def partner_address(self):
        return self._address_by_employee(self.partner)

    @ilru_cache()
    def _doctor_employee(self):
        try:
            return self.doctor.person.servidor_set.get(ativo=True)
        except:
            return None

    @property
    def doctor_employee(self):
        return self._doctor_employee()

    @property
    def doctor_workplace(self):
        return self._doctor_employee().work_locations.first()

    @property
    def doctor_address(self):
        return self._address_by_employee(self._doctor_employee())

    def _render(self):
        tpl = loader.get_template("clinical/prescription.html")

        return tpl.render(
            {
                "me": self,
                "sign": self.signs.first(),
                "partner_address": str(self.partner_address),
                "doctor_address": str(self.doctor_address),
            }
        )

    @property
    def ready_only(self):
        return False

    @property
    def rendered(self):
        return self.cache_rendered if self.cache_rendered else self._render()

    def _fill_prescription_cache_number(self):
        current_year = date.today().year

        query = self.__class__.objects.filter(prescription_year=current_year).aggregate(
            max_number=models.Max("prescription_number")
        )

        self.prescription_year = current_year
        self.prescription_number = int(query.get("max_number") or 0) + 1
        self.cache_number = "/".join(
            [str(self.prescription_number), str(self.prescription_year)]
        )

    def _fill_partner(self):
        if self.patient.servidor_set.filter(ativo=True).exists():
            self.partner = self.patient.servidor_set.get(ativo=True)
        else:
            query = Dependente.objects.filter(
                models.Q(pessoa_fisica=self.patient)
                & models.Q(dependente_direto=True)
                & models.Q(
                    models.Q(data_fim=None) | models.Q(data_fim__gt=date.today())
                )
            )

            if query.exists():
                self.partner = query.first().servidor
            else:
                raise Exception("Não conseigo definir o conveniado")

    def _fill_doctor(self):
        employee = employee_from_user(get_current_user())

        if employee:
            self.doctor = getattr(employee.pessoa_fisica, "has_doctor", None)

    def save(self, *args, **kwargs):
        if not getattr(self, "doctor", None):
            self._fill_doctor()

        if not getattr(self, "partner", None) and self.patient:
            self._fill_partner()

        if not self.prescription_number:
            self._fill_prescription_cache_number()

        super().save(*args, **kwargs)


class LegalSignPrescription(LegalSign):
    prescription = models.ForeignKey(
        Prescription, related_name="signs", on_delete=models.PROTECT
    )

    def _fill(self, prescription):
        super()._fill()
        self.prescription = prescription
        self.plain_content = self.prescription.rendered
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha1", self.content).hexdigest()

    @classmethod
    def sign(klass, prescription):
        log.debug("Sign prescription %s", prescription)

        obj = klass()
        obj._fill(prescription)

        obj.save()
