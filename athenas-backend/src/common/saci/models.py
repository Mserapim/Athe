# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime
from io import StringIO, BytesIO
import hashlib
import os
import re

from django.conf import settings
from django.db import models, transaction
from django.template import loader
from PyPDF2 import PdfReader

from contrib.middleware import get_current_user
from contrib.utils import getLogger, person_from_user, employee_from_user
from edocs.protocolo.models import LegalSign
from edocs.protocolo.models import Protocolo, Movimentacao, TipoDocumento
from rh.models import Pessoa as Person, OrgaoGeral, Lotacao, Servidor
from standard.models import AuditTimestampModel
from standard.models import Configuration


log = getLogger(__name__)


class Typology(AuditTimestampModel):
    name = models.CharField(max_length=200, verbose_name="nome")

    class Meta:
        verbose_name = "Tipologia de Público Alvo"
        ordering = ["name"]

    def __str__(self):
        return "%s" % self.name


class Attendance(AuditTimestampModel):

    protocol = models.OneToOneField(
        Protocolo, null=True, blank=True, on_delete=models.PROTECT
    )
    person = models.ForeignKey(
        Person,
        verbose_name="pessoa",
        related_name="in_attendance",
        on_delete=models.PROTECT,
    )
    typology = models.ForeignKey(
        Typology,
        verbose_name="Tipologia",
        related_name="in_attendance",
        on_delete=models.PROTECT,
    )
    represented = models.ForeignKey(
        Person,
        verbose_name="representado",
        related_name="in_attendance_represented",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    department = models.ForeignKey(
        OrgaoGeral,
        verbose_name="departamento",
        related_name="in_attendance_department",
        on_delete=models.PROTECT,
    )
    destination = models.ForeignKey(
        OrgaoGeral,
        verbose_name="destinação",
        related_name="in_attendance_destination",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    contains_represented = models.BooleanField(
        default=False, verbose_name="possui representado"
    )
    competence_others = models.BooleanField(
        default=False, verbose_name="competência do órgão"
    )
    deleted = models.BooleanField(default=False, db_index=True)
    confidential = models.BooleanField(default=False)

    subject = models.CharField(max_length=200, verbose_name="assunto")
    story = models.TextField(verbose_name="relato do cidadão", null=True, blank=True)
    feedback = models.TextField(verbose_name="parecer", blank=True)
    content = models.TextField(blank=True)

    signed_content = models.TextField(null=True, blank=True)
    signed_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Atendimento"
        ordering = ["-created_at"]
        permissions = (
            ("can_sign_attendance", "Pode assinar atendimento"),
            (
                "can_generate_reports_all_location",
                "Pode gerar relatório de todos os locais",
            ),
        )

    def __str__(self):
        return "%s" % self.subject

    @property
    def state_icon(self):
        rst = {}

        if self.protocol.out_court_lawsuits.exists():
            rst.update(
                title="Atendimento faz parte de um processo E-EXT",
                iconCls="icon-saci icon-saci-doc-process",
            )
        elif self.is_read_only:
            if self.competence_others:
                rst.update(
                    title="Termo de encaminhamento",
                    iconCls="icon-saci icon-saci-attendance-forward-external",
                )
            else:
                rst.update(
                    title="Atendimento finalizado",
                    iconCls="icon-saci icon-saci-doc-signed",
                )
        else:
            rst.update(
                title="Atendimento em aberto",
                iconCls="icon-saci icon-saci-attendance-editable",
            )

        return rst

    @property
    def icons(self):
        return [self.state_icon]

    @property
    def is_editable(self):
        return self.is_read_only

    def movement(self, destination=None, justification=None, employee=None):
        if not (destination and justification):
            raise Exception("Falta informações para realizar o encaminhamento.")

        self.validate_out_court_lawsuits()

        Step.create(
            attendance=self,
            destination=destination,
            annotation=justification,
            employee=employee,
        )
        self.department = destination
        self.save()

    def finalize(
        self, destination=None, competence_others=False, feedback="", employee=None
    ):

        if destination is None:
            self.destination = self.department
        else:
            self.destination = destination

        self.competence_others = competence_others
        self.feedback = feedback
        self.sign(employee=employee)

    def after_generate_lawsuit(self):
        with transaction.atomic():
            self.signed_content = self.content = self._render_content()
            self.signed_by = get_current_user()
            self.signed_at = datetime.now()
            self._check = False
            self._run_docketing = False
            self.save()
            self.sign_document()
            Step.create(
                attendance=self,
                destination=self.department,
                annotation="Foi criado um procedimento Extrajudicial.",
                employee=employee_from_user(get_current_user()),
            )

    def can_sign(self):
        if not get_current_user().has_perm("saci.can_sign_attendance"):
            raise Exception("Você não tem permissão para assinar o atendimento.")

        return True

    def check_to_sign(self):
        self.can_sign()
        self.validate_represented()
        self.validate_story()
        self.validate_out_court_lawsuits()

    def sign(self, employee=None):
        self.check_to_sign()
        self.validate_feedback()
        self.validate_destination()
        with transaction.atomic():
            self.signed_content = self.content = self._render_content()
            self.signed_by = get_current_user()
            self.signed_at = datetime.now()
            self.save()
            self.send_to()
            self.sign_document()
            Step.create(
                attendance=self,
                destination=self.destination,
                annotation=self.feedback,
                employee=employee,
            )

    def sign_document(self):
        AttendanceLegalSign.sign(self)

    def send_to(self):
        movement = self.protocol.movimentacoes.first()

        movement.do_send(
            person_destination=[], advice=self.feedback, close=True, with_workflow=True
        )

    def docketing(self):
        with transaction.atomic():
            cfg = Configuration.get_or_create("saci")

            movement = self.protocol.movimentacoes.first() if self.protocol else None

            if movement:
                Movimentacao.objects.filter(pk=movement.pk).update(
                    data_encaminhamento=datetime.now(),
                    data_recebimento=datetime.now(),
                    lotacao_origem=self.department,
                    lotacao_destino=self.department,
                    parecer=self.content,
                    servidor_origem=employee_from_user(get_current_user()),
                    servidor_destino=employee_from_user(get_current_user()),
                    destinatario=person_from_user(get_current_user()),
                    with_workflow=True,
                )
                movement.refresh_from_db()

            self.protocol = Protocolo.docketing(
                subject=self.subject,
                movement_id=movement.id if movement else None,
                document_type=TipoDocumento.objects.get(
                    pk=int(cfg.get("documentType") or 0)
                ),
                interested=self.represented if self.represented else self.person,
                home_court=self.department,
                content=self.content,
                with_workflow=True,
            )

    def validate_typology(self):
        if not self.typology:
            raise Exception('O "Público Alvo" deve ser informado.')

    def validate_department(self):
        if not self.department:
            raise Exception('O "Atuando por" deve ser informado.')

    def validate_represented(self):
        if self.contains_represented and not self.represented:
            raise Exception('O "Representado" deve ser informado.')

    def validate_destination(self):
        """Verifica se o destinatário do atendimento foi definido. Tambem faz validação para os casos que o destino do atendimento
        seja um orgao externo mas seja definido um órgao interno, dessa forma deverá ser lançado um Exception.
        Da mesma forma que o destino seja marcado como interno, e seja definido um órgao externo.
        """
        if not self.destination:
            raise Exception('O "Destinado a" deve ser informado.')
        else:
            if self.competence_others and hasattr(self.destination, "lotacao"):
                raise Exception("O orgão de destino deve ser externo.")
            elif not self.competence_others and not hasattr(
                self.destination, "lotacao"
            ):
                raise Exception("O orgão de destino deve ser interno.")

    def validate_feedback(self):
        if self.competence_others and (
            self.feedback == "<p><br></p>" or self.feedback == ""
        ):  # melhorar as verificações
            raise Exception("Não é possível finalizar o atendimento sem um parecer.")

    def validate_story(self):
        if self.story == "<p><br></p>" or self.story == "":  # melhorar a verificação
            raise Exception('O campo "Relato do Cidadão" deve ser preenchido.')

    def validate_subject(self):
        if not self.subject:
            raise Exception('O campo "Assunto" deve ser preenchido')

    def validate_initial(self):
        if self.pk:
            self.validate_out_court_lawsuits()
            older = self.__class__.objects.get(pk=self.pk)
            if older.is_read_only:
                raise Exception("Atendimento não pode ser modificado.")
        self.validate_represented()

    def validate_out_court_lawsuits(self):
        if self.protocol.out_court_lawsuits.exists():
            raise Exception(
                "Esse Atendimento faz parte de um processo. Logo não pode ser modificado, finalizado ou encaminhado."
            )

    def delete(self, *args, **kwags):
        if self.has_protocol:
            raise Exception("Atendimento protocolado não pode ser removido.")

        super(Attendance, self).delete(*args, **kwags)

    def save(self, *args, **kwargs):
        if self.pk and not self.can_read:
            raise Exception("Este documento possui controle de acesso.")

        if getattr(self, "_check", True):
            self.validate_initial()

        self.content = self._render_content()

        if getattr(self, "_run_docketing", True):
            self.docketing()

        super().save(*args, **kwargs)

    @property
    def is_read_only(self):
        return self.signed_by

    @property
    def has_protocol(self):
        return self.protocol

    def _render_content(self):
        tpl = loader.get_template(self.template)
        endereco_destino = (
            self.destination.address.first() if self.destination else None
        )
        telefone_destino = self.destination.phone.first() if self.destination else None

        return tpl.render(
            {
                "doc": self,
                "localidade": Lotacao.objects.get(pk=self.department.pk).localidade,
                "attendant_by": person_from_user(get_current_user()),
                "attendant_at": datetime.now(),
                "endereco_destino": endereco_destino,
                "telefone_destino": telefone_destino,
            }
        )

    @property
    def template(self):
        return "saci/content.html"

    @property
    def rendered(self):
        if self.can_read:
            return loader.get_template("saci/attendance.html").render(
                {"instance": self}
            )
        else:
            return loader.get_template("protocolo/access-denied.html").render(
                {"protocol": self.protocol}
            )

    @property
    def appends_of_document(self):
        if self.can_read:
            rendered = loader.get_template("saci/steps.html").render({"doc": self})
            return [rendered] if rendered else []
        else:
            return []

    @property
    def extra_pages_attached(self):
        pages = []

        for attached in self.attached.filter():
            pages += attached.extract_pages()

        return pages

    @property
    def extra_pages(self):
        pages = self.extra_pages_attached
        return [
            page.get("page")
            for page in sorted(pages, key=lambda d: d.get("at") or datetime.now())
        ]

    @property
    def can_read(self):
        """Retorna True se o usuário corrente estiver autorizado a ler
        o conteúdo do documento. Caso contrário, retorna False.

        Verifica se este procotolo possui controle de acesso. Se possui,
        então verifica se o usuário corrente está autorizado a ler o seu
        conteúdo. Mas se não existe controle de acesso, retorna True por
        padrão.
        """
        if hasattr(self, "attendance_control"):
            return self.attendance_control.can_read
        return True


class AttendanceLegalSign(LegalSign):
    attendance = models.ForeignKey(
        Attendance, related_name="legal_signs", on_delete=models.PROTECT
    )

    def _fill(self, attendance):
        LegalSign._fill(self)
        self.attendance = attendance
        self.plain_content = self.attendance.signed_content
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha1", self.content).hexdigest()

    @classmethod
    def sign(klass, attendance):
        obj = klass()
        obj._fill(attendance)
        obj.save()


class Step(AuditTimestampModel):
    attendance = models.ForeignKey(
        Attendance, related_name="steps", on_delete=models.PROTECT
    )
    origin = models.ForeignKey(
        OrgaoGeral,
        verbose_name="Origem",
        related_name="step_origin",
        on_delete=models.PROTECT,
    )
    destination = models.ForeignKey(
        OrgaoGeral,
        verbose_name="Destino",
        related_name="step_destination",
        on_delete=models.PROTECT,
    )
    annotation = models.TextField(verbose_name="Anotação")
    employee = models.ForeignKey(
        Servidor, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Passo"
        ordering = ["-created_at"]

    def __str__(self):
        return "Passo - %s " % self.attendance

    @classmethod
    def create(cls, attendance=None, destination=None, annotation=None, employee=None):
        if attendance is None:
            raise Exception("Não é possível criar o Passo do atendimento")

        obj = cls()
        obj.attendance = attendance
        obj.origin = attendance.department
        obj.destination = destination
        obj.annotation = annotation
        obj.employee = employee
        obj.save()

    @property
    def rendered(self):
        if self.attendance.can_read:
            return self.annotation
        else:
            return "<strong>CONTEÚDO RESTRITO</strong>"

    @property
    def who_person(self):
        if person_from_user(self.created_by, False):
            return str(person_from_user(self.created_by, False).nome)


class Attachment(AuditTimestampModel):
    # Parametro "on_delete" adicionado. (Django 2)
    attendance = models.ForeignKey(
        Attendance, related_name="attached", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100, blank=True, null=True)
    file_descriptor = models.ForeignKey(
        "ged.arquivo", related_name="+", on_delete=models.PROTECT
    )
    observation = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("created_at",)

    def process_renderer_pages(self):
        drivers = {
            r"^application\/(pdf|octet\-stream|force\-download)$": self.process_renderer_pages_of_protable_document,
        }

        processor = None
        for test, fn in list(drivers.items()):
            if re.match(test, self.file_descriptor.mimetype):
                processor = fn
                break

        (processor if processor else lambda: None)()

    def process_renderer_pages_of_protable_document(self):
        from common.saci.tasks import (
            process_renderer_pages_of_protable_document_executor as executor,
        )

        filebase = self.file_descriptor.absolute_path

        log.info("processing pages of protable document")
        log.info("filename: %s", filebase)

        cachedir = os.path.join(
            getattr(settings, "CACHE_BASE", ""), "ejud", self.file_descriptor.file
        )

        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

        if os.path.exists(filebase):
            pdf_fd = PdfReader(open(filebase, "rb"), strict=False)
            if pdf_fd.isEncrypted:
                pdf_fd.descrypt("")

            log.info("Número de páginas: %d", pdf_fd.numPages)

            for start in range(0, pdf_fd.numPages, 10):
                end = start + 10

                if end > pdf_fd.numPages:
                    end = pdf_fd.numPages

                executor.delay(filebase, os.path.join(cachedir, "%05d.jpg"), start, end)
        else:
            log.info("file cache not found")

    def extract_pages(self):
        drivers = {
            r"^application\/(pdf|octet\-stream|force\-download)$": self.extract_pages_of_portable_document,
            r"^image\/(png|jpeg|jpg|gif)$": self.extract_pages_of_image,
        }
        log.info("chamou")
        extractor = self.extract_pages_of_fallback
        for test, fn in list(drivers.items()):
            if re.match(test, self.file_descriptor.mimetype):
                extractor = fn
                break

        return extractor()

    def extract_pages_of_portable_document(self):
        cachedir = os.path.join(
            os.path.join(getattr(settings, "CACHE_BASE", ""), "ejud"),
            self.file_descriptor.file,
        )
        pages = []
        page = (
            '<div style="margin: -15mm -20mm;'
            "width: 210mm;"
            "height: 297mm;"
            "background: url('/athenas/static/judicial-cache/%s/%s') center center no-repeat\">"
            "</div>"
        )

        try:
            if os.path.exists(cachedir):
                pages += [
                    {
                        "page": page % (self.file_descriptor.file, filename),
                        "at": self.created_at,
                    }
                    for filename in sorted(os.listdir(cachedir))
                ]
        except Exception as e:
            return [{"page": "%s" % e, "at": self.file_descriptor.created}]
        else:
            return pages

    def extract_pages_of_image(self):
        from PIL import Image
        from base64 import b64encode

        tpl = loader.get_template("saci/attached_page.html")

        pages = [{"page": tpl.render({"attached": self}), "at": self.created_at}]

        try:
            filepath = self.file_descriptor.absolute_path
            img_fd = Image.open(filepath)

            log.info("filename: %s", filepath)
            if img_fd.size[0] > 720 and img_fd.size[0] > img_fd.size[1]:
                img_fd = img_fd.transpose(Image.ROTATE_90)

            if img_fd.size[0] > 720:
                scale = 720.0 / img_fd.size[0]
                img_fd = img_fd.resize(
                    [720, int(scale * img_fd.size[1])], Image.LANCZOS
                )

            if img_fd.size[1] > 980:
                scale = 980.0 / img_fd.size[1]
                img_fd = img_fd.resize(
                    [int(scale * img_fd.size[0]), 980], Image.LANCZOS
                )

            data = BytesIO()
            img_fd.save(data, img_fd.format)

            page = (
                '<div style="margin: -15mm -20mm;'
                "width: 210mm;"
                "height: 297mm;"
                'background: url(data:%s;base64,%s) center center no-repeat">'
                "</div>"
            ) % (Image.MIME[img_fd.format], b64encode(data.getvalue()).decode())
        except Exception as e:
            log.exception(e)
            page = f"<p>{e}</p>"

        pages.append({"page": page, "at": self.created_at})

        return pages

    def extract_pages_of_fallback(self):
        tpl = loader.get_template("saci/attached_page.html")

        return [{"page": tpl.render({"attached": self}), "at": self.created_at}]

    def delete(self, *args, **kwargs):
        if self.attendance.is_read_only:
            raise Exception("Não posso modificar um anexo de um documento assinado.")

        super(Attachment, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.attendance:
            raise Exception("Não posso criar uma anexo sem um atendimento.")

        if not self.title:
            self.title = self.file_descriptor.filename
        log.info(getattr(self, "skip_read_only_validate", False))
        # if not getattr(self, 'skip_read_only_validate', False) and self.owner.read_only:
        if (
            not getattr(self, "skip_read_only_validate", False)
            and self.attendance.is_read_only
        ):
            raise Exception("Não posso modificar um anexo de um documento assinado.")

        super(Attachment, self).save(*args, **kwargs)

        from common.saci.tasks import process_attached_document

        process_attached_document.delay(self.pk)
