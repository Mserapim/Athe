# -*- coding: utf-8 -*-
import os
import re
import math
import random
import time
import django
import hashlib
import json

# import pyqrcode
from subprocess import Popen, PIPE
from base64 import b64encode
from datetime import datetime, date, timedelta

from PyPDF2 import PdfReader
from celery import group
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template import loader, engines
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, F

from ged.models import Arquivo
from contrib.middleware import get_current_user
from engine.notification.models import Message, Notification
from judicial.const import TYPE_ORDINACE
from standard.models import AuditTimestampModel, Choice, Configuration
from dateutil.relativedelta import relativedelta
from auth.jwt.models import DisposableVoucher
from functools import partial
from common.document_access.models import ProtocolControl
from contrib.nil import nil_datetime, nil_person_user
from contrib.helpers import capitalize_words
from contrib.utils import getLogger, DateUtils, person_from_user, employee_from_user
from edocs.protocolo.utils import EDOCBoxQuery
from edocs.protocolo.models import (
    Protocolo,
    LegalSign,
    Movimentacao,
    TipoDocumento,
    Protocolo as Protocol,
)
from rh.models import (
    Endereco as Address,
    Pessoa,
    Lotacao,
    Localidade,
    Servidor,
    OrgaoGeral,
    ServidorLotacao,
    Publicacao as Publication,
)

from django.contrib.postgres.search import SearchVectorField


if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success

log = getLogger(__name__)


MEANING_TYPE_ACTION = 1
MEANING_TYPE_DOCUMENT = 2
MEANING_TYPE_UNDEFINED = 100


class Bloke(models.Model):
    lawsuit = models.ForeignKey(
        "OutCourtLawsuit", related_name="blokes", on_delete=models.PROTECT
    )
    my_type = models.CharField(max_length=60, db_index=True, blank=True)

    @property
    def my_bloke(self):
        return self.my_origin.bloke

    @classmethod
    def person_from_bloke_id(klass, bloke_id):
        return klass.objects.get(pk=bloke_id).my_bloke

    @property
    def my_origin(self):
        if self.pk:
            if hasattr(self, self.my_type):
                return getattr(self, self.my_type, self)
            else:
                return self
        else:
            return self

    def save(self, *args, **kwargs):
        employee = employee_from_user(get_current_user())
        if not self.lawsuit.current_moviment() and not self.lawsuit.is_acting:
            raise Exception(
                "Não posso mudar os apontados/investigados, pois, este procedimento não esta em sua posse."
            )

        self.my_type = self._meta.model_name
        super(Bloke, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.my_origin.bloke)


class BlokeAddress(models.Model):
    bloke = models.ForeignKey(
        Bloke, related_name="addresses", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    location = models.ForeignKey(
        "rh.Localidade", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    district = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    complement = models.CharField(max_length=200, null=True, blank=True)
    observation = models.TextField(blank=True)


class CommonPerson(Bloke):
    bloke = models.ForeignKey(
        "rh.pessoa", related_name="has_bloke_common", on_delete=models.PROTECT
    )


class Person(Bloke):
    bloke = models.ForeignKey(
        "rh.pessoafisica", related_name="has_bloke_person", on_delete=models.PROTECT
    )


class Association(Bloke):
    bloke = models.ForeignKey(
        "rh.pessoajuridica",
        related_name="has_bloke_association",
        on_delete=models.PROTECT,
    )


class Company(Bloke):
    bloke = models.ForeignKey(
        "rh.pessoajuridica", related_name="has_bloke_company", on_delete=models.PROTECT
    )


class GovernmentPublic(Bloke):
    bloke = models.ForeignKey(
        "rh.pessoafisica", related_name="has_bloke_government", on_delete=models.PROTECT
    )


class Tag(models.Model):
    title = models.CharField(max_length=40, blank=True, verbose_name="Título")
    slug = models.CharField(max_length=40, blank=True, verbose_name="Abreviação")
    tag_type = models.SmallIntegerField(
        verbose_name="Acesso", choices=((1, "SYSTEM"), (2, "WORK"))
    )
    work_place = models.ForeignKey(
        "rh.lotacao",
        related_name="tags",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    owner = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    classification = models.OneToOneField(
        "judicial.LegalClassification",
        related_name="has_tag",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    active = models.BooleanField(default=True)
    priority = models.SmallIntegerField(
        verbose_name="Prioridade", default=1, null=True, blank=True
    )

    class OwnerNotDefined(Exception):

        def __init__(self):
            Exception("For tag with type USER is needed a owner.")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        if int(self.tag_type or 0) == 2 and self.owner is None:
            self.owner = get_current_user()

        if int(self.tag_type or 0) == 2 and self.owner is None:
            raise self.OwnerNotDefined()

        super(Tag, self).save(*args, **kwargs)


class OutCourtLawsuit(models.Model):
    type_lawsuit = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_LAWSUIT"),
        default=1,
        verbose_name="Tipo do Procedimento",
    )
    title = models.TextField(null=True)
    """
    # FIXME: como o protocolo pode transitar para qualquer orgão geral o campo localidade
           deveria apotar para ele  e não Lotacao
    location = models.ForeignKey('rh.OrgaoGeral', related_name='lawsuit', on_delete=models.CASCADE) # Parametro "on_delete" adicionado. (Django 2)
    """
    notice_locations = models.ManyToManyField("rh.Localidade", related_name="+")
    location = models.ForeignKey(
        "rh.Lotacao", related_name="lawsuit", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    external_locations = models.ManyToManyField(
        "rh.OrgaoGeral", related_name="in_lawsuit_as_external"
    )
    main_tag = models.ForeignKey(
        Tag,
        related_name="has_main_tag_in_lawsuits",
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    tags = models.ManyToManyField(Tag, related_name="out_court_lawsuits")
    origin = models.ForeignKey(
        "protocolo.Protocolo",
        related_name="out_court_lawsuits",
        on_delete=models.PROTECT,
        null=True,
    )
    year = models.SmallIntegerField(verbose_name="Ano", null=True, blank=True)
    number_lawsuit = models.IntegerField(verbose_name="Número", null=True, blank=True)
    cache_number = models.CharField(max_length=20, verbose_name="Número/Ano")
    deadline_cache = models.DateField(null=True)
    is_criminal = models.BooleanField(default=False)
    closed_by = models.ForeignKey(
        "auth.User", related_name="closeds_lawsuit", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    closed_at = models.DateTimeField(null=True)
    attached_lawsuit = models.ForeignKey(
        "self",
        related_name="has_connected",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    removed_by = models.ForeignKey(
        "auth.user",
        related_name="has_remover_of_lawsuit",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    removed_at = models.DateTimeField(null=True)
    main_matter = models.ForeignKey(
        "judicial.LegalMatter",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    matters = models.ManyToManyField("judicial.LegalMatter", related_name="in_lawsuit")
    city_locations = models.ManyToManyField("rh.Localidade", related_name="+")
    last_part_lawsuit = models.ForeignKey(
        "PartLawsuit", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    acting_zone = models.ForeignKey(
        "ActingZone",
        related_name="lawsuit_acting_zone",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    remaining_days = models.SmallIntegerField(null=True, blank=True)
    statistic_markers = models.ManyToManyField(
        "StatisticMarker", related_name="lawsuits"
    )
    external_code = models.CharField(max_length=100, null=True)

    class Meta:
        permissions = (
            ("outcourtlawsuitadmin", "Pode administrar os OutCourtLawsuit"),
            (
                "can_view_outcourtlawsuit_secretary",
                "Pode visualizar os procedimentos da Secretaria",
            ),
        )
        ordering = ("remaining_days", "cache_number")

    @property
    def cache_dir(self):
        return os.path.join(
            settings.CACHE_BASE,
            settings.JUDICIAL_DESTINATION_CACHE,
            "%d" % self.year,
            "%d" % (self.number_lawsuit / 256),
            self.cache_number,
        )

    @property
    def abs_file_cache(self):
        return os.path.join(self.cache_dir, "full")

    @property
    def url_cache(self):
        return "%s%s/%d/" % (
            settings.ATHENAS,
            settings.JUDICIAL_URL_PDF_LAWSUIT,
            self.pk,
        )

    @property
    def abs_url_cache(self):
        return "/%s%s/%d/" % (
            settings.CONTEXT,
            settings.JUDICIAL_URL_PDF_LAWSUIT,
            self.pk,
        )

    @property
    def exists_cache(self):
        destination = os.path.join(self.lawsuit.cache_dir, "%d" % (self.pk))
        return os.path.exists(destination)

    @property
    def cache_filestream(self):
        if self.exists_cache:
            pdf_file = self.abs_file_cache
        else:
            pdf_file = settings.JUDICIAL_PDF_ERROR

        etag = self.get_etag_cache(pdf_file)

        class __LawsuitCacheFileStream:
            def __init__(self):
                self.stream = open(pdf_file, "rb")
                self.etag = etag

            def __enter__(self):
                return self

            def __exit__(self, *args, **kwargs):
                self.stream.close()

        return __LawsuitCacheFileStream

    @property
    def in_secretary(self):
        return self.tags.filter(slug="caixa-da-secretaria").exists()

    @property
    def in_give_back_box(self):
        return self.tags.filter(slug="proc-devolvidos").exists()

    def get_etag_cache(self, file):
        file_stats = os.stat(file)
        return hashlib.md5(str(file_stats.st_mtime).encode()).hexdigest()

    def _create_lockfile(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        with open(os.path.join(self.cache_dir, "full.lock"), "w+"):
            pass

    @classmethod
    def calculate_deadline_date(klass, lawsuit, by=None):
        deadline = klass.remainig_days_type_lawsuit(lawsuit)

        return (date.today() if not by else by) + relativedelta(days=deadline)

    @classmethod
    def remainig_days_type_lawsuit(klass, lawsuit):
        cfg = Configuration.get_or_create("ejud")
        triage_workplace = json.loads(cfg.get("triageCenter", "[]"))
        main_triage_center = int(cfg.get("mainTriageCenter", 0)) or None

        if not main_triage_center:
            raise Exception(
                "Não foi definido um centro de triagem principal. Favor ajustar definições no configurador do eJud."
            )

        triage_workplace.append(main_triage_center)
        deadline = 0

        type_lawsuit_map = {
            1: "deadlineFactNews",
            2: "deadlineCivilInvestigation",
            3: "deadlinePreparatoryProcedure",
            4: "deadlinePreparatoryCivilInvestigation",
            6: "deadlineAssessmentNoticeOffice",
            7: "deadlineAdministrativeProcedure",
            8: "deadlineRogatoryLetter",
            9: "deadlinePreparatoryProcedureElectoral",
            10: "deadlineAdministrativeManagement",
        }

        if lawsuit.type_lawsuit == 1 and lawsuit.location.pk in triage_workplace:
            deadline = int(cfg.get("deadlineTriage", 0) or 0)
        else:
            label = type_lawsuit_map.get(int(lawsuit.type_lawsuit), "undefined")
            deadline = int(cfg.get(label) or 0)

        return deadline

    @property
    def is_acting_as_owner(self):
        employee = employee_from_user(get_current_user())

        if employee:
            return employee.work_locations.filter(pk=self.location.pk).exists()

        return False

    @property
    def is_acting_as_collaborator(self):
        employee = employee_from_user(get_current_user())

        if employee:
            return (
                self.requestcollaboration.filter(canceled_by=None)
                .filter(
                    Q(requestcollaborationperson__person=employee.pessoa_fisica)
                    | Q(
                        requestcollaborationgeneralorgan__general_organ__in=employee.work_locations
                    )
                )
                .exists()
            )

        return False

    @property
    def is_acting_as_secretary(self):
        employee = employee_from_user(get_current_user())

        if employee:
            employee_locations = employee.work_assignment_effective_exercise.values(
                "lotacao"
            )
            secretaries = Secretary.objects.filter(location__in=employee_locations)
            secretary = None
            if secretaries.exists():
                secretary = secretaries.first()
                return secretary.execution_organs.filter(pk=self.location).exists()

        return False

    @property
    def is_acting_as_secretary(self):
        employee = employee_from_user(get_current_user())

        if employee:
            employee_locations = employee.work_assignment_effective_exercise.values(
                "lotacao"
            )
            secretaries = Secretary.objects.filter(location__in=employee_locations)
            secretary = None
            if secretaries.exists():
                secretary = secretaries.first()
                return secretary.execution_organs.filter(pk=self.location).exists()

        return False

    @property
    def is_acting(self):
        return (
            self.is_acting_as_owner
            or self.is_acting_as_collaborator
            or self.is_acting_as_secretary
        )

    @property
    def active_access_controls(self):
        return self.access_controls.exclude(signed_by=None).filter(suspended_by=None)

    @property
    def can_read(self):
        if self.active_access_controls.exists():
            query = self.active_access_controls.filter(
                Q(authorization__person=person_from_user(get_current_user()))
                & Q(authorization__state__in=(1, 2))
            )

            if query.exists():
                log.info("Numero de autorizações: %d", query.count())
                log.info("Extrato:")
                for control in query:
                    authorization = control.authorization.filter(
                        person=person_from_user(get_current_user()), state__in=(1, 2)
                    )[0]

                    log.info("Para: %s", authorization.person)
                    log.info("Estado: %s", authorization.get_state_display())

            return query.exists()
        else:
            return True

    @property
    def icon_access_control(self):
        if self.active_access_controls.exists():
            return {
                "iconCls": "icon-judicial icon-ejud-part-access",
                "title": "Com controle de acesso",
            }
        elif self.access_controls.filter(suspended_by=None).exists():
            return {
                "iconCls": "icon-judicial icon-ejud-part-access-edit",
                "title": "Com controle de acesso em construção",
            }

    def next_number_control(self):
        if EventControl.objects.filter(lawsuit=self).exists():
            query = EventControl.objects.filter(lawsuit=self).aggregate(
                max_number=models.Max("number_control")
            )
            return int(query.get("max_number") or 0) + 1
        else:
            return 1

    def __str__(self):
        if self.origin:
            return " - ".join([self.cache_number, self.origin.assunto])
        else:
            return self.cache_number

    def conflict_page_number(self, document):
        return (
            self.all_signed_documents.exclude(pk=document.pk)
            .filter(page_number=document.page_number)
            .exists()
        )

    def reordenate_documents_by(self, by_document):
        log.info("Reornenado documentos a partir de %s", by_document)
        query = (
            self._all_signed_documents(False)
            .exclude(pk=by_document.pk)
            .filter(page_number__gte=by_document.page_number)
        )

        if query.exclude(lawsuit=self.pk).exists():
            log.debug(by_document.page_number)

            while query.filter(page_number=by_document.page_number).exists():
                by_document.page_number -= 1
                query = self.all_signed_documents.exclude(pk=by_document.pk).filter(
                    page_number__gte=by_document.page_number
                )

            log.debug(
                "pk: %d - page: %d - %s"
                % (by_document.pk, by_document.page_number, by_document)
            )
            PartLawsuit.objects.filter(pk=by_document.pk).update(
                page_number=by_document.page_number
            )
        else:
            for document in query.order_by("-page_number"):
                log.info(
                    "Reordenando o documento %s da página %d para %d",
                    (
                        document.my_origin,
                        document.page_number,
                        document.page_number + 1,
                    ),
                )
                PartLawsuit.objects.filter(pk=document.pk).update(
                    page_number=(document.page_number + 1)
                )

    def next_page(self):
        query = self.all_documents.aggregate(max_page_number=models.Max("page_number"))
        return int(query.get("max_page_number") or 0) + 1

    @property
    def current_location(self):
        return (
            self.location
            if not self.external_locations.filter().exists()
            else self.external_locations.filter()
        )

    @classmethod
    def import_from_protocol(klass, protocol, location=None, type_lawsuit=1):
        with transaction.atomic():
            query = Movimentacao.inbox_queryset().filter(protocolo=protocol)
            cfg = Configuration.get_or_create("ejud")

            inst = None

            if query.exists():
                movement = query.first()

                loc = None

                if movement.lotacao_destino and movement.lotacao_destino.pk == int(
                    location
                ):
                    loc = movement.lotacao_destino.lotacao
                elif not movement.lotacao_destino:
                    employee = employee_from_user(get_current_user())
                    loc = employee.work_locations.get(pk=location)
                else:
                    raise Exception(
                        "Inconsistencia na importação, importação interrompida."
                    )

                inst = OutCourtLawsuit(origin=movement.protocolo)
                inst.title = movement.protocolo.assunto
                inst.location = loc
                inst.remaining_days = int(cfg.get("deadlineTriage") or 0)

                inst.save()

                denunciation = Denunciation(
                    protocol=movement.protocolo,
                    create_location=inst.location,
                    lawsuit=inst,
                )
                denunciation.force_type_lawsuit = type_lawsuit
                denunciation.save()
                PartLegalSign.sign(denunciation)

                inst.parts.add(Triage(create_location=inst.location), bulk=False)

                inst.send_to(
                    to=inst.location,
                    parecer_template="<p>Para este protocolo foi gerado o procedimento %s.</p>"
                    % inst.cache_number,
                )

            else:
                raise Exception(
                    "Este documento não esta mais na sua caixa de entrada no protocolo."
                )

            return inst

    @property
    def interested(self):
        return Pessoa.objects.filter(
            pk__in=Interested.objects.filter(lawsuit=self).values("person")
        )

    @property
    def all_documents(self):
        my = PartLawsuit.objects.filter(lawsuit=self)
        shared = PartLawsuit.objects.filter(shared_with_lawsuit=self)
        return PartLawsuit.objects.filter(
            Q(pk__in=my.values("pk")) | Q(pk__in=shared.values("pk"))
        )

    def _all_signed_documents(self, exclude_unfolded=True):
        query = self.all_documents.exclude(signed_by=None)
        return query if not exclude_unfolded else query.filter(unfolded_by=None)

    @property
    def all_own_signed_documents(self):
        return PartLawsuit.objects.filter(lawsuit=self).exclude(signed_by=None)

    @property
    def all_signed_documents(self):
        return self._all_signed_documents()

    def _documents(self, pklist=None):
        if pklist:
            query = (
                PartLawsuit.objects.filter(
                    Q(lawsuit=self) | Q(shared_with_lawsuit=self)
                )
                .filter(pk__in=pklist)
                .exclude(signed_by=None)
            )

            return self.prepare_pages(query)

        return self.documents

    def prepare_pages(self, query=None):
        pages = []
        for document in query:
            pages.append(document.rendered)
            pages += document.extra_pages

        return pages

    @property
    def documents(self):
        query = PartLawsuit.objects.filter(
            Q(lawsuit=self) | Q(shared_with_lawsuit=self)
        ).exclude(signed_by=None)
        return self.prepare_pages(query)

    @property
    def access_controls(self):
        return PartLawsuitAccess.objects.filter(
            Q(Q(part__lawsuit=self) | Q(part__shared_with_lawsuit=self))
            & ~Q(signed_by=None)
            & Q(suspended_by=None)
        )

    @property
    def my_tracks_executionorgan(self):
        return ExecutionOrgan.objects.filter(
            pk__in=self.origin.movimentacoes.values("lotacao_origem")
        )

    @property
    def icon_have_time(self):
        if self.deadline and self.deadline >= 5:
            return {
                "iconCls": "icon-judicial icon-ejud-outlawcortsuit-have-time",
                "title": "Há tempo para atuação.",
            }
        elif self.deadline and self.deadline >= 0:
            return {
                "iconCls": "icon-judicial icon-ejud-outlawcortsuit-have-short-time",
                "title": "Há pouco tempo para atuação.",
            }
        elif self.deadline is None:
            return {}
        else:
            return {
                "iconCls": "icon-judicial icon-ejud-outlawcortsuit-not-have-time",
                "title": "Não há mais tempo para atuação.",
            }

    @classmethod
    def next_number(klass, year):
        rst = klass.objects.filter(year=year).aggregate(
            max_year=models.Max("number_lawsuit")
        )
        return int(rst.get("max_year", 0) or 0) + 1

    @classmethod
    def format_cache_number(klass, number, year):
        if not number or not year:
            return "--"
        else:
            return "%(year)d.%(number)07d" % {"number": number, "year": year}

    @property
    def connecteds(self):
        return self.__class__.objects.filter(
            pk__in=self.connections.exclude(signed_by=None).values("lawsuit")
        )

    @property
    def deadline_date(self):
        return (
            date.today() + timedelta(days=self.remaining_days)
            if self.remaining_days is not None
            else None
        )

    @property
    def deadline(self):
        return self.remaining_days

    @property
    def icon_type_lawsuit(self):
        return {
            "iconCls": "icon-judicial icon-ejud-%s-in-grid"
            % slugify(self.get_type_lawsuit_display()),
            "title": self.get_type_lawsuit_display(),
        }

    @property
    def icon_state(self):
        return {
            "iconCls": "icon-judicial icon-ejud-lawsuit-%s"
            % ("locked" if self.closed_at else "open"),
            "title": (
                "Procedimento finalizando extrajudicialmente"
                if self.closed_by
                else "Em andamento"
            ),
        }

    @property
    def icons(self):
        return [
            self.icon_state,
            self.icon_type_lawsuit,
            self.icon_have_time,
            self.icon_access_control,
        ]

    def current_moviment(self, data_finalizado=None):
        if getattr(self, "_current_moviment", None) is None:

            """
            Trecho modificado para obter a movimentação atual da caixa de entrada
            do responsável pela central de triagem caso a criação da notícia de fato tenha origem na web.
            """
            employee = None
            if getattr(self.origin, "_signed_by_web", False):
                cfg = Configuration.get_or_create("ejud")

                pk = cfg.get("mainTriageCenter")
                if not pk:
                    raise Exception(
                        "Sem central de triagem definida. Favor ajustar definições no configurador do eJud."
                    )

                triageCenter = Lotacao.objects.get(pk=pk)
                employee = triageCenter.responsavel
            else:
                employee = employee_from_user(get_current_user())

            collab_location_ids = (
                RequestCollaboration.objects.filter(canceled_by=None)
                .filter(
                    Q(requestcollaborationperson__person=employee.pessoa_fisica)
                    | Q(
                        requestcollaborationgeneralorgan__general_organ__in=employee.work_locations
                    )
                )
                .values("lawsuit__location_id")
            )

            employee_locations = employee.work_assignment_effective_exercise.values(
                "lotacao"
            )
            secretaries = Secretary.objects.filter(location__in=employee_locations)
            execution_organs = secretaries.values("execution_organs")

            acting_locations = Lotacao.objects.filter(
                Q(pk__in=employee.work_locations)
                | Q(pk__in=collab_location_ids)
                | Q(pk__in=execution_organs)
            )

            lotacoes = [wl for wl in acting_locations if wl.pk == self.location.pk]
            qset = EDOCBoxQuery(servidor=employee, lotacoes=lotacoes)

            self._current_moviment = (
                qset.get_caixa_entrada()
                .filter(protocolo=self.origin, data_finalizado=data_finalizado)
                .order_by("id")
                .last()
            )

        return self._current_moviment

    def _get_matters_formated(self):
        matters = []
        for item in self.matters.all():
            matters.append(">".join(item.path_cache.split(">")[1:]))

        return matters

    @property
    def _get_qrcode(self):
        pass
        # code = pyqrcode.create(self.cache_number)
        # return code.png_as_base64_str(scale=4)

    @property
    def cover(self):
        if self.can_read:
            tpl = loader.get_template("judicial/lawsuit/cover.html")

            return tpl.render(
                {
                    "doc": self,
                    "qrcode": self._get_qrcode,
                    "location": self.location,
                    "number": self.cache_number,
                    "type_self": self.get_type_lawsuit_display(),
                    "created_at": DateUtils.datetime_to_str(
                        self.origin.data_criacao if self.origin else datetime.now()
                    ),
                    "matters": self._get_matters_formated(),
                    "is_confidential": self.active_access_controls.exists(),
                }
            )
        else:
            return """<h2>Procedimento com Controle de Acesso</h2>"""

    @property
    def last_part_lawsuit_signed(self):
        return self.last_part_lawsuit

    @property
    def is_received(self):
        employee = employee_from_user(get_current_user())

        if employee:
            return not self.movements.filter(
                to_location__in=employee.work_locations,
                received_by=None,
                received_at=None,
            ).exists()
        else:
            return False

    def add_authorization_confidential_lawsuit(self, peoples=[], departaments=[]):

        query = PartLawsuitAccess.objects.filter(
            Q(Q(lawsuit=self) | Q(part__in=self.parts.filter()))
        ).distinct()

        for acl in query:
            acl.authorization.filter(state__in=[1, 2]).update(
                state=3, finished_by=get_current_user(), finished_at=datetime.now()
            )
            for person in peoples:
                if not acl.authorization.filter(
                    person=person, state__in=[1, 2]
                ).exists():
                    acl.add_person_access(person=person, controlled=False)
                else:
                    log.info(
                        "%s já possui autorização para o documento %s", person, acl.part
                    )

            # adiciona os responsaveis pelo departamento, apenas o sistema poderá remover ou editar posteriormente.
            # mas o usuário poderá revogar a permissão.
            for dep in Lotacao.objects.filter(pk__in=departaments):
                resp = dep.responsavel.pessoa_fisica if dep.responsavel else None
                if (
                    resp
                    and not acl.authorization.filter(
                        person=resp, controlled=True, state__in=[1, 2]
                    ).exists()
                ):
                    acl.add_person_access(person=resp, controlled=True)

    def send_to(
        self,
        to,
        parecer_template="",
        finalizado=False,
        force_current=None,
        force_location=None,
    ):
        to = to if isinstance(to, (tuple, list, set)) is True else [to]
        peoples = [dst.pk for dst in to if isinstance(dst, Pessoa) is True]
        departaments = [dst.pk for dst in to if isinstance(dst, OrgaoGeral) is True]

        log.info("Destinatarios")
        log.info("> Pessoas: %d", len(peoples))
        log.info("> Locais: %d", len(departaments))
        log.info("> Closed: %s", ("Sim" if finalizado else "Não"))

        if len(peoples) == 0 and len(departaments) == 0:
            raise Exception("Nenhuma destinação para o protocolo.")

        # metodo para realizar mudanca das permissoes de visualizacao de procedimentos com sigilo
        self.add_authorization_confidential_lawsuit(
            peoples=peoples, departaments=departaments
        )

        log.info("force current? %s", "yes" if force_current else "no")
        current_movement = force_current if force_current else self.current_moviment()

        if self.origin.data_finalizado:
            Protocol.objects.filter(pk=self.origin.pk).update(data_finalizado=None)

        if current_movement.data_finalizado:
            log.info(
                "Detectado movimento finalizado, realizando o desfinalizamento do mesmo."
            )
            self.origin.movimentacoes.filter(
                pk__in=(current_movement.pk, current_movement.child_of.pk)
            ).update(data_finalizado=None, encaminhado=False)

            undo_movement = self.origin.movimentacoes.get(pk=current_movement.pk)
            father_movement = self.origin.movimentacoes.get(
                pk=undo_movement.child_of.pk
            )

            current_movement = self.origin.movimentacoes.get(pk=father_movement.pk)

            log.info("curernt movement")
            log.info("pk: %d", current_movement.pk)
            log.info("step: %d", current_movement.passo)
            log.info("closed date: %s", current_movement.data_finalizado)

            log.info("undo movement")
            log.info("pk: %d", undo_movement.pk)
            log.info("step: %d", undo_movement.passo)
            log.info("closed date: %s", undo_movement.data_finalizado)

            undo_movement.undo()

        current_movement.do_send(
            person_destination=peoples,
            location_destination=departaments,
            close=finalizado,
            advice=parecer_template,
            with_workflow=True,
        )

        for connected in self.has_connected.filter(closed_at=None):
            log.info(" \033[1m*\033[0m lawsuit connected %s", connected)
            if not connected.origin.pk == self.origin.pk:
                connected.send_to(
                    to=to,
                    parecer_template=parecer_template,
                    finalizado=finalizado,
                    force_location=force_location,
                )
            else:
                connected.finalize()

            connected.location = to[0] if not force_location else force_location
            connected.save()

        if finalizado:
            self.finalize()

    def finalize(self):
        # self.deadline_cache = None
        self.remaining_days = None
        self.closed_by = get_current_user()
        self.closed_at = datetime.now()
        self.save()

    @classmethod
    def update_last_part_lawsuit(cls, out_court_lawsuit):
        lawsuit = cls.objects.get(pk=out_court_lawsuit.pk)

        if not lawsuit.all_signed_documents.exists():
            return None
        else:
            current = lawsuit.all_signed_documents.order_by("signed_at").last()
            if current.pk != (
                lawsuit.last_part_lawsuit.pk if lawsuit.last_part_lawsuit else None
            ):
                cls.objects.filter(pk=lawsuit.pk).update(last_part_lawsuit=current)
                return current
            else:
                return lawsuit.last_part_lawsuit

    @classmethod
    def decrement_remaining_days(cls, query_set=[], dry_run=True):
        for lawsuit in query_set:
            if not dry_run and lawsuit.remaining_days is not None:

                DeadlineLog.register(
                    lawsuit=lawsuit,
                    days=lawsuit.remaining_days,
                    observation="Inserido pelo sistema",
                )

                days = lawsuit.remaining_days - 1
                cls.objects.filter(pk=lawsuit.pk).update(remaining_days=days)

    @classmethod
    def queryset_lawsuit_to_decrement_day(cls, location=None, to_date=None):
        executed_today = DeadlineLog.queryset_lawsuit_executed_to_date(to_date=to_date)
        return (
            cls.objects.filter(
                Q(
                    Q(remaining_days__isnull=False)
                    & Q(closed_at__isnull=True)
                    & Q(removed_at__isnull=True)
                    & Q(location__localidade=location)
                )
            )
            .exclude(pk__in=executed_today)
            .exclude(attached_lawsuit__isnull=False)
        )

    @classmethod
    def queryset_lawsuit_to_weekend_decrement_day(cls, location=None, to_date=None):
        return (
            cls.queryset_lawsuit_to_decrement_day(location=location, to_date=to_date)
            .exclude(remaining_days=1)
            .exclude(attached_lawsuit__isnull=False)
        )

    def fill_main_tag(self, prevent_save=False):
        choice = JudicialChoice.objects.get(
            app_label="judicial", name="TYPE_LAWSUIT", value=self.type_lawsuit
        )
        if choice.classification:
            self.main_tag = Tag.objects.filter(tag_type=1).get(
                classification=choice.classification
            )

    def __contains_bloke__(self, who_pk):
        for bloke in self.blokes.filter():
            if bloke.my_bloke.pk == who_pk:
                return True
        return False

    def receive_collaboration(self):
        employer = employee_from_user(get_current_user())

        collaborations = self.requestcollaboration.filter(
            Q(
                Q(requestcollaborationperson__person=employer.pessoa_fisica)
                | Q(
                    requestcollaborationgeneralorgan__general_organ__in=employer.work_locations
                )
            )
        ).filter(received_by__isnull=True)

        if collaborations.exists():
            collaborations.update(
                received_by=get_current_user(), received_at=datetime.now()
            )

    def receive_movement(self):
        self.receive_collaboration()

        movements = MovementLog.objects.filter(
            out_court_lawsuit=self,
            to_location=self.location,
            received_by=None,
            received_at=None,
        )

        employee = employee_from_user(get_current_user())
        if self.is_acting_as_owner and movements.exists():
            if movements.count() > 1:
                log.warn(
                    ">>>Não é possível definir qual Log de Movimento será atualizado<<<"
                )
                log.warn("Procedimento: %s " % self)
                log.warn("Localidade: %s " % self.location)

            movements.update(received_by=get_current_user(), received_at=datetime.now())
            self.tags.remove(Tag.objects.get(tag_type=1, slug="nao-recebido"))

    def receive_movement_lot(self, from_location):
        movements = MovementLog.objects.filter(
            out_court_lawsuit=self,
            to_location=from_location,
            received_by=None,
            received_at=None,
        )

        if movements.exists():
            movements.update(received_by=get_current_user(), received_at=datetime.now())
            self.tags.remove(Tag.objects.get(tag_type=1, slug="nao-recebido"))

    def validate_ownership(self):
        if not self.current_moviment():
            raise Exception(
                "Você não pode modificar um procedimento que não em sua posse."
            )

    def finish_requestcollaborations(self):
        self.requestcollaboration.all().update(
            canceled_by=get_current_user(), canceled_at=datetime.now()
        )

    @classmethod
    def on(klass, event_name, callback):
        db = getattr(klass, "_events", {})
        events = db.get(event_name, [])
        events.append(callback)
        db.update({event_name: events})
        klass._events = db

    @classmethod
    def emmit(klass, event_name, *args, **kwrgs):
        db = getattr(klass, "_events", {})
        events = db.get(event_name, [])

        for callback in events:
            callback(*args, **kwrgs)

    def save(self, *args, **kwargs):
        if not self.cache_number or self.cache_number == "--":
            self.cache_number = self.format_cache_number(self.number_lawsuit, self.year)

        # need_change_location = False
        # older_location = None

        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)
            if older.location != self.location:
                # need_change_location = True
                # older_location = older.location
                self.emmit(
                    "changed_location",
                    lawsuit=self,
                    of=older.location,
                    to=self.location,
                )
        # else:
        #    need_change_location = True

        # self.emmit('changed_location', lawsuit=self, of=older.location, to=self.location)

        self.fill_main_tag(prevent_save=True)
        super(OutCourtLawsuit, self).save(*args, **kwargs)

        # self.emmit('changed_location', lawsuit=self, of=older.location, to=self.location)

        OutCourtLawsuit.update_last_part_lawsuit(self)

        for connected in self.has_connected.filter():
            connected.remaining_days = self.remaining_days
            connected.save()

        try:
            current_moviment = self.current_moviment()

            if not self.removed_by and not current_moviment.with_workflow:
                log.info("marcado protocolo %s com workflow", self.origin.codigo)
                self.origin.movimentacoes.filter(pk=current_moviment.pk).update(
                    with_workflow=True
                )
            elif self.removed_by and current_moviment.with_workflow:
                if (
                    not self.origin.out_court_lawsuits.exclude(pk=self.pk)
                    .filter(removed_by=None)
                    .exists()
                ):
                    self.origin.movimentacoes.filter(pk=current_moviment.pk).update(
                        with_workflow=False
                    )
            else:
                log.info(
                    "o protocolo %s não precisa ser marcado com workflow",
                    self.origin.codigo,
                )
        except Exception:
            log.info(
                "O procedimento %s com protocolo %s não esta marcado como com workflow e não pode ser mudado",
                (
                    self.cache_number,
                    self.origin.codigo if self.origin else "indefinido",
                ),
            )

    @property
    def exists_cache(self):
        destination = os.path.join(self.cache_dir, "full")
        return os.path.exists(destination)

    def create_cache_lawsuit(self):
        from judicial.tasks.realtime import create_cache_lawsuit

        user = get_current_user()
        voucher = DisposableVoucher.objects.create(user=get_current_user())

        self._create_lockfile()
        create_cache_lawsuit.delay(voucher.jwt, self.pk, user.pk)

    @property
    def my_reminders(self):
        user = get_current_user()
        employee = employee_from_user(user)
        workplaces = [sl.lotacao for sl in employee.work_assignment_effective_exercise]

        collaborations = self.requestcollaboration.filter(canceled_by__isnull=True)
        for collab in collaborations:
            if collab.my_origin.is_to_user(user):
                workplaces.append(collab.origin_location.lotacao)

        return self.reminders.filter(
            Q(created_by=user)
            | Q(access_level=Reminder.PUBLIC)
            | Q(workplace__in=workplaces)
        ).exclude(deactivated_by__isnull=False)


OutCourtLawsuit.on(
    "changed_location", lambda lawsuit, of, to: lawsuit.finish_requestcollaborations()
)

OutCourtLawsuit.on(
    "changed_location", lambda lawsuit, of, to: MovementLog.register(lawsuit, of, to)
)


class Interested(AuditTimestampModel):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="has_interested", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    person = models.ForeignKey(
        "rh.Pessoa", related_name="has_interested_of_lawsuits", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    direct = models.BooleanField(default=False)

    class Meta:
        ordering = ("-direct", "person")

    @property
    def icons(self):
        return [
            {
                "iconCls": "icon-judicial icon-ejud-confirm-diligence",
                "title": "Interessado",
            }
        ]

    def save(self, *args, **kwags):
        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)
            if older.person != self.person and older.direct:
                raise Exception(
                    "Não posso modificar um interessado que foi indicado pelo sistema."
                )

        super(Interested, self).save(*args, **kwags)


class NotifyStack(models.Model):
    employee = models.ForeignKey(
        "rh.Servidor", related_name="+", on_delete=models.PROTECT
    )
    out_court_lawsuits = models.ForeignKey(
        OutCourtLawsuit, related_name="+", on_delete=models.PROTECT
    )
    notfied = models.BooleanField(default=False)

    def notify(self, mid="EJUD_CREATION"):
        message = Message.objects.filter(mid=mid)
        if message.exists():
            params = {
                "cache_number": self.out_court_lawsuits.cache_number,
                "assunto": self.out_court_lawsuits.origin.assunto,
                "type_lawsuit": self.out_court_lawsuits.get_type_lawsuit_display(),
                "location": self.out_court_lawsuits.location.nome,
            }
            target = self.employee
            Notification.notify(message.get(), target, sender=None, **params)
            self.notfied = True
            self.save()

    @classmethod
    def create_for_location(klass, out_court_lawsuits, location):
        # if hasattr(location, 'lotacao'):
        for employee in location.lotacao.employees:
            query = klass.objects.filter(
                employee=employee, out_court_lawsuits=out_court_lawsuits
            )

            if not query.exists():
                NotifyStack(
                    employee=employee, out_court_lawsuits=out_court_lawsuits
                ).save()

    @classmethod
    def create_for(klass, out_court_lawsuits):
        if out_court_lawsuits.number_lawsuit and out_court_lawsuits.year:
            klass.create_for_location(out_court_lawsuits, out_court_lawsuits.location)


class Taxonomy(models.Model):
    version = models.CharField(max_length=20, db_index=True)
    efective_date = models.DateField()

    def __str__(self):
        return "%s - %s" % (self.version, self.efective_date)


class LegalClassification(models.Model):
    version = models.ForeignKey(
        Taxonomy, related_name="classifications", on_delete=models.PROTECT
    )
    cnmp_code = models.IntegerField(null=True, db_index=True)
    father = models.ForeignKey(
        "self", related_name="children", null=True, on_delete=models.PROTECT
    )
    title = models.CharField(max_length=200, db_index=True)
    path_cache = models.CharField(max_length=400, db_index=True, blank=True)
    taxonomy_type = models.CharField(max_length=30, default="", null=True, blank=True)
    glossary = models.TextField(blank=True, null=True)
    disabled = models.BooleanField(default=False)
    administrative_classification = models.BooleanField(default=False)
    selectable = models.BooleanField(default=False)
    judicial_classification = models.BooleanField(default=False)
    suspend_deadline = models.BooleanField(default=False)
    helper_can_sign = models.BooleanField(default=False)
    collaborator_can_sign = models.BooleanField(default=False)
    extend_deadline = models.BooleanField(default=False)

    sep = " > "

    class Meta:
        ordering = (
            "path_cache",
            "title",
        )

    @property
    def cnmp_unicode(self):
        return "%06d - %s" % (self.cnmp_code, self.title)

    @classmethod
    def export_as_html(klass):

        root = klass.objects.filter(father=None)

        return loader.get_template(
            "judicial/legalclassification_tree_view.html"
        ).render({"root": root})

    def __str__(self):
        return self.path

    @property
    def path(self):
        if not self.path_cache or self.path_cache in ("", " "):
            self.path_cache = (
                self.title
                if not self.father
                else self.sep.join([self.father.path, self.title])
            )
            self.save()

        return self.path_cache

    def save(self, *args, **kwargs):
        if not self.taxonomy_type:
            self.taxonomy_type = self._meta.model_name

        super(LegalClassification, self).save(*args, **kwargs)


class LegalMatter(LegalClassification):
    pass


class LegalMoviment(LegalClassification):
    pass


class LegalProcedure(LegalClassification):
    pass


class LegalClass(LegalClassification):
    instauration = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "CLASS_INSTAURATION"),
        blank=True,
        null=True,
    )

    def _sync_type_lawsuit_choices(self, value_number):
        log.info("Check in judicial.TYPELAWSUIT")
        query = self.has_judicial_choices.filter(
            app_label="judicial", name="TYPE_LAWSUIT"
        )

        if not query.exists():
            obj = JudicialChoice.objects.create(
                app_label="judicial",
                name="TYPE_LAWSUIT",
                label=self.title,
                classification=self,
                value=value_number,
            )
            log.info("judicial.TYPELAWSUIT created")
        elif query.filter(active=False).exists():
            query.update(label=self.title, active=True)
            value_number = query.get().value
            log.info("judicial.TYPELAWSUIT actived")
        else:
            value_number = query.get().value

        return value_number

    def _sync_notice_office_type_choices(self, value_number):
        log.info("Check in judicial.NOTICE_OFFICE_TYPE")
        query = self.has_judicial_choices.filter(
            app_label="judicial", name="NOTICE_OFFICE_TYPE"
        )
        if not query.exists():
            JudicialChoice.objects.create(
                app_label="judicial",
                name="NOTICE_OFFICE_TYPE",
                label=self.title,
                classification=self,
                value=value_number,
            )
            log.info("judicial.NOTICE_OFFICE_TYPE created")
        elif query.filter(active=False).exists():
            query.update(label=self.title, active=True)
            log.info("judicial.NOTICE_OFFICE_TYPE actived")

    def _sync_type_ordinace_choices(self, value_number):
        log.info("Check in judicial.TYPE_ORDINACE")
        query = self.has_judicial_choices.filter(
            app_label="judicial", name="TYPE_ORDINACE"
        )
        if not query.exists():
            JudicialChoice.objects.create(
                app_label="judicial",
                name="TYPE_ORDINACE",
                label=self.title,
                classification=self,
                value=value_number,
            )
            log.info("judicial.TYPE_ORDINACE created")
        elif query.filter(active=False).exists():
            query.update(label=self.title, active=True)
            log.info("judicial.TYPE_ORDINACE actived")

    def _sync_tag(self):
        log.info("Check in Tag exists")
        value = None

        if self.instauration:
            if not hasattr(self, "has_tag"):
                tag = Tag.objects.create(
                    title=self.title, tag_type=1, classification=self, active=True
                )
                log.info("Tag is created")
                value = tag.pk
            else:
                self.has_tag.title = self.title
                self.has_tag.active = True
                self.has_tag.save()
                log.info("Tag is activated")
                value = self.has_tag.pk
        else:
            if hasattr(self, "has_tag") and self.has_tag.active:
                self.has_tag.title = self.title
                self.has_tag.active = False
                self.has_tag.save()
                log.info("Tag is inactivated")

        return value

    def sync_choices(self):
        self.has_judicial_choices.filter().update(active=False)

        if self.instauration:
            value_number = self._sync_tag()
            self.instauration = int(self.instauration) if self.instauration else None
            self._sync_type_lawsuit_choices(value_number)
            if self.instauration == 1:
                self._sync_notice_office_type_choices(value_number)
            elif self.instauration == 2:
                self._sync_type_ordinace_choices(value_number)

        self._sync_tag()

    def save(self, *args, **kwags):
        self.sync_choices()
        super(LegalClass, self).save(*args, **kwags)


class JudicialChoice(Choice):
    classification = models.ForeignKey(
        LegalClassification,
        related_name="has_judicial_choices",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)


class Character(models.Model):
    title = models.CharField(max_length=60, unique=True, verbose_name="Título")
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    users = models.ManyToManyField("auth.User", related_name="has_character")

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Character, self).save(*args, **kwargs)


class GlosaryManager(models.Manager):

    def get_by_natural_key(self, app_label, model_name):
        return self.get(app_label=app_label, model_name=model_name)


class Glosary(models.Model):
    objects = GlosaryManager()

    title = models.CharField(max_length=120, null=True)
    app_label = models.CharField(max_length=200, db_index=True)
    model_name = models.CharField(max_length=200, db_index=True)
    icon_class = models.CharField(max_length=200)
    meaning_type = models.SmallIntegerField(
        choices=(
            (MEANING_TYPE_DOCUMENT, "Documento"),
            (MEANING_TYPE_ACTION, "Ação"),
            (MEANING_TYPE_UNDEFINED, "Não classificado"),
        ),
        default=MEANING_TYPE_UNDEFINED,
    )
    classification_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "GLOSARY_CLASSIFICATION_TYPE"),
        null=True,
        blank=True,
    )
    legal_classification = models.ForeignKey(
        LegalClassification,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    allowed_for = models.ManyToManyField(Character, related_name="permissions")
    active = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("can_admin_glosary", "Pode administrar os tipos de documentos"),
        )
        ordering = ("title", "app_label", "model_name")
        unique_together = (("app_label", "model_name"),)

    def natural_key(self):
        return (self.app_label, self.model_name)

    @classmethod
    def do_register(klass):
        for dest in getattr(klass, "_todo_register", []):
            log.info("Register %s ...", dest)
            try:
                gpl, created = klass.objects.get_or_create(
                    app_label=dest._meta.app_label, model_name=dest._meta.model_name
                )

                obj = dest()
                gpl.icon_class = getattr(dest, "default_icon", lambda: "")()
                gpl.title = obj.my_origin.codename
                gpl.meaning_type = getattr(obj, "meaning_type", MEANING_TYPE_UNDEFINED)
            except Exception as e:
                log.exception(e)
            else:
                gpl.save()
        klass._todo_register = []

    @classmethod
    def register(klass):
        def _decorator(dest):
            klass._todo_register = getattr(klass, "_todo_register", [])
            klass._todo_register.append(dest)

            if (
                django.VERSION[0] < 1
                or django.VERSION[0] == 1
                and django.VERSION[1] < 7
            ):
                klass.do_register()

            return dest

        return _decorator


type_part_lawsuit = Glosary.register


class GlosaryTemplate(AuditTimestampModel):
    title = models.CharField(max_length=60)
    glosary = models.ForeignKey(
        Glosary, related_name="templates", on_delete=models.PROTECT
    )
    template = models.TextField(blank=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = (
            "-active",
            "-pk",
        )

    @property
    def icons(self):
        if self.active:
            return [{"iconCls": "icon-judicial icon-ejud-active", "title": "Ativo"}]
        else:
            return []

    def save(self, *args, **kwargs):
        if self.active:
            self.glosary.templates.filter(active=True).update(active=False)

        super(GlosaryTemplate, self).save(*args, **kwargs)


class templated(object):

    @property
    def template(self):
        try:
            tpl = GlosaryTemplate.objects.get(
                glosary__app_label=self._meta.app_label,
                glosary__model_name=self._meta.model_name,
                active=True,
            ).template
        except GlosaryTemplate.DoesNotExist:
            tpl = '<div style="color: red">Template não encontrada</div>'
        finally:
            return engines["django"].from_string(tpl)
            # return Engine().from_string(tpl)


class PartLawsuit(AuditTimestampModel):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="parts", blank=True, on_delete=models.PROTECT
    )
    create_location = models.ForeignKey(
        "rh.Lotacao",
        related_name="created_parts_lawsuit",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    shared_with_lawsuit = models.ManyToManyField(
        OutCourtLawsuit, related_name="shared_parts"
    )
    cache_rendered = models.TextField(null=True, blank=True)
    type_part = models.CharField(max_length=60, null=True, blank=True)
    codename_part = models.CharField(max_length=100, null=True, blank=True)
    signed_by = models.ForeignKey(
        "auth.user",
        related_name="as_signed_by_in_part",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    legal_classification = models.ForeignKey(
        LegalClassification,
        null=True,
        blank=True,
        related_name="generalmotion",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    acting_zone = models.ForeignKey(
        "ActingZone",
        related_name="part_lawsuit_acting_zone",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    unfolded_by = models.ForeignKey(
        "auth.user",
        related_name="as_unfolded_by_in_part",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    unfolded_at = models.DateTimeField(null=True, blank=True)

    search_vector = SearchVectorField(null=True, editable=False)

    allow_instated = False

    class Meta:
        permissions = (
            ("can_sign", "Pode assinar qualquer documento"),
            (
                "can_sign_simples",
                "Pode assinar qualquer documento classificado como simples",
            ),
            ("can_unfold_any_document", "Pode desentranhar qualquer documento"),
        )
        unique_together = (("lawsuit", "page_number"),)
        ordering = (
            "page_number",
            "created_at",
        )

    def at_moment(self):
        return self.signed_at

    def add_shared_with_lawsuit(self, lawsuit):
        EventControl.factory(lawsuit, self)
        self.shared_with_lawsuit.add(lawsuit)

    @property
    def abs_file_cache(self):
        return os.path.join(self.lawsuit.cache_dir, "%s" % self.pk)

    @property
    def cache_filestream_size(self):
        size = 0

        try:
            size = (
                0
                if not os.path.exists(self.abs_file_cache)
                else os.path.getsize(self.abs_file_cache)
            )
        except Exception as e:
            log.exception(e)

        return size

    @property
    def meaning_type(self):
        return MEANING_TYPE_UNDEFINED

    @property
    def sign_permissions(self):
        return ["judicial.can_sign"]

    @property
    def is_initiator(self):
        return False

    def dispatch_comunication(self, subject, external_number=None):
        """
        Este metodo é responsável por entregar as comunicações pendentes.
        """
        for sciency in self.sciences.filter(protocol=None):
            sciency.dispatch()

    @property
    def is_lawsuit_autonumberator(self):
        return True

    @property
    def is_unfolded(self):
        return True if self.unfolded_by else False

    @property
    def can_sign_manifestation_after_deadline(self):
        return True

    @property
    def _only_responsible_sign(self):
        """
        Este método verifica se somente o responsável pelo local pode assinar este movimento. As classes
        que herdam desta deverão possuir o atributo chamado only_responsible_sign. Caso não encontre o atributo
        na classe ou caso o atributo seja sejada como False o software considerará que todos podem assinal.
        Do contrário somente o responsável.
        """
        if hasattr(self, "only_responsible_sign"):
            return self.only_responsible_sign
        return False

    def _who_for_interested(self):
        return tuple(
            {interested.person for interested in self.lawsuit.has_interested.all()}
        )

    def _who_for_accused(self):
        return tuple([bloke.my_origin.bloke for bloke in self.lawsuit.blokes.filter()])

    def _who_for_witness(self):
        return tuple()

    def _who_for_representative(self):
        query = (
            RequestExternalAccess.objects.filter(lawsuit=self.lawsuit)
            .exclude(as_representative_of=None)
            .exclude(authorized_by=None)
            .filter(revoked_by=None, denied_by=None)
        )

        return tuple({rea.person for rea in query})

    def _who_for_owner_executationorgan(self):
        return tuple([self.lawsuit.location.responsavel.pessoa_fisica])

    def _who_for_officer(self):
        query = self.diligences.filter(who_type=7, responsible_delivering__isnull=False)
        return tuple(
            [
                diligence.responsible_delivering.officer_diligence.pessoa_fisica
                for diligence in query
            ]
        )

    def who_are(self, person):
        if person.pk in [p.pk for p in self._who_for_interested()]:
            return 1
        elif person.pk in [p.pk for p in self._who_for_accused()]:
            return 2
        elif person.pk in [p.pk for p in self._who_for_witness()]:
            return 3
        elif person.pk in [p.pk for p in self._who_for_representative()]:
            return 5
        elif person.pk in [p.pk for p in self._who_for_owner_executationorgan()]:
            return 4
        elif person.pk in [p.pk for p in self._who_for_officer()]:
            return 7
        else:
            return 0

    def _who_for_type(self, who_type):
        type_map = {
            1: self._who_for_interested,
            2: self._who_for_accused,
            3: self._who_for_witness,
            4: self._who_for_owner_executationorgan,
            5: self._who_for_representative,
        }

        return type_map.get(who_type, lambda: [])

    def _open_manifestation(self, for_these, who_type, deadline=None, diligence=None):
        if len(for_these) == 0:
            raise Exception("Nenhuma pessoa foi indicada para manifestações.")

        with transaction.atomic():
            for who in for_these:
                log.info("Abrindo manifestação para %s", who)
                self.manifestations.add(
                    Manifestation(
                        who=who,
                        who_type=who_type,
                        deadline=deadline,
                        diligence=diligence,
                    ),
                    bulk=False,
                )

    def open_manifestations(
        self, who=None, who_type=None, deadline=None, diligence=None
    ):
        if not who and not who_type:
            raise Exception(
                "Não é possivel determinar para quem esta sendo aberto espaço  para manifestação."
            )

        if deadline and deadline < datetime.now():
            raise Exception(
                "Não faz sentido abrir espaço para manifestação com prazo encerrado."
            )

        if not who and who_type:
            log.info(
                "Abrir manifestações tendo como base o tipo de pessoa no procedimento."
            )
            if who_type == 3:
                raise Exception("Para testemunha é importante colocar quem é a pessoa.")
            else:
                self._open_manifestation(
                    self._who_for_type(int(who_type or 0))(),
                    who_type,
                    deadline,
                    diligence,
                )

        elif who and not who_type:
            log.info("Abrir manifestações para pessoa no procedimento.")
            self._open_manifestation(
                for_these=[who],
                who_type=self.who_are(who),
                deadline=deadline,
                diligence=diligence,
            )
        elif who and who_type:
            log.info("Abrir manifestações para pessoa no procedimento.")
            self._open_manifestation(
                for_these=[who],
                who_type=who_type,
                deadline=deadline,
                diligence=diligence,
            )
        else:
            raise Exception(
                "Para abrir um espaço para manifestação é preciso ou saber quem é ou como o mesmo esta envolvido no procedimento."
            )

    def publish(self, enable=True):
        log.info([self.is_public, enable])

        if self.is_public == enable:
            raise Exception("Estão ação não implica em nenhuma mudança na publicidade")
        elif enable and self.active_access_controls.exists():
            raise Exception(
                "Não posso dar publicidade a um documento que tem sigilosidade assinado."
            )
        elif enable and self.access_controls.filter(suspended_by=None).exists():
            raise Exception(
                "Não posso dar publicidade a um documento que tem sigilosidade."
            )
        elif enable:
            PublishPart(part=self).save()
        else:
            publish = PublishPart.objects.filter(revoked_by=None).get(part=self)
            publish.revoke()

    def apply_is_public(self, is_public):
        PartLawsuit.objects.filter(pk=self.pk).update(is_public=is_public)
        query = Attached.objects.filter(
            models.Q(attached_document=self.pk)
            | models.Q(attached_diligence__judicialdiligence__part=self.pk)
        )

        for attached in query:
            attached.published_by = get_current_user() if is_public else None
            attached.published_at = datetime.now() if is_public else None
            attached.skip_read_only_validate = True
            attached.save()

    def destroy_document(self):
        if self.signed_by:
            raise Exception("Não posso remover um documento que já foi removido.")

        """
        FIXME: transformar em metodo de OutCourtLawsuit
        """
        self.lawsuit.removed_by = get_current_user()
        self.lawsuit.removed_at = datetime.now()
        self.lawsuit.save()

    def validate_current_location(self):
        try:
            current_moviment = self.lawsuit.current_moviment()
            user = get_current_user()
            servidor = employee_from_user(user)
        except Servidor.DoesNotExist:
            raise Exception(
                "Um servidor que não esta ativo não pode assinar documentos."
            )
        except Exception as e:
            raise e
        else:
            log.info(
                "Movimentação corrente para: %s", current_moviment.lotacao_destino.pk
            )
            log.info("Usuário: %s", user)
            log.info("Servidor: %s", servidor)
            log.info("Locais de trabalho: %s", [l.pk for l in servidor.work_locations])

            if not self.lawsuit.is_acting:
                raise Exception("O documento não esta na posse do usuário.")

        return True

    @property
    def extra_pages_of_diligences(self):
        pages = []

        if self.can_read:
            for diligence in self.diligences.order_by("signed_at"):
                pages.append(
                    {
                        "at": (
                            diligence.signed_at
                            if diligence.signed_at
                            else datetime.now()
                        ),
                        "page": diligence.rendered,
                    }
                )

                for attaches in diligence.attaches.filter():
                    pages += [
                        {
                            "page": page.get("page"),
                            "at": (
                                diligence.signed_at
                                if diligence.signed_at
                                else datetime.now()
                            ),
                        }
                        for page in attaches.extract_pages()
                    ]

                for delivery in diligence.deliveryattempt_set.filter():
                    pages.append({"at": delivery.exit_date, "page": delivery.rendered})

        return pages

    @property
    def extra_pages_attached(self):
        pages = []

        if self.can_read:
            for attached in self.attaches.filter():
                pages += attached.extract_pages()

            if self.is_unfolded:
                for page in pages:
                    page.update({"extra_classes": "unfolded"})

        return pages

    @property
    def extra_pages(self):
        return self._extra_pages() if self.can_read else []

    @property
    def extra_pages_complete(self):
        return self._all_extra_pages_complete() if self.can_read else []

    @property
    def extra_pages_unfold(self):
        if self.can_read:
            return [
                {
                    "extra_classes": "unfolded",
                    "at": self.created_at,
                    "page": "".join(self._get_page_document_renderer(self.my_origin)),
                }
            ]
        else:
            return []

    @property
    def get_page_certificate_unfold(self):
        if not self.unfolder.exists():
            return "<h1>Erro ao gerar o certificado de desentranhamento</h1>"

        doc = self.unfolder.first()

        data = [
            loader.get_template("judicial/lawsuit/certificate_unfold.html").render(
                {
                    "event": self.event_control,
                    "sign": {
                        "moment_at": doc.signed_at,
                        "person": (
                            doc.signed_by.servidor.pessoa_fisica
                            if doc.signed_by
                            else None
                        ),
                        "organ": doc._get_organ_signer() if doc.signed_by else None,
                    },
                }
            )
        ]

        data += [sign.rendered for sign in doc.get_legal_signs]

        if doc.get_legal_signs.exists():
            data.append(
                loader.get_template("judicial/legal_sign_fundament.html").render({})
            )

        return "".join(data)

    def _all_extra_pages_complete(self):
        if self.is_unfolded:
            return (
                self.extra_pages_unfold
                + self.extra_pages_attached
                + self.extra_pages_of_diligences
                + self.extra_pages_of_manifestation
            )

        return (
            self.extra_pages_attached
            + self.extra_pages_of_diligences
            + self.extra_pages_of_manifestation
        )

    def _extra_pages(self):
        if self.can_read:
            pages = self._all_extra_pages_complete()
            return [
                page.get("page")
                for page in sorted(pages, key=lambda d: d.get("at") or datetime.now())
            ]
        else:
            return []

    @property
    def extra_pages_of_manifestation(self):
        pages = []

        if self.can_read:
            for manifestation in self.manifestations.exclude(signed_by=None).order_by(
                "signed_at"
            ):
                pages.append(
                    {"at": manifestation.signed_at, "page": manifestation.renderer}
                )

                for attaches in manifestation.attaches.filter():
                    pages += [
                        {
                            "page": page.get("page"),
                            "at": (
                                manifestation.signed_at
                                if manifestation.signed_at
                                else datetime.now()
                            ),
                        }
                        for page in attaches.extract_pages()
                    ]

        return pages

    @property
    def collaborator_can_sign(self):
        return (
            self.legal_classification
            and not self.legal_classification.collaborator_can_sign
        )

    @property
    def sign_part_authorized(self):
        return self._sign_part_authorized()

    def _sign_part_authorized(self):
        user = get_current_user()

        if self.lawsuit.is_acting_as_collaborator and self.collaborator_can_sign:
            raise Exception("Colaborador não pode assinar esse documento")

        flag = False
        for perm in self.sign_permissions:
            if user.has_perm(perm):
                flag = True
                break

        return flag

    @property
    def is_instanted(self):
        return self.lawsuit.number_lawsuit and self.lawsuit.year

    @property
    def get_part_legal_sign(self):
        return PartLegalSign

    def sign_part(self):
        if not self.allow_instated and not self.is_instanted:
            raise Exception(
                "Não foi possível assinar o documento. Pois o procedimento ainda não foi instaurado."
            )

        if self.sign_part_authorized:
            """
            marcando documento como assinado e limpando o cache de renderização
            """
            self.cache_rendered = None
            self.signed_by = get_current_user()
            self.signed_at = datetime.now()
            self.save()

            if self.my_origin.is_initiator:
                self.lawsuit.acting_zone = self.my_origin.acting_zone
                self.lawsuit.save()
            """
            atualizando o valor do cache de renderização
            """
            self.__class__.objects.filter(pk=self.pk).update(
                cache_rendered=self.rendered
            )

            self.my_origin.get_part_legal_sign.sign(self.my_origin)
            OutCourtLawsuit.update_last_part_lawsuit(self.lawsuit)
            self.lawsuit.refresh_from_db()

            EventControl.objects.create(
                lawsuit=self.lawsuit,
                part=self,
                number_control=self.lawsuit.next_number_control(),
            )
            OutCourtLawsuitLog.register(self.lawsuit, self.my_origin)

            if NoticeConfiguration.objects.filter(
                legal_classification=self.legal_classification
            ).exists():
                noticies = NoticeConfiguration.objects.filter(
                    legal_classification=self.legal_classification
                )
                for noticie in noticies:
                    for departament in noticie.departament.all():
                        scientify = ScientifyWorkplace(
                            part=self, location=departament, content=self.rendered
                        )
                        scientify.save()
                        scientify.dispatch()

        else:
            raise Exception(
                "O usuário %s não tem permissão para assinar esse documento"
                % get_current_user()
            )

    def sign_moviment(self):
        moviment = self.lawsuit.current_moviment()

        if not moviment:
            log.info("Não consegui encontrar a movimentação corrente.")
        elif moviment and not moviment.data_recebimento:
            moviment.data_recebimento = datetime.now()
            moviment.servidor_destino = employee_from_user(get_current_user())
            moviment.save()
            log.info(
                "Recebendo a movimentação %d do protocolo %s.",
                moviment.passo,
                moviment.protocolo.codigo,
            )
        else:
            log.info(
                "A movimentação %d do protocolo %s foi recebida por %s.",
                moviment.passo,
                moviment.protocolo.codigo,
                moviment.servidor_destino.pessoa_fisica,
            )

    def _send_to_council(self, parecer_template=""):
        cfg = Configuration.objects.get(application="ejud")

        try:
            council = Lotacao.objects.get(pk=cfg.get("csmpLocation", None))
        except Lotacao.DoesNotExist:
            raise Exception(
                "Não consegui encontrar o destinho do Conselho Superior do Ministério Público."
            )
        else:
            log.debug(
                "Lotacao atual: %s", self.lawsuit.current_moviment().lotacao_destino
            )

            if (
                self.lawsuit.location.pk
                == self.lawsuit.current_moviment().lotacao_destino.pk
            ):
                log.info(
                    "Autos %s remetidos para %s", self.lawsuit.origin.codigo, council
                )
                self.lawsuit.send_to(to=council, parecer_template=parecer_template)
                # self.lawsuit.deadline_cache = None
                self.lawsuit.remaining_days = None
                self.lawsuit.location = council
                self.lawsuit.save()
            else:
                raise Exception(
                    "Aparentemente este procedimento não esta mais em sua posse."
                )

    def validate_ownership(self):
        if not self.lawsuit.current_moviment():
            raise Exception(
                "Você não pode modificar um procedimento que não esta em sua posse."
            )

    @property
    def model_part_type(self):
        return self._meta.model_name

    def __str__(self):
        return self.my_origin.title

    @property
    def my_origin(self):
        if self.pk:
            if hasattr(self, self.type_part):
                obj = getattr(self, self.type_part, self)

                return obj
            else:
                return self
        else:
            return self

    @property
    def glossary(self):
        try:
            return Glosary.objects.get(
                app_label=self._meta.app_label, model_name=self._meta.model_name
            )
        except Glosary.DoesNotExist:
            return None

    @property
    def default_legal_classification(self):
        return (
            self.legal_classification
            if self.legal_classification
            else self.glossary_classification
        )

    @property
    def glossary_classification(self):
        glossary = self.glossary
        return glossary.legal_classification if glossary else None

    @property
    def need_sign(self):
        return False

    @property
    def signed(self):
        return self.signed_by and self.signed_at

    @property
    def template(self):
        try:
            tpl = GlosaryTemplate.objects.get(
                glosary__app_label=self._meta.app_label,
                glosary__model_name=self._meta.model_name,
                active=True,
            ).template
        except GlosaryTemplate.DoesNotExist:
            tpl = '<div style="color:red">Template não encontrada</div>'
        finally:
            """
            FIXME: veja que a engine de carga de template esta fixa.
            """
            return engines["django"].from_string(tpl)

    def _get_organ_signer(self):
        organ = None
        if not getattr(self, "diligence", None):
            organ = self.lawsuit.location
        else:
            if (
                self.signed_by
                and self.signed_by.servidor.work_assignment_effective_exercise.filter(
                    main=True
                )
            ):
                organ = (
                    self.signed_by.servidor.work_assignment_effective_exercise.filter(
                        main=True
                    )
                    .first()
                    .lotacao
                )
            elif self.signed_by and self.signed_by.servidor.workplace_only.filter(
                ativo=True
            ):
                organ = (
                    self.signed_by.servidor.workplace_only.filter(ativo=True)
                    .first()
                    .lotacao
                )

        return organ

    def params(self):
        rst = {"doc": self, "execution_organ": self._get_organ_signer()}

        try:
            rst.update(
                {
                    "name": self.title,
                    "created_at": nil_datetime(self.created_at, "ERROR"),
                    "created_by": nil_person_user(self.created_by, "ERROR"),
                    "modified_at": nil_datetime(self.modified_at, "Não foi modificado"),
                    "modified_by": nil_person_user(
                        self.modified_by, "Não foi modificado"
                    ),
                }
            )
        except Exception:
            rst.update(
                {
                    "name": self.title,
                    "created_at": nil_datetime(datetime.now(), "ERROR"),
                    "created_by": nil_person_user(get_current_user(), "ERROR"),
                    "modified_at": None,
                    "modified_by": None,
                }
            )

        return rst

    codename = "Generic PartLawsuit"

    @property
    def title(self):
        return self.codename

    @property
    def read_only(self):
        employee = employee_from_user(get_current_user())

        if self.lawsuit.is_acting:
            return True if self.signed_by else False
        else:
            return True

    @property
    def get_legal_signs(self):
        return self.legal_signs.filter()

    def _get_page_document_renderer(self, doc):
        data = [
            (
                doc.template.render(self.params())
                if not doc.cache_rendered
                else doc.cache_rendered
            )
        ]
        data += [sign.rendered for sign in doc.get_legal_signs]

        if doc.get_legal_signs.exists():
            data.append(
                loader.get_template("judicial/legal_sign_fundament.html").render({})
            )

        return data

    @property
    def rendered(self):
        if self.can_read:
            if self.unfolded_by:
                return self.get_page_certificate_unfold

            return "".join(self._get_page_document_renderer(self.my_origin))
        else:
            return "<h1>Documento com Controle de Acesso</h1>"

    def _create_lockfile(self):
        if not os.path.exists(self.lawsuit.cache_dir):
            os.makedirs(self.lawsuit.cache_dir)

        with open(os.path.join(self.lawsuit.cache_dir, "%d.lock" % self.pk), "w+"):
            pass

    def create_cache_document(self, force=None):
        if force or not self.exists_cache_document_in_lawsuit:
            from judicial.tasks.realtime import create_cache_document

            user = get_current_user()
            voucher = DisposableVoucher.objects.create(user=user)

            self._create_lockfile()
            create_cache_document.delay(voucher.jwt, self.pk, user.pk)

    def invalidate_cache(self):
        if self.exists_cache_document_in_lawsuit:
            os.remove(self.abs_file_cache)

    @property
    def exists_cache_document_in_lawsuit(self):
        destination = os.path.join(self.lawsuit.cache_dir, "%d" % (self.pk))
        return os.path.exists(destination)

    @property
    def exists_valid_lock_document(self):
        lock_file = os.path.join(self.lawsuit.cache_dir, "%d.lock" % (self.pk))
        if not os.path.exists(lock_file):
            return False
        else:
            file_stats = os.stat(lock_file)
            if (time.time() - file_stats.st_mtime) > 300:
                return False
            else:
                return True

    @property
    def url_cache(self):
        return "%s%s/%d/" % (settings.ATHENAS, settings.JUDICIAL_URL_PDF, self.pk)

    @property
    def abs_url_cache(self):
        return "/%s%s/%d/" % (settings.CONTEXT, settings.JUDICIAL_URL_PDF, self.pk)

    @property
    def cache_filestream(self):
        pdf_file = settings.JUDICIAL_PDF_PROCESSING

        if self.exists_cache_document_in_lawsuit:
            pdf_file = self.abs_file_cache
        elif not self.exists_valid_lock_document:
            self.create_cache_document()

        etag = self.get_etag_cache(pdf_file)

        class __PartLawsuitCacheFileStream:
            def __init__(self):
                self.stream = open(pdf_file, "rb")
                self.etag = etag

            def __enter__(self):
                return self

            def __exit__(self, *args, **kwargs):
                self.stream.close()

        return __PartLawsuitCacheFileStream

    def get_etag_cache(self, file):
        file_stats = os.stat(file)
        return hashlib.md5(str(file_stats.st_mtime).encode("utf-8")).hexdigest()

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-uknow"

    @property
    def signed_icon(self):
        return {
            "iconCls": "icon-judicial icon-ejud-%ssigned"
            % ("" if self.signed else "un"),
            "title": "Assinado" if self.read_only else "Não foi assinado",
        }

    @property
    def read_only_icon(self):
        return {
            "iconCls": "icon-judicial icon-ejud-read-only%s"
            % ("" if self.read_only else "-no"),
            "title": (
                "Somente para leitura" if self.read_only else "Pode sofre alterações"
            ),
        }

    @property
    def active_access_controls(self):
        return self.access_controls.exclude(signed_by=None).filter(suspended_by=None)

    @property
    def can_read(self):
        user = get_current_user()
        employee = employee_from_user(user)

        log.info(
            'Verificando direito de acesso ao documento para "%s" ao documento "%s" do procedimento "%s".'
            % (str(user), str(self), self.lawsuit.cache_number)
        )

        if (
            self.active_access_controls.exists()
            or self.lawsuit.active_access_controls.exists()
        ):
            return self.user_has_perm_control_access(user)
        else:
            if user.has_perm("judicial.outcourtlawsuitadmin"):
                return True
            elif self.lawsuit.is_acting:
                return True
            elif self.lawsuit.all_signed_documents.filter(
                diligences__responsible_delivering__officer_diligence=employee_from_user(
                    user
                )
            ):
                return True
            elif (
                self.signed_by
                and employee.work_locations.filter(
                    pk__in=self.lawsuit.origin.cronologic_moviments.values_list(
                        "lotacao_origem", flat=True
                    )
                ).exists()
            ):
                return True
            else:
                for lawsuit in self.shared_with_lawsuit.all():
                    if lawsuit.is_acting:
                        return True

                return False

    def user_has_perm_control_access(self, user):
        person = person_from_user(user)
        queryP = self.active_access_controls.filter(
            Q(authorization__person=person) & Q(authorization__state__in=(1, 2))
        )
        queryL = self.lawsuit.active_access_controls.filter(
            Q(authorization__person=person) & Q(authorization__state__in=(1, 2))
        )

        for query in (queryP, queryL):
            if query.exists():
                log.info("Numero de autorizações: %d", query.count())
                log.info("Extrato:")
                for control in query:
                    authorization = (
                        control.authorization.filter(person=person, state__in=(1, 2))
                        .order_by("state")
                        .first()
                    )
                    log.info("Estado: %s", authorization.get_state_display())

                if query.exists():
                    log.info("Numero de autorizações: %d", query.count())
                    log.info("Extrato:")
                    for control in query:
                        authorization = (
                            control.authorization.filter(
                                person=person_from_user(get_current_user()),
                                state__in=(1, 2),
                            )
                            .order_by("state")
                            .first()
                        )
                        log.info("Estado: %s", authorization.get_state_display())

                    if query.exists():
                        return True

        return False

    @property
    def icon_access_control(self):
        if self.lawsuit.active_access_controls.exists():
            return {
                "iconCls": "icon-judicial icon-ejud-part-access",
                "title": "Com controle de acesso no Procedimento",
            }
        elif self.active_access_controls.exists():
            return {
                "iconCls": "icon-judicial icon-ejud-part-access",
                "title": "Com controle de acesso",
            }
        elif (
            self.access_controls.filter(suspended_by=None)
            .exclude(signed_by=None)
            .exists()
        ):
            return {
                "iconCls": "icon-judicial icon-ejud-part-access-edit",
                "title": "Com controle de acesso em construção",
            }
        elif self.is_public:
            return {
                "iconCls": "icon-judicial icon-ejud-public",
                "title": "Foi dado publicidade no portal de atendimento ao cidadão.",
            }

    @property
    def icons(self):
        return [self.signed_icon, self.icon_access_control]

    @property
    def number_pages(self):
        qt = 0
        for at in self.attaches.filter():
            qt += at.number_pages if at.number_pages else 0
        return qt

    @property
    def event_control(self):
        return (
            self.has_event_controls.first()
            if self.has_event_controls.exists()
            else None
        )

    @property
    def number_event_control(self):
        return EventControl.number_control_of(self.lawsuit, self)

    @property
    def change_location_to(self):
        return None

    def delete(self, *args, **kwargs):
        if self.signed:
            raise Exception("Não é possivel remover uma peça assinada.")

        if (
            hasattr(self.my_origin, "destroy_document")
            and not self.lawsuit.all_documents.exclude(pk=self.pk).exists()
        ):
            log.info(
                "destroy document? %s",
                ("sim" if hasattr(self.my_origin, "destroy_document") else "nao"),
            )
            log.info(
                "number of signed documents: %d",
                self.lawsuit.all_signed_documents.exclude(pk=self.pk).count(),
            )
            self.my_origin.destroy_document()

        super(PartLawsuit, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk and not hasattr(self, "decision_store"):
            older = self.__class__.objects.get(pk=self.pk)
            if older.read_only and not getattr(self, "skip_read_only_validate", False):
                raise Exception(
                    "Este documento não pode mais ser modificado pois já foi assinado."
                )

        # self.type_part = self._meta.model_name
        self.type_part = self.model_part_type
        self.codename_part = self.my_origin.codename

        if not self.create_location:
            self.create_location = self.lawsuit.location

        if not getattr(self, "skip_sign_current_moviment", False):
            self.sign_moviment()

        if not getattr(self, "skip_validade_ownership", False):
            self.validate_ownership()

        if self.signed_by and not self.page_number:
            self.page_number = self.lawsuit.next_page()
        elif self.signed_by and self.page_number:
            log.info("Verificando conflito de paginação.")
            if self.lawsuit.conflict_page_number(self):
                log.info("Conflito de paginação encontrado")
                self.lawsuit.reordenate_documents_by(self)

        if self.legal_classification is None:
            self.legal_classification = self.default_legal_classification

        super(PartLawsuit, self).save(*args, **kwargs)

        self.lawsuit.last_part_lawsuit_signed

    @property
    def my_reminders(self):
        user = get_current_user()
        employee = employee_from_user(user)
        workplaces = [sl.lotacao for sl in employee.work_assignment_effective_exercise]

        collaborations = self.lawsuit.requestcollaboration.filter(
            canceled_by__isnull=True
        )
        for collab in collaborations:
            if collab.my_origin.is_to_user(user):
                workplaces.append(collab.origin_location.lotacao)

        return self.reminders.filter(
            Q(created_by=user)
            | Q(access_level=Reminder.PUBLIC)
            | Q(workplace__in=workplaces)
        ).exclude(deactivated_by__isnull=False)


class InitialPartlawsuit(object):

    @property
    def is_lawsuit_autonumberator(self):
        return False

    @property
    def lawsuit_title(self):
        raise Exception("abstract property not implemented")

    @property
    def content_processed(self):
        try:
            return re.sub(
                r"<!-- begin header -->.*<!-- end header -->",
                "",
                self.rendered.replace("\n", ""),
            )
        except Exception as e:
            return str(e)

    def _docketing_protocol(self):
        p = Protocolo.docketing(
            self.lawsuit_title,
            TipoDocumento.objects.get(pk=4),
            movement_id=None,
            interested=getattr(
                self, "interested", person_from_user(get_current_user())
            ),
            seal_number=None,
            media=1,
            home_court=self.location,
            external_number=None,
            content="<p>Este protocolo instaura um novo Procedimento</p>",
        )

        return p

    def _calculate_deadline_date(self):
        raise Exception("abstract method not implemented")

    def _lawsuit_type(self):
        raise Exception("abstract method not implemented")

    def current_moviment_protocol(self, protocol=None):
        employee = employee_from_user(get_current_user())

        locations = [wl for wl in employee.work_locations if wl.pk == self.location.pk]
        qset = EDOCBoxQuery(servidor=employee, lotacoes=locations)

        moviment = (
            qset.get_caixa_entrada().filter(protocolo=protocol).order_by("id").last()
        )

        return moviment

    def _create_lawsuit(self, protocol=None):
        lawsuit = OutCourtLawsuit(
            title=self.lawsuit_title,
            location=self.location,
            type_lawsuit=self._lawsuit_type(),
            # deadline_cache=self._calculate_deadline_date(),
            remaining_days=self._calculate_deadline_date(),
        )

        if not protocol and self.interested:
            lawsuit.origin = self._docketing_protocol()

        moviment = None

        if protocol:
            moviment = self.current_moviment_protocol(protocol=protocol)

        log.debug(
            [
                getattr(self, "skip_with_workflow_validator", False),
                (protocol and moviment.with_workflow),
            ]
        )

        if protocol and not moviment.with_workflow:
            moviment.with_workflow = True
            moviment.save()
        elif getattr(self, "skip_with_workflow_validator", False) and (
            protocol and moviment.with_workflow
        ):
            raise Exception("O protocolo já faz parte de um procedimento.")

        lawsuit.origin = protocol if not lawsuit.origin else lawsuit.origin
        lawsuit.save()
        return lawsuit

    def validate_ownership(self):
        if not self.lawsuit.is_acting:
            raise Exception(
                "Você não pode modificar um procedimento que não em sua posse."
            )

    def _sign_lawsuit_prepare(self):
        if not self.is_instanted:
            self.lawsuit.year = date.today().year
            self.lawsuit.number_lawsuit = self.lawsuit.next_number(self.lawsuit.year)

        self.lawsuit.type_lawsuit = self._lawsuit_type()
        # self.lawsuit.deadline_cache = self._calculate_deadline_date()
        self.lawsuit.remaining_days = self._calculate_deadline_date()
        self.lawsuit.save()

    def _post_save_trigger(self):
        if (
            hasattr(self, "interested")
            and not Interested.objects.filter(
                lawsuit=self.lawsuit, person=self.interested
            ).exists()
        ):
            Interested(lawsuit=self.lawsuit, person=self.interested, direct=True).save()

        if self.protocol_origin:
            for attachment in self.protocol_origin.attachments.filter():
                Attached(
                    attached_document=self,
                    title=attachment.title,
                    file_descriptor=attachment.attach,
                ).save()

    @property
    def is_initiator(self):
        return True


class PublishPart(AuditTimestampModel):
    part = models.ForeignKey(
        PartLawsuit, related_name="authorizartion_for_publish", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    revoked_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def revoke(self):
        self.revoked_at = datetime.now()
        self.revoked_by = get_current_user()
        self.save()

    def save(self, *args, **kwags):
        super(PublishPart, self).save(*args, **kwags)

        is_public = None

        if self.revoked_by and self.part.is_public:
            is_public = False
        elif not self.revoked_by and not self.part.is_public:
            is_public = True

        if is_public is not None:
            self.part.my_origin.apply_is_public(is_public)


class County(AuditTimestampModel):
    title = models.CharField(max_length=100)
    address = models.ForeignKey(
        Address,
        related_name="counties",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    locations = models.ManyToManyField("rh.Localidade", related_name="counties")
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, blank=True, null=True
    )

    @property
    def phones(self):
        return list(
            self.locations.filter(
                lotacao__nome__icontains="sede", lotacao__ativo=True
            ).values(
                numero=F("lotacao__phone__numero"),
                principal=F("lotacao__phone__main"),
                publico=F("lotacao__phone__publico"),
                tipo=F("lotacao__phone__tipo_telefone"),
                desc=F("lotacao__phone__description"),
            )
        )

    @property
    def coordinate(self):
        return (
            f"[{self.latitude}, {self.longitude}]"
            if self.latitude and self.longitude
            else None
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("title",)


class Sectional(models.Model):
    county = models.ForeignKey(
        County,
        related_name="in_sections",
        verbose_name="Comarca",
        on_delete=models.PROTECT,
    )
    title = models.CharField(max_length=120, db_index=True, verbose_name="Título")

    class Meta:
        ordering = ("county__title", "title")
        unique_together = ("county", "title")

    def __str__(self):
        return self.title


class ExecutionOrgan(Lotacao):
    general_distribution = models.BooleanField(default=True)
    attribution = models.CharField(
        max_length=4000, db_index=True, blank=True, verbose_name="Atribuição"
    )
    attribution_document = models.ForeignKey(
        "rh.Publicacao",
        on_delete=models.CASCADE,
        verbose_name="Documento de atribuição",
        related_name="executionorgan_attribution_document",
        null=True,
        blank=True,
    )  # Parametro "on_delete" adicionado. (Django 2)
    occupation_area = models.CharField(
        max_length=4000,
        db_index=True,
        null=True,
        blank=True,
        verbose_name="Área de atuação",
    )

    @property
    def employees(self):
        return super(ExecutionOrgan, self).employees.filter(tipo="M")

    @property
    def employee_workplaces_responsible(self):
        return super(ExecutionOrgan, self).employee_workplaces_responsible.filter(
            servidor__tipo="M"
        )

    @property
    def employee_exercise(self):
        return super(ExecutionOrgan, self).employee_exercise.filter(servidor__tipo="M")

    @property
    def active_matters(self):
        return self.in_distribution_tables.filter(
            models.Q(
                models.Q(document__data_vigencia__lte=date.today())
                & models.Q(end_document__isnull=True)
            )
            | models.Q(
                models.Q(document__data_vigencia__lte=date.today())
                & models.Q(end_document__data_vigencia__gt=date.today())
            )
        )

    @property
    def counties(self):
        return self.localidade.counties.all()

    def owner_unicode(self):
        owner = self.owner_for_cache
        return str(owner.pessoa_fisica) if owner else None

    def employee_exercise_unicode(self):
        exercise = ""
        for ex in self.employee_exercise.order_by("-owner"):
            publication = (" - %s" % ex.publicacao) if ex.publicacao else ""

            type_exercise = ""
            if ex.lotacao.owner.filter(pk=ex.servidor.pk).exists():
                type_exercise = ""
            elif ex.substitution_substitute.filter(ordinance=True).exists():
                type_exercise = "Substituição Por Portaria"
            elif ex.ordinance is True:
                type_exercise = "Designação Por Portaria"
            elif ex.ordinance is False:
                type_exercise = "Substituição Automática"
                identify = ex.lotacao.my_substitute_by_employee_order(ex.servidor)
                workplace_substitute = identify.get("workplace_substitute")
                order = 0
                for elem in workplace_substitute:
                    if order == 0:
                        order = elem.get("order")
                    elif elem.get("substitute") != self.pk and order < elem.get(
                        "order"
                    ):
                        order = elem.get("order")

                if order != 0:
                    type_exercise = "%s - %s" % (type_exercise, order)
                else:
                    type_exercise = "Exercício"

            buff_employee = "%s" % str(ex.servidor)

            if type_exercise:
                type_exercise = " - %s %s" % (type_exercise, publication)
                buff_employee = "%s %s" % (buff_employee, type_exercise)

            if exercise:
                exercise += " | "
                exercise += buff_employee
            else:
                exercise = buff_employee
        return exercise

    def employee_workplaces_responsible_unicode(self):
        responsible = None
        for ex in self.employee_workplaces_responsible.order_by("-owner"):
            if responsible is not None:
                responsible += " | "
                responsible += "%s" % str(ex.servidor)
            else:
                responsible = "%s" % str(ex.servidor)
        return responsible

    def job_position_execution(self):
        """
        :py:function:: job_position_execution(self)

        This method makes a interface to Employee.substitutes and finds responsible definition.

        :return:
        :rtype: list
        """
        replacement = {}
        for substitute in self.substitutes().values(
            "replaced",
            "replaced__nome",
            "substitute",
            "substitute__nome",
            "order",
            "substitute__servidores_lotacao__pk",
            "substitute__servidores_lotacao__servidor__matricula",
            "substitute__servidores_lotacao__servidor__pessoa_fisica__nome",
        ):
            sub = {
                "cargo_subs": substitute.get("substitute"),
                "cargo_subs_nome": substitute.get("substitute__nome"),
                "order": substitute.get("order"),
                "servidor": substitute.get(
                    "substitute__servidores_lotacao__servidor__pessoa_fisica__nome"
                ),
            }
            if substitute.get("replaced") not in replacement:
                replaced = {
                    "cargo": substitute.get("replaced"),
                    "cargo_nome": substitute.get("replaced__nome"),
                    "exercicio_pleno": True,
                    "possui_substituto": True if sub else False,
                    "substitutos": [sub],
                    "afastado": self.afastamento_ativo(),
                }
                replacement.update({substitute.get("replaced"): replaced})
            else:
                replacement[substitute.get("replaced")].get("substitutos").append(sub)
        return list(replacement.values())

    def increment_score_for_matter(self, matter):
        obj, created = DistributionScore.objects.get_or_create(
            execution_organ=self, matter=matter
        )

        if created:
            obj.score = 0
            obj.save()

        obj.score += 1
        obj.total += 1
        obj.save()
        log.info(
            "Incrementada o score de distribuição para %s no assunto %s",
            self.nome,
            matter,
        )

    def set_score_for_matter(self, matter, score):
        obj, created = DistributionScore.objects.get_or_create(
            execution_organ=self, matter=matter
        )
        obj.score = score
        obj.save()

    def get_score_for_matter(self, matter):
        obj, created = DistributionScore.objects.get_or_create(
            execution_organ=self, matter=matter
        )

        if created:
            obj.score = 0
            obj.save()

        return obj.score

    def __str__(self):
        return "%s" % (self.nome)

    @classmethod
    def migrate_fields(cls):
        # for eo in ExecutionOrgan.objects.filter(nome__icontains='07ª PROMOTORIA DE JUSTIÇA DA CAPITAL'):
        for eo in ExecutionOrgan.objects.filter():
            print(eo)
            print(eo.descricao)
            dts = eo.in_distribution_tables.select_related("document").all()
            dt = dts.filter(end_document__isnull=True).first()
            print(dt)
            print(dt.document if dt else None)
            ExecutionOrgan.objects.filter(pk=eo.pk).update(
                occupation_area=eo.descricao,
                attribution_document=dt.document if dt else None,
            )
            print("-----------------")


class DistributionTable(models.Model):
    execution_organ = models.ForeignKey(
        ExecutionOrgan, related_name="in_distribution_tables", on_delete=models.PROTECT
    )
    matter = models.ForeignKey(
        LegalMatter, related_name="in_distribution_tables", on_delete=models.PROTECT
    )
    sectional = models.ForeignKey(
        Sectional,
        related_name="in_distribution_tables",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    factor = models.DecimalField(max_digits=12, decimal_places=4)
    document = models.ForeignKey(
        "rh.Publicacao", related_name="in_distribution_tables", on_delete=models.PROTECT
    )
    end_document = models.ForeignKey(
        "rh.Publicacao",
        related_name="in_distribution_table_has_end",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ("-document__data_vigencia", "-factor")

    def __str__(self):
        return "%s - %s" % (self.matter, self.document)


class DistributionScore(models.Model):
    execution_organ = models.ForeignKey(
        ExecutionOrgan, related_name="in_distribution_scores", on_delete=models.PROTECT
    )
    matter = models.ForeignKey(
        LegalMatter,
        related_name="in_distribution_scores",
        null=True,
        on_delete=models.PROTECT,
    )
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)


@type_part_lawsuit()
class Triage(PartLawsuit):
    triage_number = models.IntegerField(blank=True)
    triage_year = models.IntegerField(blank=True)
    effected_at = models.DateTimeField(null=True, blank=True)
    effected_by = models.ForeignKey(
        "auth.user",
        related_name="effected_triages",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def delivery(self):
        cfg = Configuration.objects.get(application="ejud")

        if self.effected_by:
            raise Exception(
                "Não posso realizar entrega de um procedimento já entregue."
            )

        for part in self.parts.filter(distributed__isnull=True):
            part.do_concurrence()

        destinations = []
        destination_matter = {}
        destination_triage_part = {}
        destination_city = {}

        for part in self.parts.filter():
            log.info(
                "Entregar a segmentação do procedimento %s no assunto %s para %s",
                self.lawsuit.cache_number,
                part.matter.title,
                part.distributed,
            )

            destination = part.delivery()
            if destination not in destinations:
                destinations.append(destination)

            db = destination_matter.get(destination.pk, [])
            db.append(part.matter)
            destination_matter.update({destination.pk: db})

            db = destination_triage_part.get(destination.pk, [])
            db.append(part)
            destination_triage_part.update({destination.pk: db})

            if destination.pk in destination_city:
                db = destination_city.get(destination.pk)
                for tpl in TriagePartLocation.objects.filter(triagepart=part):
                    db.append(tpl.location)
            else:
                db = []

                for tpl in TriagePartLocation.objects.filter(triagepart=part):
                    db.append(tpl.location)

                destination_city.update({destination.pk: db})

        if len(destinations) == 0:
            raise Exception("Não consegui definir nenhum destino para o procedimento.")

        self.effected_at = datetime.now()
        self.effected_by = get_current_user()

        first_destination = destinations[0]
        parts_triage = destination_triage_part.get(first_destination.pk, [])
        first_triage_part = parts_triage[0] if parts_triage else None

        first_matter = destination_matter.get(first_destination.pk, [])[0]

        self.lawsuit.__class__.objects.filter(pk=self.lawsuit.pk).update(
            main_matter=first_matter,
            acting_zone=first_triage_part.acting_zone,
        )

        self.sign_part()

        if len(destinations) > 1:
            log.info("Distribuir procedimentos a mais de uma promotoria.")
            oldparts = PartLawsuit.objects.filter(
                models.Q(lawsuit=self.lawsuit)
                | models.Q(shared_with_lawsuit=self.lawsuit)
            ).exclude(signed_by=None)

            with transaction.atomic():
                for destination in destinations[1:]:
                    log.info("Derivar protocol de noticia de fato para %s", destination)
                    lawsuit = OutCourtLawsuit.objects.create(
                        title=self.lawsuit.title,
                        location=self.lawsuit.location,
                        origin=self.lawsuit.origin,
                    )
                    lawsuit.year = date.today().year
                    lawsuit.number_lawsuit = lawsuit.next_number(lawsuit.year)
                    lawsuit.cache_number = lawsuit.format_cache_number(
                        lawsuit.number_lawsuit, lawsuit.year
                    )

                    lawsuit.remaining_days = OutCourtLawsuit.remainig_days_type_lawsuit(
                        lawsuit
                    )
                    lawsuit.location = destination

                    for matter in destination_matter.get(destination.pk, []):
                        lawsuit.main_matter = matter

                    for triage_part in destination_triage_part.get(destination.pk, []):
                        lawsuit.acting_zone = triage_part.acting_zone

                    lawsuit.save()

                    LawsuitMatter.register_principal_matter(
                        lawsuit=lawsuit, matter=lawsuit.main_matter
                    )

                    [
                        lawsuit.city_locations.add(a)
                        for a in destination_city.get(destination.pk, [])
                    ]

                    for oldpart in oldparts:
                        oldpart.add_shared_with_lawsuit(lawsuit)
                        OutCourtLawsuitLog.register(lawsuit, oldpart)

        self.lawsuit.location = first_destination

        if first_triage_part:
            self.lawsuit.acting_zone = first_triage_part.acting_zone

        self.lawsuit.send_to(destinations)

        self.lawsuit.remaining_days = OutCourtLawsuit.remainig_days_type_lawsuit(
            self.lawsuit
        )

        for matter in destination_matter.get(first_destination.pk, []):
            self.lawsuit.main_matter = matter

        self.lawsuit.save()

        LawsuitMatter.register_principal_matter(
            lawsuit=self.lawsuit, matter=self.lawsuit.main_matter
        )

        for city in destination_city.get(first_destination.pk, []):
            self.lawsuit.city_locations.add(city)

        Interested.objects.filter(lawsuit=self.lawsuit).update(direct=False)
        if Interested.objects.filter(
            lawsuit=self.lawsuit, person=self.lawsuit.origin.interessado
        ).exists():
            Interested.objects.filter(
                lawsuit=self.lawsuit, person=self.lawsuit.origin.interessado
            ).update(direct=True)
        else:
            Interested(
                person=self.lawsuit.origin.interessado,
                direct=True,
                lawsuit=self.lawsuit,
            ).save()

    def _next_number(self):
        Model = self.__class__

        max_number = (
            Model.objects.filter(triage_year=date.today().year)
            .aggregate(max_number=models.Max("triage_number"))
            .get("max_number", 0)
        )

        return int(max_number or 0) + 1

    @property
    def formated_number(self):
        return "%06d/%d" % (int(self.triage_number or 0), int(self.triage_year or 0))

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-triage"

    codename = "Distribuição - Órgão de execução"

    @property
    def title(self):
        return " ".join([self.codename, self.formated_number])

    @property
    def change_location_to(self):
        return [triagepart.distributed for triagepart in self.parts.all()]

    def params(self):
        rst = PartLawsuit.params(self)

        rst.update(
            triage={
                "number": self.formated_number,
                "parts": [
                    {
                        "title": p.matter.path.replace(p.matter.sep, ", "),
                        "locations": [
                            {"name": str(l)} for l in p.locations.order_by("nome")
                        ],
                        "concurrence": [
                            {
                                "name": tc.execution_organ.nome,
                                "incident_type": tc.incident_type,
                                "argumentation": tc.argumentation,
                                "incident": tc.get_incident_display(),
                            }
                            for tc in TriageConcurrence.objects.filter(triage_part=p)
                        ],
                        "distributed": p.distributed,
                        "effected_by": (
                            person_from_user(p.effected_by).nome
                            if person_from_user(p.effected_by)
                            else None
                        ),
                        "effected_at": (
                            DateUtils.datetime_to_str(p.effected_at)
                            if p.effected_at
                            else None
                        ),
                    }
                    for p in self.parts.order_by("matter__title")
                ],
            }
        )

        return rst

    def save(self, *args, **kwargs):
        if not self.triage_number or not self.triage_year:
            self.triage_year = date.today().year
            self.triage_number = self._next_number()

        if self.effected_by and not self.cache_rendered:
            self.cache_rendered = self.rendered

        super(Triage, self).save(*args, **kwargs)


class TriagePart(models.Model):
    triage = models.ForeignKey(Triage, related_name="parts", on_delete=models.PROTECT)
    matter = models.ForeignKey(
        LegalMatter, related_name="triages", on_delete=models.PROTECT
    )
    locations = models.ManyToManyField(
        "rh.Localidade", related_name="as_triage_parts", through="TriagePartLocation"
    )
    distributed = models.ForeignKey(
        ExecutionOrgan,
        related_name="as_distributeds",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    effected_at = models.DateTimeField(null=True, blank=True)
    effected_by = models.ForeignKey(
        "auth.user",
        related_name="effected_parts_of_triage",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    concurrence = models.ManyToManyField(
        ExecutionOrgan, related_name="as_concurrences", through="TriageConcurrence"
    )
    text = models.TextField(blank=True)
    acting_zone = models.ForeignKey(
        "ActingZone",
        related_name="in_triage_part",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    lawsuit = models.ForeignKey(
        OutCourtLawsuit,
        related_name="triageparts",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    def delivery(self):
        if not self.distributed:
            raise Exception("Primeiro deve ser realizado o sorteio.")

        if self.effected_by:
            raise Exception("Este segmentação do procedimento já foi encaminhada.")

        self.effected_by = get_current_user()
        self.effected_at = datetime.now()
        self.save()

        return self.distributed

    def delete(self, *args, **kwargs):
        if self.distributed:
            raise Exception("Não posso modificar uma distribuição concretizada.")

        super(TriagePart, self).delete(*args, **kwargs)

    def validate(self):
        if self.triage.effected_by:
            raise Exception("Não posso modificar uma triagem que já foi efetivada.")

        if not self.acting_zone:
            raise Exception("É necessário informar a área de atuação")

        if self.pk:
            older = TriagePart.objects.get(pk=self.pk)

            if older.matter != self.matter:
                TriagePartLocation.objects.filter(triagepart=self).delete()
                TriageConcurrence.objects.filter(triage_part=self).delete()

    def save(self, *args, **kwargs):
        self.validate()
        super(TriagePart, self).save(*args, **kwargs)

    def _concurrence_slots(self, max_size):
        query = TriageConcurrence.objects.filter(triage_part=self).exclude(
            incident_type=3
        )
        slots = []

        for tc in query:
            factor = 1.0

            if tc.with_matter:
                factor = float(
                    tc.execution_organ.active_matters.get(matter=tc.with_matter).factor
                )

            multi = math.ceil(max_size * float(factor))
            score = tc.execution_organ.get_score_for_matter(tc.with_matter)

            slots += [(tc.execution_organ, tc.with_matter)] * (int(multi) - score)
        return slots

    def _down_score(self, factor):
        query = TriageConcurrence.objects.filter(triage_part=self).exclude(
            incident_type=3
        )

        for tc in query:
            score = (
                tc.execution_organ.get_score_for_matter(tc.with_matter) or 0
            ) - factor
            tc.execution_organ.set_score_for_matter(
                tc.with_matter, score if score > 0 else 0
            )

            log.debug([tc.execution_organ, score, factor])

    def do_concurrence(self):
        log.info("Preparando para realizar o sorteio.")
        query = TriageConcurrence.objects.filter(triage_part=self).exclude(
            incident_type=3
        )

        if self.distributed:
            raise Exception(
                "Esta parte do procedimento já foi distribuida para (%s)."
                % self.distributed
            )

        if query.filter(incident_type=2).exists():
            tc = query.get(incident_type=2)
            log.info(
                "Sem sorteio, existe um incidente de %s para %s",
                tc.get_incident_display(),
                tc.execution_organ.nome,
            )
            self.distributed = tc.execution_organ
            self.save()
            tc.execution_organ.increment_score_for_matter(tc.with_matter)
        elif query.count() == 1:
            log.info("Sem sorteio, envio direto.")
            self.distributed = query.get().execution_organ
            self.save()
        elif query.count() > 1:
            log.info("Deve ser realizado o sorteio.")
            max_size = 0.0
            factor = 0.0
            for tc in query:
                factor = 1.0
                if tc.with_matter:
                    factor = float(
                        tc.execution_organ.active_matters.get(
                            matter=tc.with_matter
                        ).factor
                    )
                size = math.ceil(1.0 / factor)
                max_size = size if size > max_size else max_size

            slots = []
            count = 0
            while not slots:
                slots = self._concurrence_slots(max_size)

                if not slots:
                    factor = int(math.ceil(factor or 0))
                    self._down_score(factor)

                count += 1
                if count > 5:
                    raise Exception("Problema de indefinição no sorteio.")

            random.seed(os.urandom(4096))

            for e, m in slots:
                log.debug(e)

            selected, selected_matter = slots[random.randrange(len(slots))]
            selected.increment_score_for_matter(selected_matter)
            self.distributed = selected
            self.save()
        else:
            raise Exception("Ainda não foi feita a preparação para o concurso.")

    def sectional_for_county(self, county):
        return TriagePartLocation.objects.filter(
            triagepart=self, location__counties=county
        ).exclude(sectional=None)

    def _concurrence_in_county_from_matter(self, county, matter=None):
        matter = matter if matter else self.matter
        log.info(
            "Buscando concorrencia especifica para o assunto %s na comarca %s",
            matter,
            county.title,
        )

        sectional = None

        if self.sectional_for_county(county).exists():
            sectional = self.sectional_for_county(county).first().sectional
            log.info("Reginal especificada %s para comarca %s.", sectional, county)

        query = ExecutionOrgan.objects.filter(
            localidade__in=county.locations.filter(),
            in_distribution_tables__matter=matter,
            in_distribution_tables__factor__gt=0,
            ativo=True,
        )

        query = (
            query
            if not sectional
            else query.filter(in_distribution_tables__sectional=sectional)
        )

        query = query.filter(
            models.Q(
                models.Q(
                    in_distribution_tables__document__data_vigencia__lte=date.today()
                )
                & models.Q(in_distribution_tables__end_document__isnull=True)
            )
            | models.Q(
                models.Q(
                    in_distribution_tables__document__data_vigencia__lte=date.today()
                )
                & models.Q(
                    in_distribution_tables__end_document__data_vigencia__gt=date.today()
                )
            )
        )

        if query.exists():
            return [(e, matter) for e in query]
        elif matter.father:
            log.info("Não foi encontrada promotoria especifica para este assunto.")
            log.info("Mas o assunto é filho de %s", matter.father.title)
            return self._concurrence_in_county_from_matter(
                county, matter.father.legalmatter
            )
        else:
            log.warning(
                "Não foram encontradas promotórias especificas para está raiz de assunto."
            )
            return []

    def concurrence_in_county(self, county):
        log.info(
            "Buscando concorrencia para o assunto %s na comarca %s",
            self.matter.title,
            county.title,
        )

        rst = None

        log.info("Buscando promotorias especificas...")
        rst = self._concurrence_in_county_from_matter(county)

        if not rst:
            log.info("Buscando promotorias gerais...")
            rst = [
                (e, None)
                for e in ExecutionOrgan.objects.filter(
                    localidade__in=county.locations.filter(),
                    general_distribution=True,
                    ativo=True,
                )
            ]
        else:
            log.info("Foram encontradas %d promotorias especificas", len(rst))

        for e, m in rst:
            obj, created = TriageConcurrence.objects.get_or_create(
                triage_part=self, execution_organ=e, with_matter=m, direct=False
            )

            if created:
                obj.save()


class TriagePartLocation(models.Model):
    triagepart = models.ForeignKey(
        TriagePart, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    location = models.ForeignKey(Localidade, related_name="+", on_delete=models.PROTECT)
    sectional = models.ForeignKey(
        Sectional,
        related_name="in_triage_part_locations",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (("triagepart", "location"),)

    def validate(self):
        if self.sectional:
            self.validate_sectional()

    def validate_sectional(self):
        county = self.location.counties.get()

        def genealogic(matter):
            rst = []

            while matter:
                log.debug(matter)
                rst.append(matter)
                matter = matter.father

            return rst

        query = ExecutionOrgan.objects.filter(
            localidade__in=county.locations.filter(),
            in_distribution_tables__matter__in=genealogic(self.triagepart.matter),
            in_distribution_tables__factor__gt=0,
            in_distribution_tables__sectional=self.sectional,
        ).filter(
            models.Q(
                models.Q(
                    in_distribution_tables__document__data_vigencia__lte=date.today()
                )
                & models.Q(in_distribution_tables__end_document__isnull=True)
            )
            | models.Q(
                models.Q(
                    in_distribution_tables__document__data_vigencia__lte=date.today()
                )
                & models.Q(
                    in_distribution_tables__end_document__data_vigencia__gt=date.today()
                )
            )
        )

        if not query.exists():
            raise Exception(
                "Nenhum órgão de execução foi encontrado para esta configuração."
            )

    def save(self, *args, **kwargs):
        self.validate()
        super(TriagePartLocation, self).save(*args, **kwargs)


class TriageConcurrence(models.Model):
    triage_part = models.ForeignKey(
        TriagePart, related_name="as_triage_concurrences", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    execution_organ = models.ForeignKey(
        ExecutionOrgan, related_name="as_triage_concurrences", on_delete=models.PROTECT
    )
    with_matter = models.ForeignKey(
        LegalMatter,
        related_name="as_with_matter",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    direct = models.BooleanField(default=True)
    incident_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "INCIDENT_TYPE"),
        default=1,
        blank=True,
    )
    incident = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "INCIDENT"), null=True, blank=True
    )
    argumentation = models.TextField(null=True)

    reason_for_suspension = models.SmallIntegerField(
        choices=((0, "Nenhum"), (1, "Ativo"), (2, "Motivo 2"), (3, "Motivo 3")),
        default=None,
        null=True,
        blank=True,
    )

    def delete(self, *args, **kwargs):
        if self.triage_part.distributed:
            raise Exception("Não posso modificar uma distribuição concretizada.")
        if not self.direct:
            raise Exception(
                "Não posso excluir um órgão de execução que foi colocado no concurso de forma indireta."
            )

        super(TriageConcurrence, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.incident = int(self.incident or 0)

        if self.triage_part.distributed:
            raise Exception(
                "Não posso modifica a concorrência desta triagem, pois, já foi distribuido."
            )

        if self.incident > 100 and self.incident < 200:
            self.incident_type = 2
        elif self.incident > 200 and self.incident < 300:
            self.incident_type = 3
        else:
            self.incident_type = 0

        if self.direct and self.incident_type != 2:
            raise Exception("Só podemos inserir concorrêntes com PREVENÇÃO ou CONEXÃO.")

        if self.incident_type == 2:
            query = TriageConcurrence.objects.filter(
                triage_part=self.triage_part, incident_type=self.incident_type
            )

            query = query.exclude(pk=self.pk) if self.pk else query

            if query.exists():
                shock = query.get()

                raise Exception(
                    'Não posso criar o incidente de "%s", pois já temos um incidente "%s" destinado para "%s"'
                    % (
                        self.get_incident_display(),
                        shock.get_incident_display(),
                        shock.execution_organ.nome,
                    )
                )

        super(TriageConcurrence, self).save(*args, **kwargs)


class LegalGround(models.Model):
    title = models.CharField(max_length=300)
    text = models.TextField(blank=True)

    def __str__(self):
        return self.title


@type_part_lawsuit()
class Ordinace(PartLawsuit):
    number = models.SmallIntegerField(blank=True)
    type_ordinace = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_ORDINACE")
    )
    year = models.SmallIntegerField(blank=True)
    legalgrounds = models.ManyToManyField(LegalGround, related_name="in_ordinaces")
    cache_formated_number = models.CharField(max_length=100, null=True, blank=True)
    object_of_proccess = models.TextField(null=True)
    consideration = models.TextField(null=True, blank=True)
    only_responsible_sign = True

    @property
    def deadline_days(self):
        return self.deadline_days_for_type(self.type_ordinace)

    @classmethod
    def deadline_days_for_type(klass, type_ordinace):
        cfg = Configuration.objects.get(application="ejud")
        type_ordinace = int(type_ordinace or 0)

        type_map = {
            2: "deadlineCivilInvestigation",
            3: "deadlinePreparatoryProcedure",
            4: "deadlinePreparatoryCivilInvestigation",
            7: "deadlineAdministrativeProcedure",
            8: "deadlineRogatoryLetter",
            9: "deadlinePreparatoryProcedureElectoral",
            10: "deadlineAdministrativeManagement",
        }

        return int(cfg.get(type_map.get(type_ordinace, "unknow"), 0))

    def create_supplement(self):
        if not self.read_only:
            raise Exception(
                "Não é necessário criar um suplemento para um portaria que ainda não foi assinada."
            )
        elif self.supplementations.filter(signed_by=None).exists():
            raise Exception("Já existe uma suplementação de portária em aberto.")
        else:
            inst = SupplementOrdinace(ordinace=self, lawsuit=self.lawsuit)
            inst.save()
            return inst

    def sign_part(self):
        with transaction.atomic():
            if not self.diligences.exists():
                raise Exception("Não foi adicionada nenhuma diligencia a portaria.")

            if (
                int(self.type_ordinace or 0) in (2,)
                and not self.lawsuit.blokes.exists()
            ):
                raise Exception("%s deve ter pelo menos um investigado." % self.title)

            self.page_number = 1
            super(Ordinace, self).sign_part()
            for diligence in self.diligences.filter():
                diligence.change_state_diligence(
                    diligence.delivery_status, "aguardando-distribuicao"
                )
                diligence.without_attached_documents = True
                diligence.with_manifestation = True
                diligence.save()
            self.lawsuit.type_lawsuit = self.type_ordinace
            # self.lawsuit.deadline_cache = date.today() + timedelta(days=self.deadline_days)
            self.lawsuit.remaining_days = self.deadline_days
            self.lawsuit.save()

    def delete(self, *args, **kwags):
        with transaction.atomic():
            self.in_rejection_fact.filter().update(ordinace=None)
            super(Ordinace, self).delete(*args, **kwags)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.number = self._next_number()
            self.year = datetime.now().year

        self.cache_formated_number = self.formated_number
        super(Ordinace, self).save(*args, **kwargs)

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(
            doc=self,
            execution_organ=execution_organ,
            ordinace={
                "number": self.formated_number,
                "execution_organ": execution_organ,
                "document_number": self.lawsuit.origin.codigo,
                "type": self.get_type_ordinace_display(),
                "object_of_proccess": self.object_of_proccess,
                "legalgrounds": self.legalgrounds.filter(),
                "modified_at": self.modified_at,
                "diligences": self.diligences.filter(),
                "blokes": [
                    capitalize_words(bloke.my_bloke.nome)
                    for bloke in self.lawsuit.blokes.filter()
                ],
                "section": 3
                + (
                    (1 if self.lawsuit.blokes.exists() else 0)
                    + (1 if self.legalgrounds.exists() else 0)
                ),
            },
        )

        return rst

    def _next_number(self):
        Model = self.__class__

        max_number = (
            Model.objects.filter(
                year=date.today().year, type_ordinace=self.type_ordinace
            )
            .aggregate(max_number=models.Max("number"))
            .get("max_number", 0)
        )

        return int(max_number or 0) + 1

    @property
    def formated_number(self):
        kind = {2: "ICP", 3: "PP", 4: "PIC", 7: "PAD"}

        return "%s/%04d/%d" % (
            kind.get(int(self.type_ordinace or 0), ""),
            int(self.number or 0),
            int(self.year or 0),
        )

    codename = "Portaria de Instauração (Deprecated)"

    @property
    def title(self):
        return " ".join([self.codename, self.formated_number])

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-investigation"


@type_part_lawsuit()
class SupplementOrdinace(PartLawsuit):
    supplemented_ordinace = models.ForeignKey(
        Ordinace, related_name="supplementations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    justification = models.TextField()

    codename = "Suplementação de Portária de Instauração"
    only_responsible_sign = True

    def sign_part(self):
        with transaction.atomic():
            super(SupplementOrdinace, self).sign_part()
            for diligence in self.diligences.filter():
                diligence.change_state_diligence(
                    diligence.delivery_status, "aguardando-distribuicao"
                )
                diligence.without_attached_documents = True
                diligence.with_manifestation = True
                diligence.save()

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-suplement-ordinace"

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(execution_organ=execution_organ, doc=self)

        return rst


@type_part_lawsuit()
class Denunciation(InitialPartlawsuit, PartLawsuit):
    protocol = models.ForeignKey(
        "protocolo.protocolo", related_name="has_deunciation", on_delete=models.PROTECT
    )
    movement_cache_rendered = models.TextField(blank=True, null=True)

    codename = "Protocolo de Noticia de Fato"

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-denunciation"

    def _lawsuit_type(self):
        return getattr(self, "force_type_lawsuit", 1)

    @property
    def lawsuit_title(self):
        return self.protocol.assunto

    def _calculate_deadline_date(self):
        cfg = Configuration.get_or_create("ejud")
        triage_workplace = json.loads(cfg.get("triageCenter", "[]"))

        main_triage_center = int(cfg.get("mainTriageCenter", 0)) or None

        if not main_triage_center:
            raise Exception(
                "Não foi definido um centro de triagem principal. Favor ajustar definições no configurador do eJud."
            )

        triage_workplace.append(main_triage_center)

        deadline = 0

        type_lawsuit = int(self.lawsuit.type_lawsuit or 0)
        if self.lawsuit.location.pk in triage_workplace:
            deadline = int(cfg.get("deadlineTriage", 0) or 0)
        else:
            type_map = {
                1: "deadlineFactNews",
                2: "deadlineCivilInvestigation",
                3: "deadlinePreparatoryProcedure",
                4: "deadlinePreparatoryCivilInvestigation",
                7: "deadlineAdministrativeProcedure",
                8: "deadlineRogatoryLetter",
                9: "deadlinePreparatoryProcedureElectoral",
                10: "deadlineAdministrativeManagement",
            }

            kind = type_map.get(type_lawsuit)
            deadline = int(cfg.get(kind) or 0) if kind else None

        return deadline

    @property
    def movement_render(self):
        data = [
            loader.get_template("judicial/movement_protocol.html").render(
                {
                    "protocol": self.protocol,
                }
            )
        ]
        return "".join(data)

    @property
    def extra_pages_protocol(self):
        pages = []

        if self.can_read and self.movement_cache_rendered:
            pages.append({"at": self.signed_at, "page": self.movement_cache_rendered})
        return pages

    def _all_extra_pages_complete(self):
        return (
            super(Denunciation, self)._all_extra_pages_complete()
            + self.extra_pages_protocol
        )

    def _sign(self):
        signed = False
        if self.pk is None:
            self._sign_lawsuit_prepare()
            self.signed_by = self.signed_by if self.signed_by else get_current_user()
            self.signed_at = self.signed_at if self.signed_at else datetime.now()
            signed = True
        return signed

    def _after_save(self, signed):
        if signed:
            EventControl.objects.create(
                lawsuit=self.lawsuit,
                part=self,
                number_control=self.lawsuit.next_number_control(),
            )
            OutCourtLawsuitLog.register(self.lawsuit, self)

        for attachment in self.lawsuit.origin.attachments.filter():
            obj = Attached(
                attached_document=self,
                title=attachment.title[:100],
                file_descriptor=attachment.attach,
            )
            obj.skip_read_only_validate = True
            obj.save()

        self.__class__.objects.filter(pk=self.pk).update(cache_rendered=self.rendered)
        movement = self.lawsuit.current_moviment()
        movement.with_workflow = True
        movement.save()

    def _create_grant_confidential_access(self):
        grant = GrantConfidentialAccess()
        grant.apply_in = 2
        grant.location = self.create_location
        grant.lawsuit = self.lawsuit
        grant.save()
        grant.add_part(self)
        grant.by_confidential_protocol = True
        grant.sign_part()

    @property
    def is_protocol_secret(self):
        try:
            return self.protocol.protocol_control.is_secret
        except Exception as e:
            log.debug(e)
            return False

    def save(self, *args, **kwargs):
        with transaction.atomic():
            signed_now = self._sign()

            self.cache_rendered = None
            self.movement_cache_rendered = self.movement_render
            super(Denunciation, self).save(*args, **kwargs)

            self._after_save(signed_now)

            if self.is_protocol_secret:
                self._create_grant_confidential_access()

    def params(self):
        rst = PartLawsuit.params(self)

        rst.update(protocol=self.protocol)

        return rst


class OfficerDiligence(AuditTimestampModel):
    score = models.SmallIntegerField(default=0, blank=True)
    officer_diligence = models.OneToOneField(Servidor, on_delete=models.CASCADE)
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("common", "ACTIVE_CHOICES"), default=1, null=True
    )
    is_removed = models.BooleanField(default=False)

    class Meta:
        permissions = (("office_geral", "Gestor geral de diligencias"),)
        ordering = ("officer_diligence__pessoa_fisica__nome",)

    def accept_diligence(self, diligence):
        if int(self.status or 0) != 1:
            raise Exception(
                "%s não esta ativo devido a motivos de afastamento."
                % self.officer_diligence.pessoa_fisica
            )

        if (
            self == diligence.responsible_delivering
            and diligence.is_delivery_status_awaiting_officer
        ):
            diligence.ignore_validate_changes = True
            if diligence.judicialdiligence.is_who_type_internal:
                diligence.change_state_diligence(
                    diligence.delivery_status, "aguardando-resposta"
                )
                delivery_attempt = DeliveryAttempt(
                    diligence=diligence,
                    observation="A diligência %s foi recebida por %s para cumprimento."
                    % (
                        diligence.formated_number,
                        self.officer_diligence.pessoa_fisica.nome,
                    ),
                    exit_date=datetime.now(),
                    return_date=datetime.now(),
                    delivery_date=datetime.now(),
                    attempt=1,
                    delivered=1,
                    type_vehicle=1,
                )
                delivery_attempt.ignore_validate_changes = True
                delivery_attempt.save()
                delivery_attempt.sign()
                diligence.judicialdiligence.has_manifestations.update(
                    remaining_days=diligence.judicialdiligence.deadline
                )
            else:
                diligence.change_state_diligence(
                    diligence.delivery_status, "entrega-andamento"
                )

            diligence.date_receipt_diligence = datetime.now()
            diligence.save()
        elif (
            self == diligence.responsible_delivering
            and not diligence.is_delivery_status_awaiting_officer
        ):
            raise Exception(
                "Esta diligencia não esta mais na condição de aguardando o aceite."
            )
        else:
            raise Exception(
                "Não posso aceiter esta diligência ela foi atribuida à %s"
                % diligence.responsible_delivering
            )

    @classmethod
    def officies_working_in_county(klass, county):
        # Retirada união de declarações de atividade com exercícios por terem sido migradas as declarações
        # para movimentacao específica, que tem o exercício no mesmo modelo que os demais outros servidores
        employees = (
            ServidorLotacao.work_assignment_exercise()
            .filter(lotacao__localidade__in=county.locations.all())
            .values("servidor")
        )

        return klass.objects.filter(officer_diligence__in=employees)

    @classmethod
    def officies_working_in_counties(klass, counties):
        q_pool = [
            models.Q(lotacao__localidade__in=county.locations.all())
            for county in counties
        ]

        query = None

        for q in q_pool:
            query = q if not query else q | query

        # Retirada união de declarações de atividade com exercícios por terem sido migradas as declarações
        # para movimentacao específica, que tem o exercício no mesmo modelo que os demais outros servidores
        employees = (
            ServidorLotacao.work_assignment_exercise().filter(query).values("servidor")
        )

        return klass.objects.filter(officer_diligence__in=employees)

    def __str__(self):
        return "%s" % self.officer_diligence.pessoa_fisica.nome

    @property
    def work_county(self):
        work_county = None

        if len(self.officer_diligence.work_locations) > 0:
            try:
                work_county = County.objects.get(
                    locations=self.officer_diligence.work_locations[0].localidade
                )
            except County.DoesNotExist:
                work_county = None

        return work_county

    @property
    def waiting_diligences(self):
        return self.diligence_set.filter(
            judicialdiligence__delivery_status__in=[2, 3, 4]
        )

    @property
    def icons_status(self):
        ICONS = {
            1: {
                "iconCls": "icon-judicial icon-ejud-outlawcortsuit-not-have-time",
                "title": "Ocupado",
            },
            2: {"iconCls": "icon-judicial icon-ejud-unsigned", "title": "Disponível"},
        }

        return [ICONS.get(1 if self.waiting_diligences.exists() else 2)]


class Diligence(AuditTimestampModel):
    """
    Modelo base diligencia
    """

    diligence_year = models.SmallIntegerField(null=True, blank=True)
    diligence_number = models.BigIntegerField(null=True, blank=True)
    formated_number = models.CharField(
        max_length=10, null=True, blank=True, db_index=True
    )
    responsible_delivering = models.ForeignKey(
        OfficerDiligence,
        null=True,
        blank=True,
        verbose_name="responsavel pela entrega",
        on_delete=models.PROTECT,
    )
    title = models.CharField(
        max_length=100, verbose_name="Título", null=True, blank=True
    )
    text = models.TextField(blank=True)
    date_receipt_diligence = models.DateTimeField(
        null=True, blank=True, verbose_name="data de recebimento da diligencia"
    )
    date_delivery = models.DateTimeField(
        null=True, blank=True, verbose_name="data da entrega da diligencia"
    )
    delivery_status = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "DELIVERY_STATUS"),
        default=1,
        null=True,
        blank=True,
        verbose_name="status da entrega",
    )
    priority = models.SmallIntegerField(
        choices=(
            (1, "Normal"),
            (2, "Urgente"),
        ),
        default=1,
        null=True,
        blank=True,
    )
    observation = models.TextField()
    prevent_delivery_in_executionorgan = models.BooleanField(default=False)
    assumed_delivery_by = models.ForeignKey(
        "auth.User",
        related_name="diligences_assumed",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    assumed_delivery_at = models.DateTimeField(null=True, blank=True)
    county = models.ForeignKey(
        County,
        related_name="diligences",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    is_copy_of = models.ForeignKey(
        "self",
        related_name="is_copy_by",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    STATES = {
        "redigindo-diligencia": {
            "id": 1,
            "name": "Redigindo Diligência",
            "allowed": ["aguardando-distribuicao", "entrega-orgao"],
        },
        "aguardando-distribuicao": {
            "id": 2,
            "name": "Aguardando Distribuição",
            "allowed": ["aguardando-oficial", "entrega-orgao", "devolvido"],
        },
        "aguardando-oficial": {
            "id": 3,
            "name": "Aguardando Confirmação do Oficial",
            "allowed": [
                "aguardando-distribuicao",
                "entrega-andamento",
                "aguardando-resposta",
            ],
        },
        "entrega-andamento": {
            "id": 4,
            "name": "Entrega em Andamento",
            "allowed": ["entrega-concluida", "devolvido", "aguardando-resposta"],
        },
        "entrega-concluida": {
            "id": 5,
            "name": "Entrega Concluida",
            "allowed": ["aguardando-resposta"],
        },
        "publicacao-diario": {
            "id": 6,
            "name": "Publicação em Diário Oficial",
            "allowed": [],
        },
        "entrega-orgao": {
            "id": 7,
            "name": "Entrega pelo Orgão de Execução",
            "allowed": [
                "entrega-concluida",
                "devolvido",
                "aguardando-resposta",
                "finalizado",
            ],
        },
        "devolvido": {
            "id": 8,
            "name": "Devolvido",
            "allowed": ["copiado", "finalizado"],
        },
        "aguardando-resposta": {
            "id": 9,
            "name": "Aguardando Resposta",
            "allowed": ["entrega-concluida", "atrasado", "finalizado"],
        },
        "atrasado": {
            "id": 10,
            "name": "Aguardando Resposta",
            "allowed": ["finalizado"],
        },
        "copiado": {
            "id": 11,
            "name": "Suplementação",
            "allowed": ["redigindo-diligencia"],
        },
        "finalizado": {"id": 99, "name": "Finalizado", "allowed": []},
    }

    @property
    def is_delivery_status_edit(self):
        return int(self.delivery_status or 0) == 1

    @property
    def is_delivery_status_awaiting_distribution(self):
        return int(self.delivery_status or 0) == 2

    @property
    def is_delivery_status_awaiting_officer(self):
        return int(self.delivery_status or 0) == 3

    @property
    def is_delivery_status_delivery_progress(self):
        return int(self.delivery_status or 0) in (4, 7)

    @property
    def is_delivery_status_delivery_completed(self):
        return int(self.delivery_status or 0) == 5

    @property
    def is_delivery_status_organ_delivery(self):
        return int(self.delivery_status or 0) == 7

    @property
    def is_delivery_status_returned(self):
        return int(self.delivery_status or 0) == 8

    @property
    def is_delivery_status_awaiting_answer(self):
        return int(self.delivery_status or 0) == 9

    @property
    def is_delivery_status_late(self):
        return int(self.delivery_status or 0) == 10

    @property
    def is_delivery_status_supplemented(self):
        return int(self.delivery_status or 0) == 11

    @property
    def is_delivery_status_completed(self):
        return int(self.delivery_status or 0) == 99

    def _get_slug_state_from_id(self, id):
        for key, value in list(self.STATES.items()):
            if id == value["id"]:
                return key
        return ""

    def change_state_diligence(self, identifier, slug_state_destiny):
        slug_state_from = self._get_slug_state_from_id(identifier)
        if (
            slug_state_destiny in self.STATES[slug_state_from]["allowed"]
            or slug_state_from == slug_state_destiny
        ):
            self.delivery_status = self.STATES.get(slug_state_destiny)["id"]
        else:
            raise Exception(
                'Mudança de estado da Diligência de "%s" para "%s" não é permitida.'
                % (
                    self.STATES.get(slug_state_from)["name"],
                    self.STATES.get(slug_state_destiny)["name"],
                )
            )

    def __str__(self):
        return " - ".join([self.formated_number, self.title])

    ICONS = {
        1: {"iconCls": "icon-judicial icon-ejud-edition-mode", "title": "Editando"},
        2: {
            "iconCls": "icon-core icon-core-waiting",
            "title": "Aguardando distribuição aos oficiais",
        },
        3: {
            "iconCls": "icon-judicial icon-ejud-clean-definition",
            "title": "Aguardando confirmação de distribuição pelo oficial",
        },
        4: {"iconCls": "icon-fopag icon-fopag-truck", "title": "Entrega em andamento"},
        5: {"iconCls": "icon-core icon-core-success", "title": "Diligência Concluída"},
        6: {
            "iconCls": "icon-judicial icon-ejud-prepare-concurrence",
            "title": "Solicitado Publicação em Diário Oficial",
        },
        7: {
            "iconCls": "icon-judicial icon-ejud-executation-organ",
            "title": "Entrega sendo realizada no Órgão de Execução",
        },
        8: {
            "iconCls": "icon-judicial icon-ejud-executation-organ",
            "title": "Devolvido ao Remetente",
        },
    }

    @property
    def permalinks(self):
        return [
            attach.file_descriptor.complete_permalink()
            for attach in self.attaches.filter()
        ]

    @property
    def read_only(self):
        return int(self.delivery_status or 0) != 1

    @property
    def is_urgent(self):
        if int(self.priority) == 2:
            return {
                "iconCls": "icon-judicial icon-ejud-outlawcortsuit-not-have-time",
                "title": "Urgente",
            }

    @property
    def icons(self):
        icon = []
        icon.append(self.is_urgent)
        icon.append(self.ICONS.get(self.delivery_status))

        return icon

    def _next_number(self, year=None):
        Model = self.__class__

        year = year if year else date.today().year

        max_number = (
            Model.objects.filter(diligence_year=year)
            .aggregate(max_number=models.Max("diligence_number"))
            .get("max_number", 0)
        )

        return year, int(max_number or 0) + 1

    def _associate_officer_diligence_with_diligence(self, officer_diligence):
        officer_diligence.score += 1
        officer_diligence.save()

        self.responsible_delivering = officer_diligence
        self.change_state_diligence(self.delivery_status, "aguardando-oficial")
        self.ignore_validate_changes = True
        self.save()

    def send_to_officer_diligence(self, officer_diligence):
        if int(officer_diligence.status or 0) != 1:
            raise Exception(
                "Não posso passar uma diligência para um oficial que não esteja ativo."
            )

        if self.delivery_status not in (2, 3):
            raise Exception(
                'Não posso passar para o oficial uma diligência que esta como "%s".'
                % self.get_delivery_status_display()
            )

        if officer_diligence not in OfficerDiligence.officies_working_in_county(
            county=self.county
        ):
            raise Exception(
                "Não posso designar o oficial, pois ele não encontra-se na comarca onde a diligência deve ser cumprida."
            )

        self._associate_officer_diligence_with_diligence(officer_diligence)

    def remove_from_officer_diligence(self):
        if not self.is_delivery_status_awaiting_officer:
            raise Exception(
                'Não retirar do oficial uma diligência que esta como "%s".'
                % self.get_delivery_status_display()
            )

        self.responsible_delivering.score -= 1
        self.responsible_delivering.save()

        self.responsible_delivering = None
        self.change_state_diligence(self.delivery_status, "aguardando-distribuicao")
        self.ignore_validate_changes = True
        self.save()

    def validate_changes(self):
        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)

            if int(self.delivery_status or 0) > 1 and not self.county:
                raise Exception(
                    "Para diligência %s é necessário indicar a comarca onde será entregue."
                    % self.formated_number
                )

            if older.delivery_status > 1 and not getattr(
                self, "ignore_validate_changes", False
            ):
                raise Exception(
                    "Não posso modificar uma diligencia que não esta mais em edição."
                )

            if (
                self.is_delivery_status_delivery_progress
                and self.responsible_delivering
            ):
                self.date_receipt_diligence = datetime.now()

            if (
                self.date_delivery
                and self.responsible_delivering
                and self.is_delivery_status_delivery_progress
            ):
                log.info("aguardando resposta")
                self.change_state_diligence(self.delivery_status, "aguardando-resposta")

            if self.is_delivery_status_awaiting_officer and self.responsible_delivering:
                Notification.notify(
                    "ejud-notify-official",
                    self.responsible_delivering.officer_diligence,
                    types=("SYS",),
                    **{},
                )

    @property
    def number_pages(self):
        qt = 0
        for at in self.attaches.filter():
            qt += at.number_pages if at.number_pages else 0
        return qt

    def delete(self, *args, **kwags):
        if self.is_copy_of:
            Diligence.objects.filter(pk=self.is_copy_of.pk).update(delivery_status=8)

        super(Diligence, self).delete(*args, **kwags)

    def finish_diligence(self):
        """Finalizar diligência

        Finaliza uma diligência que esteja aguardando resposta, atrasada ou devolvida
        """

        self.change_state_diligence(self.delivery_status, "finalizado")
        self.ignore_validate_changes = True
        self.save()

    def save(self, *args, **kwargs):
        if not self.diligence_year or not self.diligence_number:
            self.diligence_year, self.diligence_number = self._next_number()
            self.formated_number = None

        if not self.formated_number:
            self.formated_number = "%05d/%d" % (
                self.diligence_number,
                self.diligence_year,
            )

        self.validate_changes()
        super(Diligence, self).save(*args, **kwargs)


class AdministrativeDiligence(Diligence):
    pass


class JudicialDiligence(Diligence):
    """
    Modelo Diligencias judiciais
    """

    deadline = models.SmallIntegerField(null=True, blank=True)
    who = models.ForeignKey(
        "rh.Pessoa",
        related_name="with_judicial_diligences",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    who_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "WHO_TYPE"), blank=True
    )
    part = models.ForeignKey(
        PartLawsuit, related_name="diligences", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    diligence_file = models.ForeignKey(
        Arquivo, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    publication = models.ForeignKey(
        "rh.Publicacao",
        related_name="diligences_publications",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    signed_by = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signed_at = models.DateTimeField(null=True, blank=True)
    execution_organ = models.ForeignKey(
        "rh.Lotacao",
        related_name="diligences",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    count_type = models.SmallIntegerField(
        verbose_name="Contagem",
        choices=(
            (1, "DIAS CORRIDOS"),
            (2, "DIAS UTEIS"),
        ),
    )

    class Meta:
        ordering = (
            "diligence_year",
            "diligence_number",
            "-delivery_status",
        )
        permissions = (
            ("admin_dilig", "Visão Administrador"),
            ("manager_dilig", "Visão Central de Diligências"),
            ("oficial_dilig", "Visão Oficial de Diligencias"),
            ("promotor_dilig", "Visão Promotor"),
        )

    def do_copy(self):
        """Copiar diligência
        Cria um novo lote com uma diligência baseada na que originou a cópia.
        """

        if self.delivery_status not in (8,):
            raise Exception("Só posso copiar uma diligencia que tenha sido devolvida")

        part = self.part.my_origin.__class__(lawsuit=self.part.lawsuit)
        part.save()

        copy_values = (
            "text",
            "deadline",
            "country",
            "county",
            "prevent_delivery_in_executionorgan",
            "title",
            "count_type",
            "who",
            "who_type",
            "observation",
        )

        diligence = self.__class__()
        diligence.part = part

        for field in copy_values:
            setattr(diligence, field, getattr(self, field, None))

        diligence.is_copy_of_id = self.pk
        diligence.save()

        self.change_state_diligence(self.delivery_status, "copiado")
        self.ignore_validate_changes = True
        self.save()

        for attach in self.attaches.all():
            attach.pk = None
            attach.attached_diligence = diligence
            attach.save()

    @property
    def extra_pages(self):

        if self.part.can_read:
            pages = []
            for attaches in self.attaches.filter():
                pages += [
                    {
                        "page": page.get("page"),
                        "at": self.signed_at if self.signed_at else datetime.now(),
                    }
                    for page in attaches.extract_pages()
                ]

            for attached_doc in self.as_diligence_answer.all():
                pages.append(
                    {
                        "at": self.signed_at if self.signed_at else datetime.now(),
                        "page": attached_doc.rendered,
                    }
                )

            for ro in self.has_responses.all():
                for attached in ro.attaches.all():
                    pages += [
                        {
                            "page": page.get("page"),
                            "at": self.signed_at if self.signed_at else datetime.now(),
                        }
                        for page in attached.extract_pages()
                    ]

            return [
                page.get("page")
                for page in sorted(pages, key=lambda d: d.get("at") or datetime.now())
            ]
        else:
            return []

    def _get_organ_signer(self):
        organ = None
        if self.is_delivery_status_organ_delivery:
            organ = self.part.lawsuit.location
        else:
            if self.signed_by.servidor.work_assignment_effective_exercise.filter(
                main=True
            ):
                organ = (
                    self.signed_by.servidor.work_assignment_effective_exercise.filter(
                        main=True
                    )
                    .first()
                    .lotacao
                )
            elif self.signed_by.servidor.workplace_only.filter(ativo=True):
                organ = (
                    self.signed_by.servidor.workplace_only.filter(ativo=True)
                    .first()
                    .lotacao
                )

        return organ

    @property
    def rendered(self):
        data = [
            loader.get_template("judicial/lawsuit/diligence.html").render(
                {
                    "doc": self,
                    "sign": {
                        "moment_at": self.signed_at,
                        "person": (
                            self.signed_by.servidor.pessoa_fisica
                            if self.signed_by
                            else None
                        ),
                        "organ": self._get_organ_signer() if self.signed_by else None,
                    },
                }
            )
        ]

        data += [sign.rendered for sign in self.legal_signs.filter()]

        if self.legal_signs.filter().exists():
            data.append(
                loader.get_template("judicial/legal_sign_fundament.html").render({})
            )

        return "".join(data)

    def assume_delivery(self, user=None):
        user = user if user else get_current_user()

        if self.delivery_status not in (1, 2, 3):
            raise Exception(
                'Não posso assumir a entrega de uma diligencia que esta "%s".'
                % self.get_delivery_status_display()
            )

        if not self.part.signed:
            raise Exception("O Documento não encontra-se assinado.")

        self.ignore_validate_changes = True
        self.assumed_delivery_by = user
        self.assumed_delivery_at = datetime.now()
        self.change_state_diligence(self.delivery_status, "entrega-orgao")
        self.save()

    @property
    def icons(self):
        ic = super(JudicialDiligence, self).icons

        ic.append(self.receipt_diligence)
        ic.append(self.finish_deadline)
        ic.append(self.manifestation_deadline)

        return ic

    @property
    def receipt_diligence(self):
        if self.responsible_delivering and self.date_receipt_diligence:
            return {
                "iconCls": "icon-fopag icon-fopag-stamp-arrow",
                "title": "Diligência recebida pelo Oficial em: %s"
                % DateUtils.date_to_str(self.date_receipt_diligence),
            }
        else:
            return {"iconCls": "icon-judicial icon-ejud-unsigned", "title": ""}

    @property
    def finish_deadline(self):
        if (
            self.date_delivery
            and self.deadline
            and not self.has_manifestations.filter(signed_at__isnull=False).exists()
        ):
            manifestation = self.has_manifestations.filter(
                signed_at__isnull=True
            ).first()
            days_date_finish = (
                manifestation.remaining_days
                if manifestation and manifestation.remaining_days
                else 0
            )

            return {
                "iconCls": (
                    "icon-core icon-core-info"
                    if days_date_finish > 0
                    else "icon-core icon-core-error"
                ),
                "title": (
                    "Dias restantes para a Manifestação: %s" % days_date_finish
                    if days_date_finish > 0
                    else "Manifestação atrasada."
                ),
            }
        else:
            return {"iconCls": "icon-judicial icon-ejud-unsigned", "title": ""}

    @property
    def manifestation_deadline(self):
        if (
            self.deadline
            and self.has_manifestations.filter(signed_at__isnull=False).exists()
        ):
            return {
                "iconCls": "icon-fopag icon-fopag-blueprint-pencil",
                "title": "Manifestação realizada",
            }

    def send_to_random_officer_diligence(self):
        if self.delivery_status not in (2, 3):
            raise Exception(
                'Não posso passar para o oficial uma diligência que esta como "%s".'
                % self.get_delivery_status_display()
            )

        officies_pkset = [
            office.pk
            for office in OfficerDiligence.officies_working_in_county(self.county)
            if office.status == 1
        ]

        if not officies_pkset:
            raise Exception("Nenhum oficial de diligência para distribuição")
        else:
            if self.is_delivery_status_awaiting_officer:
                self.change_state_diligence(
                    self.delivery_status, "aguardando-distribuicao"
                )
                self.responsible_delivering.score -= 1
                self.responsible_delivering.save()

            officies = OfficerDiligence.objects.filter(pk__in=officies_pkset)
            score_min = int(
                officies.aggregate(models.Min("score")).get("score__min") or 0
            )

            random.seed(time.time())
            officer = random.choice(officies.filter(score=score_min))

            self._associate_officer_diligence_with_diligence(officer)

    @classmethod
    def diligences_in_county(klass, county):
        log.info("Buscando diligências para %s", str(county))
        return klass.objects.filter(county=county)

    def _open_manifestation(self):
        if (
            not self.has_manifestations.filter().exists()
            and int(self.delivery_status or 0) > 1
        ):
            self.part.open_manifestations(
                diligence=self, who=self.who, who_type=self.who_type
            )

    def get_deadline_diligence(self):
        cfg = Configuration.objects.get(application="ejud")
        return int(cfg.get("deadlineDiligence", 0))

    def publication_text(self):
        return DiligenceTemplate().formatted_message(
            "edital",
            **{
                "promotor": Servidor.objects.get(
                    user=self.part.signed_by
                ).pessoa_fisica.nome,
                "promotoria": self.part.lawsuit.location,
                "parte": self.who,
                "numero": self.part.lawsuit.cache_number,
                "assunto": self.part.lawsuit.title,
                "content": self.rendered,
            },
        )

    @property
    def deadline_date_for_delivery(self):
        query = self.has_manifestations.filter(signed_at__isnull=True)
        if query.exists():
            manifestation = query.first()
            return manifestation.deadline_date
        else:
            return None

    @property
    def has_manifestation_signed(self):
        return self.has_manifestations.filter(signed_at__isnull=False).exists()

    @property
    def number_pages(self):
        qt = 0
        for at in self.attaches.filter():
            qt += at.number_pages if at.number_pages else 0

        return qt

    @property
    def is_who_type_interested(self):
        return int(self.who_type or 0) == 1

    @property
    def is_who_type_accused(self):
        return int(self.who_type or 0) == 2

    @property
    def is_who_type_witness(self):
        return int(self.who_type or 0) == 3

    @property
    def is_who_type_executationorgan(self):
        return int(self.who_type or 0) == 4

    @property
    def is_who_type_publicorgan(self):
        return int(self.who_type or 0) == 5

    @property
    def is_who_type_company(self):
        return int(self.who_type or 0) == 6

    @property
    def is_who_type_internal(self):
        return int(self.who_type or 0) == 7

    @property
    def has_response_officer(self):
        return self.has_responses.exists()

    @property
    def response_is_signed_by_officer(self):
        if not self.has_response_officer:
            return False
        else:
            return self.has_responses.first().is_signed

    @property
    def number_event_control(self):
        return EventControl.number_control_of(self.part.lawsuit, self.part)

    def _associate_diligence_bloke_in_lawsuit(self):
        if self.is_who_type_accused and self.who:
            if not self.part.lawsuit.__contains_bloke__(self.who.pk):
                if self.who.kind == "pessoafisica":
                    Person.objects.create(
                        bloke=self.who.pessoafisica, lawsuit=self.part.lawsuit
                    )
                elif self.who.kind == "pessoajuridica":
                    Company.objects.create(
                        bloke=self.who.pessoajuridica, lawsuit=self.part.lawsuit
                    )
                else:
                    log.debug("%s is %s", self.who.nome, self.who.kind)
        else:
            log.debug("who type: %s", self.who_type)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.who_type:
                self.who_type = self.part.who_are(self.who)

            if not self.pk and self.part.read_only:
                if not hasattr(self.part, "decision_store"):
                    raise Exception(
                        "Não posso adicionar uma diligencia a um documento já assinado."
                    )

            if self.is_delivery_status_awaiting_distribution and not self.signed_by:
                self.signed_by = self.part.signed_by
                self.signed_at = self.part.signed_at
                self.execution_organ = self.part.lawsuit.location

                JudicialDiligenceLegalSign.sign(self)

                if self.prevent_delivery_in_executionorgan:
                    self.assumed_delivery_by = self.signed_by
                    self.assumed_delivery_at = self.signed_at
                    self.change_state_diligence(self.delivery_status, "entrega-orgao")

            super(JudicialDiligence, self).save(*args, **kwargs)

        self._open_manifestation()
        self._associate_diligence_bloke_in_lawsuit()


class ResponseOfficer(models.Model):
    diligence = models.ForeignKey(
        JudicialDiligence,
        related_name="has_responses",
        null=True,
        on_delete=models.PROTECT,
    )
    text = models.TextField()
    signed_by = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("signed_at",)

    @property
    def read_only(self):
        return self.is_signed

    @property
    def is_signed(self):
        return True if self.signed_by else False

    def sign(self):
        if not self.is_signed:
            with transaction.atomic():
                self.signed_by = get_current_user()
                self.signed_at = datetime.now()
                self.save()

                attached_document = AttachedDocument(
                    attached_title=self.__str__(),
                    resume=self.text,
                    diligence=self.diligence,
                    lawsuit=self.diligence.part.lawsuit,
                )
                attached_document.skip_validade_ownership = True
                attached_document.skip_read_only_validate = True
                attached_document.save()
                Attached.objects.filter(attached_response_officer=self).update(
                    attached_document=attached_document.pk
                )

                attached_document.sign_part()
                if self.diligence.has_manifestations.exists():
                    person = person_from_user(get_current_user())
                    for manifestation in self.diligence.has_manifestations.filter(
                        signed_by__isnull=True
                    ):
                        manifestation.content = self.text
                        manifestation.sign(person)

                self.diligence.ignore_validate_changes = True
                self.diligence.change_state_diligence(
                    self.diligence.delivery_status, "finalizado"
                )
                self.diligence.save()

        else:
            raise Exception(
                "Esta manifestação já foi assinada por %s." % self.signed_by
            )

    def __str__(self):
        return "Resposta de Diligência Interna {}".format(
            self.diligence.formated_number
        )

    def save(self, *args, **kwargs):
        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)
            if older.is_signed:
                raise Exception(
                    "Não é possivel alterar uma resposta que já foi assinada."
                )

        super(ResponseOfficer, self).save(*args, **kwargs)


class Manifestation(models.Model):
    reference = models.ForeignKey(
        PartLawsuit, related_name="manifestations", on_delete=models.PROTECT
    )
    diligence = models.ForeignKey(
        JudicialDiligence,
        related_name="has_manifestations",
        null=True,
        on_delete=models.PROTECT,
    )
    who = models.ForeignKey(
        "rh.pessoa", related_name="manifestations", on_delete=models.PROTECT
    )
    who_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "WHO_TYPE")
    )
    deadline = models.DateField(null=True, blank=True)
    manifestation_type = models.SmallIntegerField(
        choices=(
            (1, "Direta"),
            (2, "Indireta"),
        ),
        null=True,
        blank=True,
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        "rh.pessoa", related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    content = models.TextField()
    remaining_days = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("signed_at",)

    def def_deadline(self, days):
        if self.deadline:
            raise Exception("Não posso modificar o prazo da manifestação.")

        query_attempt = self.diligence.deliveryattempt_set.filter(
            delivery_date__isnull=False
        )

        if query_attempt.exists():
            delivery_attempt = query_attempt.get()
            self.deadline = delivery_attempt.delivery_date.date() + relativedelta(
                days=days
            )
            self.remaining_days = days
            self.save()
        else:
            raise Exception(
                "Não posso determinar prazo para um resposta de uma diligência que não foi entregue."
            )

    @property
    def renderer(self):
        tpl = loader.get_template("judicial/lawsuit/manifestation/base.html")

        params = {"manifestation": self, "doc": self.reference}

        data = [tpl.render(params)]
        data += [sign.rendered for sign in self.legal_signs.filter()]

        if self.legal_signs.filter().exists():
            data.append(
                loader.get_template("judicial/legal_sign_fundament.html").render({})
            )

        return "".join(data)

    @property
    def expirated(self):
        if self.remaining_days and self.remaining_days < 0 and not self.signed_at:
            return True
        elif (
            self.remaining_days
            and self.remaining_days < 0
            and self.signed_at.date() > self.deadline_date
        ):
            log.warning(
                "Erro de integridade, aparentemente a manifestação foi assinada depois de expirado o prazo."
            )
            return True
        else:
            return False

    @property
    def read_only(self):
        if (
            self.reference.can_sign_manifestation_after_deadline
            and self.reference.lawsuit.is_acting
        ):
            return self.signed_by is not None
        else:
            return self.signed_by or self.expirated

    @property
    def deadline_date(self):
        return (
            date.today() + relativedelta(days=self.remaining_days)
            if self.remaining_days
            else None
        )

    def sign(self, by):
        who_are = self.reference.who_are(by)
        indirect = who_are != self.who_type

        if not who_are and not self.diligence.part.lawsuit.is_acting:
            raise Exception(
                "Não foi possivel relacionar %s com este procedimento. Não pode assinar o documento."
                % by
            )

        if not self.signed_by:
            with transaction.atomic():
                log.info("Assinando a manifestação.")
                log.info("Por: %s", by)
                log.info("Quem é: %s", who_are)
                log.info("Manifestação de quem: %s", self.who_type)
                log.info("Foi indireta a entrega? %s", "Sim" if indirect else "Não")

                self.signed_by = by
                self.signed_at = datetime.now()
                self.manifestation_type = 2 if indirect else 1
                self.save()

                ManifestationLegalSign.sign(self)
        else:
            raise Exception(
                "Esta manifestação já foi assinada por %s." % self.signed_by
            )

    def validate_change(self):
        older = self.__class__.objects.get(pk=self.pk)

        if older.signed_by:
            raise Exception("Não posso modificar uma manifestação que já foi assinada.")

        if older.who_type != int(self.who_type or 0):
            raise Exception("Não posso modificar o tipo envolvido na manifestação.")

        if older.who.pk != self.who.pk:
            raise Exception("Não posso modificar o envolvido na manifestação.")

    def validate(self):
        if self.pk:
            self.validate_change()

    def delete(self, *args, **kwargs):
        if self.read_only:
            raise Exception("Não posso remover uma manifestação que já foi aceita.")

        super(Manifestation, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not getattr(self, "ignore_validate", False):
            self.validate()
        super(Manifestation, self).save(*args, **kwargs)

    def _icon_manifestation_type(self):
        if int(self.manifestation_type or 0) == 1:
            return {
                "iconCls": "icon-judicial icon-ejud-manifestation-direct",
                "title": "Manifestação realizada pelo proprio requisitado.",
            }
        elif int(self.manifestation_type or 0) == 2:
            return {
                "iconCls": "icon-judicial icon-ejud-manifestation-indirect",
                "title": "Manifestação realizada indiretamente pelo requisitado.",
            }
        elif self.expirated:
            return {
                "iconCls": "icon-judicial icon-ejud-outlawcortsuit-not-have-time",
                "title": "Perdeu o parazo para fazer a manifestação.",
            }
        else:
            return {
                "iconCls": "icon-judicial icon-ejud-manifestation-blank",
                "title": "Ainda não foi feita nenhuma manifestação",
            }

    def _icon_who_type(self):
        icon_map = {
            1: {
                "iconCls": "icon-judicial icon-ejud-interested",
                "title": "Interessado",
            },
            2: {"iconCls": "icon-judicial icon-ejud-accused", "title": "Acusado"},
            3: {"iconCls": "icon-judicial icon-ejud-witness", "title": "Testemunha"},
            4: {
                "iconCls": "icon-judicial icon-ejud-executation-organ",
                "title": "Órgão de Execução",
            },
        }

        return icon_map.get(int(self.who_type or 0), {})

    def __str__(self):
        return str(self.diligence)

    @property
    def icons(self):
        return [self._icon_who_type(), self._icon_manifestation_type()]

    @property
    def number_pages(self):
        qt = 0
        for at in self.attaches.filter():
            qt += at.number_pages if at.number_pages else 0
        return qt

    @classmethod
    def queryset_manifestation_to_decrement_day(cls, location=None, to_date=None):
        executed_today = DeadlineLog.queryset_manifestation_executed_to_date(
            to_date=to_date
        )
        return cls.objects.filter(
            Q(
                Q(signed_by__isnull=True)
                & Q(
                    diligence__in=JudicialDiligence.objects.filter(
                        execution_organ__localidade=location
                    )
                )
            )
        ).exclude(pk__in=executed_today)

    @classmethod
    def queryset_manifestation_to_weekend_decrement_day(
        cls, location=None, to_date=None
    ):
        return cls.queryset_manifestation_to_decrement_day(
            location=location, to_date=to_date
        ).exclude(Q(Q(remaining_days=1) & Q(diligence__count_type=2)))

    @classmethod
    def decrement_remaining_days(cls, query_set=[], dry_run=True):
        for m in query_set:
            if not dry_run and m.remaining_days is not None:

                DeadlineLog.register(
                    manifestation=m,
                    days=m.remaining_days,
                    observation="Inserido pelo sistema",
                )

                days = m.remaining_days - 1
                cls.objects.filter(pk=m.pk).update(remaining_days=days)

                if m.diligence.is_delivery_status_awaiting_answer and days < 0:
                    m.diligence.change_state_diligence(
                        m.diligence.delivery_status, "atrasado"
                    )
                    m.diligence.ignore_validate_changes = True
                    m.diligence.save()


class Intimation(JudicialDiligence):
    def __str__(self):
        return "Intimação"


class Citation(JudicialDiligence):
    def __str__(self):
        return "Citação"


class NotificationDiligence(JudicialDiligence):
    def __str__(self):
        return "Notificação"


class Scientization(JudicialDiligence):
    def __str__(self):
        return "Cientificação"


class DiligenceRequest(JudicialDiligence):
    def __str__(self):
        return "Requisição"


class DeliveryAttempt(AuditTimestampModel):
    """
    Modelo tentativas de entrega
    """

    diligence = models.ForeignKey(Diligence, null=True, on_delete=models.PROTECT)
    observation = models.TextField(blank=True)
    file_delivery = models.OneToOneField(
        Arquivo, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    exit_date = models.DateTimeField(
        null=True, blank=True, verbose_name="data e hora de saida para entrega"
    )
    return_date = models.DateTimeField(
        null=True, blank=True, verbose_name="data e hora de retorno da entrega"
    )
    delivery_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Momento da entrega"
    )
    attempt = models.SmallIntegerField(
        null=True, blank=True, verbose_name="tentativas de entrega"
    )
    delivered = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "DELIVERED"),
        null=True,
        blank=True,
        verbose_name="a diligencia foi entregue ao destinatario ou nao",
    )
    type_vehicle = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_VEHICLE"),
        null=True,
        blank=True,
        verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
    )
    cancel_delivery = models.BooleanField(default=False)
    cancel_delivery_type = models.SmallIntegerField(
        blank=True,
        null=True,
        choices=Choice.get_choices_for("judicial", "DELIVERY_CANCELATION_REASON"),
    )
    signed_by = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signed_at = models.DateTimeField(null=True, blank=True)
    cache_rendered = models.TextField(null=True, blank=True)
    is_signed_by_system = models.BooleanField(default=False)

    class Meta:
        ordering = ("diligence", "-attempt")

    @property
    def delivered_at(self):
        return DateUtils.datetime_to_str(self.modified_at) if self.modified_at else ""

    @property
    def delivered_by(self):
        return employee_from_user(self.modified_by, False)

    @property
    def delivered_by_unicode(self):
        return str(self.delivered_by.pessoa_fisica)

    def _get_organ_signer(self):
        organ = None
        if self.diligence.is_delivery_status_organ_delivery or self.is_signed_by_system:
            organ = self.diligence.judicialdiligence.part.lawsuit.location
        else:
            if self.signed_by.servidor.work_assignment_effective_exercise.filter(
                main=True
            ):
                organ = (
                    self.signed_by.servidor.work_assignment_effective_exercise.filter(
                        main=True
                    )
                    .first()
                    .lotacao
                )
            elif self.signed_by.servidor.workplace_only.filter(ativo=True):
                organ = (
                    self.signed_by.servidor.workplace_only.filter(ativo=True)
                    .first()
                    .lotacao
                )

        return organ

    @property
    def rendered(self):
        if self.cache_rendered:
            return self.cache_rendered

        is_judicialdiligence_internal = False
        if (
            getattr(self.diligence, "judicialdiligence", None)
            and self.diligence.judicialdiligence.is_who_type_internal
        ):
            is_judicialdiligence_internal = True

        data = [
            loader.get_template("judicial/lawsuit/delivery.html").render(
                {
                    "doc": self,
                    "is_judicialdiligence_internal": is_judicialdiligence_internal,
                    "sign": {
                        "moment_at": self.signed_at,
                        "person": (
                            self.signed_by.servidor.pessoa_fisica
                            if self.signed_by
                            else None
                        ),
                        "organ": self._get_organ_signer() if self.signed_by else None,
                        "is_signed_by_system": self.is_signed_by_system,
                    },
                }
            )
        ]

        data += [sign.rendered for sign in self.legal_signs.filter()]

        if self.legal_signs.filter().exists():
            data.append(
                loader.get_template("judicial/legal_sign_fundament.html").render({})
            )

        return "".join(data)

    @property
    def limits(self):
        if not getattr(self, "__cache_limits", None):
            start_date = None
            end_date = datetime.now()
            diligence = self.diligence

            query = diligence.deliveryattempt_set.exclude(pk=self.pk)
            if query.exists():
                start_date = (query.order_by("-return_date").first()).return_date
            else:
                start_date = (
                    diligence.date_receipt_diligence
                    if not diligence.assumed_delivery_at
                    else diligence.assumed_delivery_at
                )

            self.__cache_limits = [start_date, end_date]

        return self.__cache_limits

    @property
    def is_delivered(self):
        return self.delivered == 1

    @property
    def is_sign(self):
        return True if self.signed_by else False

    @property
    def icons_sign(self):
        if self.is_sign:
            return [{"iconCls": "icon-judicial icon-ejud-signed", "title": "Assinado"}]
        return [
            {
                "iconCls": "icon-judicial icon-ejud-unsigned",
                "title": "Não foi asssinado",
            }
        ]

    def _validate_sign_delivery_attempt(self):
        if not self.pk:
            raise Exception(
                "É necessário salvar a tentativa de entrega antes de assinar"
            )

        if self.is_sign:
            raise Exception(
                "Esta Tentativa de entrega já foi assinada por %s." % self.signed_by
            )

        if not self.cancel_delivery:
            if not self.exit_date or not self.return_date:
                raise Exception(
                    "Para assinar a tentativa de entrega é necessário preencher as datas de saída e de retorno, caso não seja uma devolução."
                )

    def sign(self):
        self._validate_sign_delivery_attempt()
        with transaction.atomic():
            self.signed_by = get_current_user()
            self.signed_at = datetime.now()
            if self.delivery_date:
                self.delivered = 1

            self.save()
            DeliveryAttemptLegalSign.sign(self)

            self.__class__.objects.filter(pk=self.pk).update(
                cache_rendered=self.rendered
            )

            self.diligence.judicialdiligence.part.invalidate_cache()

    def validate_add_delivery_attempt(self):
        query = self.diligence.deliveryattempt_set.exclude(pk=self.pk)
        if query.filter(signed_at=None).exists():
            raise Exception(
                "Antes de adicionar uma nova tentativa de entrega, verifique se a tentativa anterior foi assinada."
            )
        if query.filter(delivery_date__isnull=False).exists():
            raise Exception(
                "Não é mais possível adicionar tentativa de entrega para esta Diligência. A entrega já foi realizada."
            )

    def delete(self, *args, **kwags):
        if self.is_sign:
            raise Exception(
                "Não posso remover uma tentativa de entrega que já teve o efeito."
            )
        super(DeliveryAttempt, self).delete(*args, **kwags)

    def cancel_delivery_notificate(self):
        destination = self.diligence.judicialdiligence.execution_organ
        log.info("notify cancel delivery of diligence %s", self.diligence)
        for employee in destination.lotacao.employees:
            log.info("notify: %s", employee)

            part = self.diligence.judicialdiligence.part
            lawsuit = part.lawsuit

            Notification.notify(
                "EJUD_CANCEL_DELIVERY",
                employee,
                sender=self,
                diligence=self.diligence.formated_number,
                lawsuit=lawsuit.cache_number,
                cancel_delivery_type=self.get_cancel_delivery_type_display(),
                event_number=EventControl.number_control_of(lawsuit, part),
            )

    def _validate_date_delivery_attempt(self):
        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)
            if older.is_sign:
                raise Exception(
                    "Não posso modificar uma tentativa de entrega que já foi assinada."
                )

        if not self.exit_date and not self.cancel_delivery:
            raise Exception("É necessário o preenchimento do momento de saída.")

        if self.cancel_delivery and not self.cancel_delivery_type:
            raise Exception(
                "É necessário o preenchimento do motivo de devolução quando a opção de devolução for preenchida."
            )

        if self.return_date or self.delivery_date:
            if self.delivery_date and not self.return_date:
                raise Exception(
                    "É necessário o preenchimento do momento do retorno quando o momento da entrega for preenchido."
                )

            if self.exit_date == self.return_date:
                raise Exception(
                    "O momento de retorno não pode ser igual o momento da saída."
                )

            if self.return_date > self.limits[1]:
                raise Exception(
                    "O momento do retorno não pode ser posterior à %s."
                    % DateUtils.datetime_to_str(self.limits[1])
                )

            if self.delivery_date and (
                self.delivery_date < self.exit_date
                or self.delivery_date > self.return_date
            ):
                raise Exception(
                    "Momento da entrega incompativel com o registros de saída e retorno."
                )

            if self.delivery_date and not self.file_delivery:
                raise Exception(
                    "O registro da entrega requer o documento de confirmação de entrega."
                )

    def _change_diligence_after_delivery_attempt(self):
        self.delivered = int(self.delivered or 0)
        if self.is_sign:
            if self.is_delivered:
                self.diligence.ignore_validate_changes = True
                self.diligence.change_state_diligence(
                    self.diligence.delivery_status, "aguardando-resposta"
                )
                self.diligence.date_delivery = self.delivery_date
                self.diligence.save()
            elif self.cancel_delivery:
                self.diligence.ignore_validate_changes = True
                self.diligence.change_state_diligence(
                    self.diligence.delivery_status, "devolvido"
                )
                self.diligence.save()
                if self.diligence.judicialdiligence:
                    self.cancel_delivery_notificate()

    def _validate_attempt(self):
        if not self.attempt:
            self.attempt = (
                self.__class__.objects.filter(diligence=self.diligence).count() + 1
            )

        if (
            int(self.attempt)
            > self.diligence.judicialdiligence.get_deadline_diligence()
        ):
            raise Exception(
                "Não é mais possível adicionar tentativa de entrega para esta Diligência. Já foi solicitado publicação em Diário Oficial."
            )

    def save(self, *args, **kwargs):
        if not getattr(self, "ignore_validate_changes", False):
            self.validate_add_delivery_attempt()
            self._validate_date_delivery_attempt()
            self._validate_attempt()

        super(DeliveryAttempt, self).save(*args, **kwargs)

        self._change_diligence_after_delivery_attempt()

    def full_clean(self):
        try:
            super(DeliveryAttempt, self).full_clean()
        except ValidationError as e:
            if "file_delivery" in e.message_dict:
                delivery_attempt = DeliveryAttempt.objects.get(
                    file_delivery=self.file_delivery
                )
                raise Exception(
                    "Arquivo já utilizado na tentativa de entrega da diligência {}".format(
                        delivery_attempt.diligence.formated_number
                    )
                )


@type_part_lawsuit()
class AttachedDocument(PartLawsuit):
    attached_title = models.CharField(max_length=150, blank=True, null=True)
    resume = models.TextField()
    attached_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "ATTACHED_TYPE"),
        default=1,
        blank=True,
        null=True,
    )
    diligence = models.ForeignKey(
        Diligence,
        related_name="as_diligence_answer",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Resposta de Diligência"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @property
    def title(self):
        if self.diligence:
            return self.attached_title if self.attached_title else self.codename
        else:
            return (
                self.attached_title if self.attached_title else "Juntada de Documentos"
            )

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-attached"

    def params(self):
        rst = PartLawsuit.params(self)

        rst.update(
            attached={
                "attached_title": self.attached_title,
                "resume": self.resume,
                "attaches": self.attaches.filter(),
            }
        )

        return rst

    def sign_part(self):
        with transaction.atomic():
            super(AttachedDocument, self).sign_part()

            if self.diligence and hasattr(self.diligence, "judicialdiligence"):
                Attached.objects.filter(attached_document__pk=self.pk).update(
                    attached_manifestation=self.diligence.judicialdiligence.has_manifestations.first()
                )

                person = person_from_user(get_current_user())
                for m in self.diligence.judicialdiligence.has_manifestations.filter(
                    signed_at__isnull=True
                ):
                    m.sign(person)

    def save(self, *args, **kwargs):
        if self.diligence:
            self.attached_title = (
                "Resposta da Diligência Nº " + self.diligence.formated_number
            )

        super(AttachedDocument, self).save(*args, **kwargs)


class PartLawsuitAccess(AuditTimestampModel):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit,
        related_name="access_controls",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    part = models.ForeignKey(
        PartLawsuit,
        related_name="access_controls",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    motivation = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "PARTLAWSUIT_ACCESS_MOTIVATION"),
        null=True,
        blank=True,
    )
    justification = models.TextField(blank=True)
    signed_by = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signed_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    suspended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = (
            "-signed_at",
            "-created_at",
        )

    @property
    def title(self):
        obj = self.lawsuit if self.lawsuit else self.part
        return str(obj)

    @property
    def icon_attachement(self):
        if self.attaches.exists():
            return {
                "iconCls": "icon-judicial icon-ejud-inquerito-civil-publico-in-grid",
                "title": "%d anexo%s"
                % (self.attaches.count(), "s" if self.attaches.count() > 1 else ""),
            }
        return {}

    @property
    def icon_state(self):
        if self.signed_by and not self.suspended_by:
            return {
                "iconCls": "icon-judicial icon-ejud-part-access",
                "title": "Ativo %s" % person_from_user(self.signed_by),
            }
        elif self.suspended_by:
            return {
                "iconCls": "icon-judicial icon-ejud-part-access-removed",
                "title": "Suspenso por %s" % person_from_user(self.suspended_by),
            }
        else:
            return {
                "iconCls": "icon-judicial icon-ejud-part-access-edit",
                "title": "Em edição",
            }

    @property
    def icons(self):
        return [self.icon_state, self.icon_attachement]

    @property
    def read_only(self):
        return True if self.signed_by else False

    def sign(self):
        self.signed_by = get_current_user()
        self.signed_at = datetime.now()
        self.save()

    @property
    def can_read(self):
        can_read = False

        if self.part:
            can_read = True if self.part.can_read else False

        if self.lawsuit:
            can_read = True if self.lawsuit.can_read else False

        return can_read

    @property
    def user_boss_location(self):
        try:
            location = None

            if self.lawsuit:
                location = self.lawsuit.location
            elif self.part:
                location = self.part.lawsuit.location

            return (
                location.responsavel.user
                if location.responsavel
                else get_current_user()
            )
        except Exception:
            return get_current_user()

    def suspend(self):
        if self.can_read:
            self.suspended_by = get_current_user()
            self.suspended_at = datetime.now()
            self.save()
        else:
            raise Exception(
                "Você não tem permissão para suspender o pedido de sigilosidade deste documento."
            )

    def delete(self, *args, **kwags):
        if self.signed_by and self.can_read:
            self.suspend()
        elif self.signed_by:
            raise Exception("Você não tem permissão para este tipo de ação.")
        else:
            super(PartLawsuitAccess, self).delete(*args, **kwags)

    def add_person_access(self, controlled=False, person=None, user=None, state=1):
        """
        Esse método adiciona, sem que haja validação em PersonHasAccess, as pessoas que terão acesso aos procedimentos com sigilo.
        """
        employee = person if person else person_from_user(user)
        if not self.authorization.filter(person=employee, state__in=[1, 2]):
            authorization = PersonHasAccess(
                person=employee, state=state, controlled=controlled
            )
            authorization.without_check_access = True
            authorization.grant_by_system = True
            self.authorization.add(authorization, bulk=False)

    @classmethod
    def swap_permission_access(
        cls, location=None, new_employee=None, old_employee=None
    ):
        """
        Esse método realiza a troca de acesso aos procedimentos sigilosos entre o antigo e o novo responsável
        de uma determinada lotação.
        """
        if location and new_employee:
            query = PartLawsuitAccess.objects.filter(
                signed_at__isnull=False, suspended_at=None
            ).filter(
                Q(
                    Q(
                        part__in=PartLawsuit.objects.filter(
                            lawsuit__location=location
                        ).filter(access_controls__isnull=False)
                    )
                    | Q(
                        lawsuit__in=OutCourtLawsuit.objects.filter(
                            location=location
                        ).filter(access_controls__isnull=False)
                    )
                )
            )

            for acesss in query:
                log.debug("Adicionando permissao para %s" % str(new_employee))
                acesss.add_person_access(controlled=True, user=new_employee.user)

            if old_employee:
                log.debug("Revogando permissao de %s" % str(old_employee))
                for obj in PersonHasAccess.objects.filter(
                    controlled=True,
                    access__in=query,
                    state=1,
                    person=person_from_user(old_employee.user),
                ):
                    obj.without_check_access = True
                    obj.state = 3
                    obj.finished_by = get_current_user()
                    obj.finished_at = datetime.now()
                    obj.revoked_by_system = True
                    obj.save()
        else:
            log.info("Nada foi feito.")

    @property
    def number_pages(self):
        qt = 0
        for at in self.attaches.filter():
            qt += at.number_pages if at.number_pages else 0
        return qt

    def save(self, *args, **kwags):
        created = True if not self.pk else False
        super(PartLawsuitAccess, self).save(*args, **kwags)

        if created:
            if get_current_user() == self.user_boss_location:
                self.add_person_access(controlled=True, user=get_current_user())
            else:
                self.add_person_access(user=get_current_user())
                self.add_person_access(controlled=True, user=self.user_boss_location)


class PersonHasAccess(AuditTimestampModel):
    access = models.ForeignKey(
        PartLawsuitAccess, related_name="authorization", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    person = models.ForeignKey(
        "rh.pessoa", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    state = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "PERSON_ACCESS_STATE")
    )
    controlled = models.BooleanField(default=False)
    finished_by = models.ForeignKey(
        User,
        related_name="+",
        verbose_name="Finalizado por",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    finished_at = models.DateTimeField(
        verbose_name="Finalizado em", null=True, blank=True
    )
    revoked_by_system = models.BooleanField(default=False)
    grant_by_system = models.BooleanField(default=False)

    class Meta:
        ordering = ("state", "-created_at")

    def validate_remove(self):
        if not self.can_change_controlled:
            raise Exception("Essa permissão não pode ser removida.")
        if not self.access.authorization.exclude(pk=self.pk).filter(state=1).exists():
            raise Exception(
                "O documento precisa de pelo menos um administrador de sigilo."
            )

    def delete(self, *args, **kwags):
        self.validate_remove()

        if self.state == 3:
            raise Exception(
                "Esta autorização já foi revogada, mas não pode ser removida."
            )
        else:
            self.state = 3
            self.finished_by = get_current_user()
            self.finished_at = datetime.now()
            self.save()

    @property
    def icons(self):
        icon_set = [
            None,
            "icon-judicial icon-ejud-approved",
            "icon-judicial icon-ejud-partially-approved",
            "icon-judicial icon-ejud-not-approved",
        ]

        return [
            {
                "iconCls": icon_set[int(self.state) or 0],
                "title": self.get_state_display(),
            }
        ]

    def validate_changes(self):
        if not self.can_change_controlled:
            raise Exception("Essa permissão não pode ser editada.")

        older = self.__class__.objects.get(pk=self.pk)
        query = self.access.authorization.exclude(pk=self.pk).filter(state=1)

        if (
            older.state != int(self.state or 0)
            and older.state == 1
            and not query.exists()
        ):
            raise Exception(
                "O documento precisa de pelo manos um administrador de sigilo."
            )

    @property
    def can_change_controlled(self):
        if getattr(self, "without_check_access", False):
            return True
        else:
            return True if not self.controlled else False

    def save(self, *args, **kwags):
        created = self.pk is None

        if self.pk:
            self.validate_changes()
            older = self.__class__.objects.get(pk=self.pk)

        if not getattr(self, "without_check_access", False):
            query = self.__class__.objects.filter(
                Q(access=self.access)
                & Q(person=person_from_user(get_current_user()))
                & Q(state=1)
            )

            if not query.exists() and self.access.signed_by:
                raise Exception("Você não tem direito de acesso a este documento.")

        super(PersonHasAccess, self).save(*args, **kwags)

        confidential_access = self.access.in_grantconfidentialaccess.first()

        if getattr(self, "_replicate", False) and confidential_access:
            if created:
                for access in confidential_access.part_lawsuit_access.exclude(
                    pk=self.access.pk
                ):
                    obj = PersonHasAccess(
                        person=self.person, state=self.state, access=access
                    )
                    obj._replicate = False
                    obj.save()
            else:
                if (older.person != self.person) or (older.state != self.state):
                    query = (
                        self.__class__.objects.exclude(pk=self.pk)
                        .filter(
                            access__in=confidential_access.part_lawsuit_access.filter()
                        )
                        .filter(
                            person=older.person, state=older.state, controlled=False
                        )
                    )

                    for access in query:
                        access.person = self.person
                        access.state = self.state
                        access._replicate = False
                        access.save()


class Attached(AuditTimestampModel):
    attached_document = models.ForeignKey(
        PartLawsuit,
        related_name="attaches",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    attached_manifestation = models.ForeignKey(
        Manifestation,
        related_name="attaches",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    attached_part_access = models.ForeignKey(
        PartLawsuitAccess,
        related_name="attaches",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    attached_diligence = models.ForeignKey(
        Diligence,
        related_name="attaches",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    attached_response_officer = models.ForeignKey(
        ResponseOfficer,
        related_name="attaches",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    title = models.CharField(max_length=250, blank=True)
    file_descriptor = models.ForeignKey(
        "ged.arquivo", related_name="+", on_delete=models.PROTECT
    )
    published_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    published_at = models.DateTimeField(null=True, blank=True)
    render_extract = models.BooleanField(default=True)
    number_pages = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)

    def process_renderer_pages(self):
        drivers = {
            r"^(application|adobe)\/(pdf|octet\-stream|force\-download)$": self.process_renderer_pages_of_protable_document,
            r"^(image\/jpeg)$": self.process_renderer_image,
        }

        processor = None
        for test, fn in list(drivers.items()):
            if re.match(test, self.file_descriptor.mimetype):
                processor = fn
                break

        (processor if processor else lambda: None)()

    def process_renderer_image(self):
        self.__class__.objects.filter(pk=self.pk).update(number_pages=1)

    def _process_renderer_pages_of_protable_document_execute(
        self, filebase, dest, start_page, end_page
    ):
        cmd = [
            '"/usr/bin/convert"',
            "-background",
            "white",
            "-limit",
            "memory",
            "%s" % (getattr(settings, "JUDICIAL_CONVERT_LIMIT_MEMORY")),
            "-limit",
            "map",
            "%s" % (getattr(settings, "JUDICIAL_CONVERT_LIMIT_MAP")),
            '"-density"',
            '"%s"' % (getattr(settings, "JUDICIAL_CONVERT_DENSITY")),
            '"-quality"',
            '"%s"' % (getattr(settings, "JUDICIAL_CONVERT_QUALITY")),
            '"%s[%d-%d]"' % (filebase, start_page, end_page - 1),
            '"-resize"',
            '"794"',
            '"%s"' % dest,
        ]

        log.info(" ".join(cmd))
        pid_fd = Popen(" ".join(cmd), shell=True, stdout=PIPE, stderr=PIPE)
        pid_fd.wait()

        log.info("Return code %d", pid_fd.returncode)
        if pid_fd.returncode != 0:
            for chunk in iter(partial(pid_fd.stderr.read, 8192), ""):
                try:
                    log.error(chunk)
                except Exception:
                    log.error("Processing %s", self.file_descriptor.file)

    def process_renderer_pages_of_protable_document(self):
        from judicial.tasks import (
            process_renderer_pages_of_protable_document_executor as executor,
        )

        filebase = self.file_descriptor.absolute_path
        filebase = (
            "%s.recovered" % filebase
            if os.path.exists("%s.recovered" % filebase)
            else filebase
        )

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

            render_extract = (
                False
                if self.render_extract is False
                else pdf_fd.numPages < self.page_number_limit
            )

            self.__class__.objects.filter(pk=self.pk).update(
                number_pages=pdf_fd.numPages, render_extract=render_extract
            )

            signatures = []
            step = getattr(settings, "EXTRACTOR_STEP", 5)
            for start in range(0, pdf_fd.numPages, step):
                end = start + step

                if end > pdf_fd.numPages:
                    end = pdf_fd.numPages

                signatures.append(
                    executor.s(
                        filebase,
                        os.path.join(
                            cachedir, getattr(settings, "EXTRACTOR_OUTPUT", "%05d.jpg")
                        ),
                        start,
                        end,
                    )
                )

            job = group(signatures)()

            def cb(task, values):
                log.debug("waiting work, finished task %s...", task)
                if job.ready():
                    log.info("remove recovery file %s", filebase)
                    os.unlink(filebase)

            if filebase.endswith(".recovered"):
                log.info("running with recovery")
                job.join(callback=cb)
            else:
                log.info("running without recovery")

        else:
            log.info("file cache not found")

    def extract_pages(self):
        drivers = {
            r"^application\/(pdf|octet\-stream|force\-download)$": self.extract_pages_of_portable_document,
            r"^image\/(png|jpeg|jpg|gif)$": self.extract_pages_of_image,
        }

        extractor = self.extract_pages_of_fallback

        if self.render_extract:
            for test, fn in list(drivers.items()):
                if re.match(test, self.file_descriptor.mimetype):
                    extractor = fn
                    break

        log.debug(extractor())

        return extractor()

    def extract_pages_of_image(self):
        from PIL import Image
        from io import BytesIO
        from base64 import b64encode

        tpl = loader.get_template("judicial/attached_page.html")
        reference_date = None
        if self.attached_to.signed_at:
            reference_date = self.attached_to.signed_at + relativedelta(seconds=1)
        else:
            reference_date = self.attached_to.created_at

        pages = [{"page": tpl.render({"attached": self}), "at": reference_date}]

        try:
            filepath = self.file_descriptor.absolute_path
            filecache = "%s.img-cache" % filepath

            data = BytesIO()

            if os.path.exists(filecache):
                with open(filecache, "rb") as fd:
                    for chunk in iter(partial(fd.read, 8096), b""):
                        data.write(chunk)
            else:
                img = Image.open(filepath)
                if img.mode == "RGBA":
                    img_fd = img.convert("RGB")
                else:
                    img_fd = img

                log.info("filename: %s", filepath)
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

                img_fd.save(data, "JPEG")
                img_fd.save(open(filecache, "wb"), "JPEG")

            pages.append(
                {
                    "page": '<div class="page-of-image" style="margin: -15mm -20mm; width: 210mm; height: 297mm; background: url(data:image/jpeg;base64,%s) center center no-repeat"></div>'
                    % (b64encode(data.getvalue()).decode()),
                    "at": reference_date,
                }
            )
        except Exception as e:
            log.exception(e)
            pages.append({"page": "<p>%s</p>" % e, "at": self.created_at})

        return pages

    def extract_pages_of_portable_document(self):
        cachedir = os.path.join(
            os.path.join(getattr(settings, "CACHE_BASE", ""), "ejud"),
            self.file_descriptor.file,
        )

        tpl = loader.get_template("judicial/attached_page.html")
        reference_date = None
        if self.attached_to.signed_at:
            reference_date = self.attached_to.signed_at + relativedelta(seconds=1)
        else:
            reference_date = self.attached_to.created_at

        try:
            pages = [{"page": tpl.render({"attached": self}), "at": reference_date}]

            if os.path.exists(cachedir):
                pages += [
                    {
                        "page": '<div class="page-of-portable" style="background: url(\'/athenas/static/judicial-cache/%s/%s\') center center no-repeat"></div>'
                        % (self.file_descriptor.file, filename),
                        "at": reference_date,
                    }
                    for filename in sorted(os.listdir(cachedir))
                ]

            return pages
        except Exception as e:
            log.exception(e)
            return [{"page": "%s" % e, "at": self.file_descriptor.created}]

    def extract_pages_of_fallback(self):
        tpl = loader.get_template("judicial/attached_page.html")
        reference_date = None
        if self.attached_to.signed_at:
            reference_date = self.attached_to.signed_at + relativedelta(seconds=1)
        else:
            reference_date = self.attached_to.created_at

        return [{"page": tpl.render({"attached": self}), "at": reference_date}]

    @property
    def attached_to(self):
        if self.attached_document:
            return self.attached_document
        elif self.attached_manifestation:
            return self.attached_manifestation
        elif self.attached_part_access:
            return self.attached_part_access
        elif self.attached_diligence:
            return self.attached_diligence
        elif self.attached_response_officer:
            return self.attached_response_officer
        else:
            return None

    @property
    def icons(self):
        icons = [
            {
                "title": self.file_descriptor.mimetype,
                "iconCls": "icon-ged icon-ged-%s"
                % slugify(
                    self.file_descriptor.mimetype.replace("/", "-").replace("+", "-")
                ),
            }
        ]

        if self.is_published:
            icons.append(
                {"title": "Publico", "iconCls": "icon-judicial icon-ejud-public"}
            )

        return icons

    @property
    def is_published(self):
        return self.published_by is not None

    def toggle_publish(self):
        self.published_by = get_current_user() if not self.published_by else None
        self.published_at = datetime.now() if not self.published_at else None
        self.skip_read_only_validate = True
        self.save()

    @property
    def possible_owners(self):
        return (
            "attached_document",
            "attached_manifestation",
            "attached_part_access",
            "attached_diligence",
            "attached_response_officer",
        )

    @property
    def owner(self):
        for attr in self.possible_owners:
            if getattr(self, attr):
                return getattr(self, attr)
        return None

    @property
    def page_number_limit(self):
        return 100

    def delete(self, *args, **kwargs):
        if self.owner.read_only:
            raise Exception("Não posso modificar um anexo de um documento assinado.")

        super(Attached, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.owner:
            raise Exception("Não posso criar uma anexo sem um dono.")

        if not self.title:
            self.title = self.file_descriptor.filename

        if not getattr(self, "skip_read_only_validate", False) and self.owner.read_only:
            log.debug([self.owner, self.owner.read_only])
            raise Exception("Não posso modificar um anexo de um documento assinado.")

        self.file_descriptor.acesso = 3 if self.is_published else 2
        self.file_descriptor.save()

        super(Attached, self).save(*args, **kwargs)

        from judicial.tasks import process_attached_document

        process_attached_document.delay(self.pk)


@type_part_lawsuit()
class RejectionLinkOther(PartLawsuit):
    despatch = models.TextField()
    other_lawsuit = models.SmallIntegerField(
        choices=(
            (1, "Procedimento Extrajudicial"),
            (2, "Procedimento Judicial"),
        )
    )
    other_lawsuit_number = models.CharField(max_length=100)
    other_lawsuit_organ = models.ForeignKey(
        OrgaoGeral, related_name="+", null=True, on_delete=models.PROTECT
    )

    codename = "Andamento em outro Procedimento"
    only_responsible_sign = True

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def save(self, *args, **kwargs):
        if self.lawsuit.type_lawsuit > 1:
            raise Exception(
                "Só posso indeferir uma Noticia de Fato, este procedimento já foi instaurado como %s."
                % self.lawsuit.get_type_lawsuit_display()
            )

        super(RejectionLinkOther, self).save(*args, **kwargs)

    def sign_part(self):
        with transaction.atomic():
            super(RejectionLinkOther, self).sign_part()
            execution_organ = self.lawsuit.location
            self.lawsuit.send_to(to=execution_organ, finalizado=True)

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(
            doc=self,
            rejection={
                "other_lawsuit": self.other_lawsuit,
                "other_lawsuit_display": self.get_other_lawsuit_display(),
                "other_lawsuit_number": self.other_lawsuit_number,
                "other_lawsuit_organ": (
                    self.other_lawsuit_organ.nome if self.other_lawsuit_organ else None
                ),
                "despatch": self.despatch,
                "execution_organ": execution_organ,
                "modified_at": self.modified_at,
            },
        )

        return rst

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-rejection-link-other"


@type_part_lawsuit()
class RejectionFact(PartLawsuit):
    despatch = models.TextField()
    rejection_fact_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "REJECTION_FACT_TYPE")
    )
    decision_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "DECISION_TYPE"),
        null=True,
        blank=True,
    )
    decision_text_cache = models.TextField(null=True, blank=True)
    decision_text = models.TextField(null=True, blank=True)
    decided_by = models.ForeignKey(
        "auth.user",
        related_name="in_reconsideration_rejection_facts",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    type_ordinace = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_ORDINACE"),
        null=True,
        blank=True,
    )
    rejected_ordinace = models.ForeignKey(
        Ordinace,
        related_name="in_rejection_fact",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    codename = "Indeferimento da Noticia de Fato"
    only_responsible_sign = True

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @property
    def can_sign_manifestation_after_deadline(self):
        return False

    @property
    def extra_pages(self):
        pages = PartLawsuit.extra_pages.fget(self)

        if self.decided_by:
            pages.append(self.decision_formated)

        return pages

    @property
    def in_manifestation_stage(self):
        if self.in_edit_stage:
            return False

        flag = False
        for manifestation in self.manifestations.filter(signed_by=None):
            if not manifestation.expirated:
                flag = True
                break

        return flag

    @property
    def in_decision_stage(self):
        log.debug(
            [
                not self.in_manifestation_stage,
                not self.in_edit_stage,
                not self.decided_by,
            ]
        )
        return (
            not self.in_manifestation_stage
            and not self.in_edit_stage
            and not self.decided_by
        )

    @property
    def in_edit_stage(self):
        return not self.signed_by

    @property
    def stage(self):
        if self.in_edit_stage:
            return "edit"
        elif self.in_manifestation_stage:
            return "manifestation"
        elif self.in_decision_stage:
            return "decision"
        else:
            return "ended"

    def save(self, *args, **kwargs):
        created = not self.pk

        if self.lawsuit.type_lawsuit > 1:
            raise Exception(
                "Só posso indeferir uma Noticia de Fato, este procedimento já foi instaurado como %s."
                % self.lawsuit.get_type_lawsuit_display()
            )

        super(RejectionFact, self).save(*args, **kwargs)

        if created:
            self.intimate_interested()

    def intimate_interested(self):
        cfg = Configuration.objects.get(application="ejud")
        deadline = int(cfg.get("deadlineAppeal", 10) or 10)

        for interested in self.lawsuit.interested.filter():
            if not self.diligences.filter(who=interested, who_type=1).exists():
                jd = JudicialDiligence(
                    part=self,
                    who=interested,
                    who_type=1,
                    deadline=deadline,
                    title="Apresentar Recurso",
                    observation="não foi preenchido nada",
                    delivery_status=1,
                )

                jd.with_manifestation = True
                jd.save()

    def sign_decision(self):
        if self.decided_by:
            raise Exception(
                "Já foi decidido por %s." % person_from_user(self.decided_by, False)
            )

        if not self.decision_text or self.decision_text == "":
            raise Exception("Aparentemente a decisão não foi preenchida.")

        if not self.in_decision_stage:
            raise Exception("Não é o momento de realizar esta decisão.")

        with transaction.atomic():
            self.decided_by = get_current_user()
            self.decided_at = datetime.now()
            self.decision_text_cache = self.decision_formated
            self.store_decision()

            if (
                self.manifestations.filter(signed_by=None).exists()
                or not self.manifestations.filter().exists()
            ):
                log.info(
                    "Como não houve a apresentação de nenhum recurso o procedimento será arquivado na promotoria."
                )
                execution_organ = self.lawsuit.location
                self.lawsuit.send_to(
                    to=execution_organ,
                    parecer_template="""Para arquivamento na promotoria.""",
                    finalizado=True,
                )
            elif int(self.decision_type == 1):
                log.info(
                    "Decidiu-se por Reconsiderar o Indeferimento de Noticia de Fato."
                )
                self._make_ordinace()
            else:
                log.info("Decidiu-se por Manter o Indeferimento de Noticia de Fato.")
                from judicial.council.models import DistributionRapporteur

                self._send_to_council()
                DistributionRapporteur(lawsuit=self.lawsuit, part_origin=self).save()

    def store_decision(self):
        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)
            if older.decided_at:
                raise Exception(
                    "A decisão encontra-se assinada, não é possível modifica-la."
                )

        if not hasattr(self, "decision_store"):
            setattr(self, "decision_store", True)

        self.save()

    def _make_ordinace(self):
        ordinace = Ordinace(lawsuit=self.lawsuit, type_ordinace=self.type_ordinace)

        ordinace.save()
        ordinace.in_rejection_fact.add(self)

    def _send_to_council(self):
        cfg = Configuration.objects.get(application="ejud")

        try:
            council = Lotacao.objects.get(pk=cfg.get("csmpLocation", None))
        except Lotacao.DoesNotExist:
            raise Exception(
                "Não consegui encontrar o destinho do Conselho Superior do Ministério Público."
            )
        else:
            log.debug(
                "Lotacao atual: %s", self.lawsuit.current_moviment().lotacao_destino
            )

            if (
                self.lawsuit.location.pk
                == self.lawsuit.current_moviment().lotacao_destino.pk
            ):
                log.info(
                    "Encaminhado a noticia de fato %s para %s",
                    self.lawsuit.origin.codigo,
                    council,
                )
                # self.lawsuit.deadline_cache = None
                self.lawsuit.remaining_days = None
                self.lawsuit.location = council
                self.lawsuit.save()
                self.lawsuit.send_to(
                    to=council,
                    parecer_template="""Para ser apreciado o indeferimento""",
                )
            else:
                raise Exception(
                    "Aparentemente este procedimento não esta mais em sua posse."
                )

    def imtimate_accused(self):
        cfg = Configuration.objects.get(application="ejud")

        for bloke in self.lawsuit.blokes.filter():
            log.info("Intimar para se manifestar %s", bloke.my_origin.bloke)
            jd = JudicialDiligence(
                part=self,
                who=bloke.my_origin.bloke,
                who_type=2,
                deadline=int(cfg.get("deadlineAppeal", 10) or 10),
                title="Convocar para apresentar argumentação",
                observation="""<p>Convocar %s para que seja apresentada argumentações a respeito da Noticia de Fato %s.</p>"""
                % (bloke.my_origin.bloke, self.lawsuit.origin.codigo),
                delivery_status=2,
            )

            jd.without_attached_documents = True
            jd.with_manifestation = True
            jd.save()

    @property
    def sign_part_authorized(self):
        if PartLawsuit.sign_part_authorized.fget(self):
            self.validate_current_location()

            if not self.despatch:
                raise Exception("Não foi inserido o texto do despacho.")

            if self.signed:
                raise Exception("Não posso assinar um documento já assinado.")

            return True
        else:
            return False

    def sign_part(self):
        with transaction.atomic():
            self.cache_rendered = self.rendered
            super(RejectionFact, self).sign_part()

            for diligence in self.diligences.exclude(who_type=2):
                diligence.change_state_diligence(
                    diligence.delivery_status, "aguardando-distribuicao"
                )
                diligence.save()

            # self.lawsuit.deadline_cache = None
            self.lawsuit.remaining_days = None
            self.lawsuit.save()

    @property
    def appeal_formated(self):
        try:
            tpl = loader.get_template("judicial/lawsuit/appeal_formated.html")

            execution_organ = self.lawsuit.location

            ctx = {
                "doc": self,
                "manifestation": self.manifestations.get(who_type=1),
                "execution_organ": execution_organ,
            }

            return tpl.render(ctx)
        except Exception:
            return ""

    @property
    def decision_formated(self):
        if not self.decision_text_cache:
            tpl = loader.get_template("judicial/lawsuit/rejectionfact/decision.html")

            execution_organ = self.lawsuit.location

            ctx = {"doc": self, "execution_organ": execution_organ}

            return tpl.render(ctx)
        else:
            return self.decision_text_cache

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-rejection-fact"

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(execution_organ=execution_organ, rejection=self)

        return rst


class BlokeDocument(AuditTimestampModel):
    bloke = models.ForeignKey(Bloke, related_name="documents", on_delete=models.PROTECT)
    rejection_fact = models.ForeignKey(
        RejectionFact, related_name="as_appeal_against", on_delete=models.PROTECT
    )
    created = models.DateTimeField(auto_now_add=True)
    appeal = models.TextField(null=True)
    appeal_deadline = models.DateTimeField(null=True)

    class Meta:
        unique_together = (("bloke", "rejection_fact"),)

    @property
    def cached_render(self):
        tpl = loader.get_template("judicial/lawsuit/bloke_document.html")
        return tpl.render({"doc": self})


class CommonRemittanceInternal(PartLawsuit):
    text = models.TextField(blank=True)
    department = models.ForeignKey(
        "rh.Lotacao", null=True, blank=True, on_delete=models.PROTECT
    )
    conflict = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def params(self):
        rst = PartLawsuit.params(self)
        rst.update(doc=self)

        return rst

    def triage_center(self):
        department = None
        try:
            conf = Configuration.objects.get(application="ejud")
            triage_center = conf.get(key="mainTriageCenter")
            department = Lotacao.objects.get(pk=triage_center)
        except Exception as e:
            log.exception(e)
        else:
            return department

    def office_presidence(self):
        department = None
        try:
            conf = Configuration.objects.get(application="ejud")
            office_presidence = conf.get(key="officePresident")
            department = Lotacao.objects.get(pk=office_presidence)
        except Exception as e:
            log.exception(e)
        else:
            return department

    def moviment_remittance(self):
        self.lawsuit.send_to(to=self.department, parecer_template=self.text)

    def is_conflict(self):
        return False

    @property
    def sign_part_authorized(self):
        if PartLawsuit.sign_part_authorized.fget(self):
            # if getattr(self, '_validate_text', True) and not self.text:
            #     raise Exception('Não foi inserido o texto das considerações.')

            if self.signed:
                raise Exception("Não posso assinar um documento já assinado.")

            return True
        else:
            return False

    @property
    def _deadline_days_for_type_lawsuit(self):
        type_map = {
            1: "deadlineFactNews",
            2: "deadlineCivilInvestigation",
            3: "deadlinePreparatoryProcedure",
            4: "deadlinePreparatoryCivilInvestigation",
            7: "deadlineAdministrativeProcedure",
            8: "deadlineRogatoryLetter",
            9: "deadlinePreparatoryProcedureElectoral",
            10: "deadlineAdministrativeManagement",
        }

        cfg = Configuration.get_or_create("ejud")

        triage_workplace = json.loads(cfg.get("triageCenter", "[]"))
        main_triage_center = int(cfg.get("mainTriageCenter", 0)) or None

        if not main_triage_center:
            raise Exception(
                "Não foi definido um centro de triagem principal. Favor ajustar definições no configurador do eJud."
            )

        triage_workplace.append(main_triage_center)

        if self.lawsuit.type_lawsuit == 1 and self.department.pk in triage_workplace:
            return int(cfg.get("deadlineTriage", 0) or 0)
        else:
            kind = type_map.get(self.lawsuit.type_lawsuit)
            return int(cfg.get(kind) or 0) if kind else None

    def sign_part(self):
        with transaction.atomic():

            super(CommonRemittanceInternal, self).sign_part()

            if self.conflict:
                self.lawsuit.send_to(
                    to=self.office_presidence(),
                    parecer_template="Para ser apreciado o conflito de atribuição",
                )
                self.lawsuit.location = self.office_presidence()
            else:
                self.lawsuit.send_to(to=self.department, parecer_template=self.text)
                self.lawsuit.location = self.department

            if self.department == self.triage_center():
                triage = Triage(lawsuit=self.lawsuit)
                triage.skip_validade_ownership = True
                triage.save()

            self.lawsuit.remaining_days = self._deadline_days_for_type_lawsuit
            self.lawsuit.save()

    def validate(self):
        if self.department and not self.department.allow_lawsuit:
            raise Exception(
                "Esse órgão não está habilitado para receber procedimentos."
            )

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-remittance-internal"

    @property
    def change_location_to(self):
        return self.department.orgaogeral_ptr

    def save(self, *args, **kwargs):
        # if getattr(self, '_validate_text', True) and not self.text:
        #     raise Exception('Preencha o campo Considerações!')
        if self.department and self.is_conflict() and not self.conflict:
            raise Exception(
                "Foi detectado o conflito de atribuição, marque o conflito de atribuição e justifique."
            )
        elif not self.department and self.conflict:
            self.department = self.office_presidence()
        elif not self.department and not self.conflict:
            self.conflict = False
            self.department = self.triage_center()
        self.validate()
        super(CommonRemittanceInternal, self).save(*args, **kwargs)


@type_part_lawsuit()
class RemittanceInternal(CommonRemittanceInternal):

    codename = "Encaminhamento a órgão interno"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)


@type_part_lawsuit()
class SpecialRemittanceInternal(CommonRemittanceInternal):

    codename = "Remessa Interna dos Autos Especial"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @property
    def sign_part_authorized(self):
        query = self.lawsuit.location.employee_exercise.filter(
            servidor__user=get_current_user()
        )

        if not query.exists():
            raise Exception("Este documento não pode ser assinado por você.")

        if not self.text:
            raise Exception("Não foi inserido o texto das considerações.")

        if self.signed:
            raise Exception("Não posso assinar um documento já assinado.")

        return True


@type_part_lawsuit()
class RemittanceExternal(PartLawsuit):
    organs = models.ManyToManyField(
        "rh.OrgaoGeral", related_name="in_remittance_external"
    )
    text = models.TextField(blank=True)

    codename = "Encaminhamento a órgão externo"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(doc=self, execution_organ=execution_organ)

        return rst

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-remittance-external"

    @property
    def sign_part_authorized(self):
        if PartLawsuit.sign_part_authorized.fget(self):
            # if not self.text:
            #     raise Exception('Não foi inserido o texto das considerações.')

            if self.signed:
                raise Exception("Não posso assinar um documento já assinado.")

            return True
        else:
            return False

    def sign_part(self):
        with transaction.atomic():
            super(RemittanceExternal, self).sign_part()

            destinations = [organ for organ in self.organs.filter()]
            destinations.append(self.lawsuit.location)

            self.lawsuit.external_locations.clear()
            for organ in destinations:
                self.lawsuit.external_locations.add(organ)

            self.lawsuit.send_to(
                to=[organ for organ in destinations],
                parecer_template="<p>Remetido para orgão externo.</p>",
                finalizado=True,
                force_location=self.lawsuit.location,
            )

    def save(self, *args, **kwargs):
        # if not self.text:
        #     raise Exception('Preencha o campo Considerações!')

        super(RemittanceExternal, self).save(*args, **kwargs)


@type_part_lawsuit()
class RemittanceItselfOrgan(PartLawsuit):
    text = models.TextField(blank=True)
    department = models.ForeignKey(
        "rh.Lotacao", null=True, blank=True, on_delete=models.PROTECT
    )

    codename = "Tramitação no Órgão"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-remittance-internal"

    @property
    def sign_part_authorized(self):
        if PartLawsuit.sign_part_authorized.fget(self):
            if not self.my_origin.department:
                raise Exception("Informe o departamento de destino.")

            if self.signed:
                raise Exception("Não posso assinar um documento já assinado.")

            return True
        else:
            return False

    def sign_part(self):
        with transaction.atomic():
            super(RemittanceItselfOrgan, self).sign_part()

            self.lawsuit.send_to(to=self.department, parecer_template=self.text)
            self.lawsuit.location = self.department
            self.lawsuit.save()

    @property
    def change_location_to(self):
        return self.department.orgaogeral_ptr

    def save(self, *args, **kwargs):
        log.debug(" *> department")
        log.debug(self.department)
        log.debug(" *> department")
        super(RemittanceItselfOrgan, self).save(*args, **kwargs)


@type_part_lawsuit()
class Archivement(PartLawsuit):
    despatch = models.TextField()

    codename = "Remessa ao Conselho - Deprecated"
    only_responsible_sign = True

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(doc=self, execution_organ=execution_organ)

        return rst

    def sign_part(self):
        with transaction.atomic():
            super(Archivement, self).sign_part()

            if self.lawsuit.type_lawsuit in (4, 7):
                # self.lawsuit.deadline_cache = None
                self.lawsuit.remaining_days = None
                self.lawsuit.closed_by = get_current_user()
                self.lawsuit.closed_at = datetime.now()
                self.lawsuit.save()
                self.lawsuit.send_to(to=self.lawsuit.location, finalizado=True)
            else:
                self._send_to_council()

                from judicial.council.models import DistributionRapporteur

                DistributionRapporteur(lawsuit=self.lawsuit, part_origin=self).save()
                log.info("Enviar ao Colégio de Procuradores...")

    def save(self, *args, **kwargs):
        super(Archivement, self).save(*args, **kwargs)


@type_part_lawsuit()
class Judicialization(PartLawsuit):
    code = models.CharField(max_length=100)
    court = models.CharField(max_length=200)
    observation = models.TextField(null=True)

    codename = "Certidão de Judicialização"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def sign_part(self):
        with transaction.atomic():
            super(Judicialization, self).sign_part()

            self.lawsuit.send_to(
                to=self.lawsuit.location,
                parecer_template=self.cache_rendered,
                finalizado=True,
            )

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(doc=self, execution_organ=execution_organ)

        return rst


class DiligenceTemplate(Message):

    class Meta:
        pass
        # managed = False

    def save(self, *args, **kwargs):
        self.type = "EJUD"
        super(DiligenceTemplate, self).save(*args, **kwargs)

    @classmethod
    def formatted_message(klass, msg_or_mid, **kargs):
        params = {}
        try:
            if isinstance(msg_or_mid, klass):
                msg = msg_or_mid
            else:
                msg = klass.objects.get(mid=msg_or_mid)
        except klass.DoesNotExist:
            raise Exception("A template %s não existe na base de dados!" % msg_or_mid)
        else:
            for k in kargs:
                params[k] = "%s" % kargs[k]
            return "%s" % msg.formated(eval(str(params)))


@type_part_lawsuit()
class ConnectionLawsuit(PartLawsuit):
    text = models.TextField(blank=True)
    lawsuit_connected = models.ForeignKey(
        OutCourtLawsuit, related_name="connections", on_delete=models.PROTECT
    )
    unconnected_by = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    unconnected_at = models.DateTimeField(null=True, blank=True)

    codename = "Anexação"

    @property
    def title(self):
        return f"{self.codename} do procedimento {self.lawsuit_connected.cache_number}"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-rejection-link-other"

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(execution_organ=execution_organ, doc=self)

        return rst

    def move_to_end(self):
        size = (
            self.lawsuit_connected.all_documents.order_by("page_number")
            .last()
            .page_number
        )

        for document in self.lawsuit.all_documents.order_by("-page_number"):
            log.debug(
                "move %s from %d to %d",
                document,
                document.page_number,
                document.page_number + size,
            )
            self.lawsuit.all_documents.filter(pk=document.pk).update(
                page_number=(document.page_number + size)
            )

    def reorder_pages(self, lawsuit, page_number):
        for document in lawsuit.all_own_signed_documents.order_by("-page_number"):
            PartLawsuit.objects.filter(pk=document.pk).update(
                page_number=(document.page_number + page_number)
            )

        if lawsuit.shared_parts.exists():
            self.reorder_pages(lawsuit.shared_parts.first().lawsuit, page_number)

    def move_documents_of_connected(self):
        log.debug("start page number %d", self.page_number)

        self.reorder_pages(self.lawsuit_connected, self.page_number)

        for document in self.lawsuit_connected.all_documents.exclude(
            signed_by=None
        ).order_by("-page_number"):
            document.shared_with_lawsuit.add(self.lawsuit)

    def sign_part(self):
        with transaction.atomic():
            super(ConnectionLawsuit, self).sign_part()
            self.move_documents_of_connected()

            self.lawsuit_connected.attached_lawsuit = self.lawsuit
            self.lawsuit_connected.save()
            self.lawsuit_connected.finish_requestcollaborations()

            Interested.objects.bulk_create(
                [
                    Interested(
                        person=person,
                        direct=True,
                        lawsuit=self.lawsuit,
                        created_by=get_current_user(),
                        modified_by=get_current_user(),
                        created_at=datetime.now(),
                        modified_at=datetime.now(),
                    )
                    for person in self.lawsuit_connected.interested.filter()
                ]
            )

            for bloke in self.lawsuit_connected.blokes.filter():
                nbloke = bloke.my_origin
                nbloke.pk = None
                nbloke.lawsuit = self.lawsuit
                nbloke.save()

            for part in self.lawsuit_connected._all_signed_documents(False):
                EventControl(
                    lawsuit=self.lawsuit,
                    part=part,
                    number_control=self.lawsuit.next_number_control(),
                ).save()

    @property
    def icons_status(self):
        if self.read_only:
            return [{"iconCls": "icon-judicial icon-ejud-signed", "title": "Assinado"}]
        else:
            return [
                {"iconCls": "icon-core icon-core-info", "title": "Não foi asssinado"}
            ]

    @property
    def cover_lawsuit_connected(self):
        pages = []

        if self.lawsuit_connected:
            pages.append({"at": self.signed_at, "page": self.lawsuit_connected.cover})

        return pages

    def _all_extra_pages_complete(self):
        return self.cover_lawsuit_connected

    @property
    def connected(self):
        return self.lawsuit_connected.location

    def validate(self):
        if not self.lawsuit.location.pk == self.connected.pk:
            raise Exception(
                "Não é possível realizar a conexão entre procedimentos que estejam em promotorias diferentes."
            )

    def save(self, *args, **kwargs):
        self.validate()
        super(ConnectionLawsuit, self).save(*args, **kwargs)


@type_part_lawsuit()
class DilationPeriod(PartLawsuit):
    older_deadline = models.DateTimeField(null=True, blank=True)
    justification = models.TextField(blank=True)
    type_lawsuit = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_LAWSUIT"),
        verbose_name="Tipo do Procedimento",
        null=True,
        blank=True,
    )
    days = models.IntegerField(null=True, blank=True)

    codename = "Dilação de Prazo"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-dilation-period"

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(execution_organ=execution_organ, doc=self)

        return rst

    def _validate_check_can_dilate(self):
        label_map = {
            1: "dilationMaxFactNews",
            2: "dilationMaxCivilInvestigation",
            3: "dilationMaxPreparatoryProcedure",
            4: "dilationMaxPreparatoryCivilInvestigation",
            7: "dilationMaxAdministrativeProcedure",
            8: "dilationRogatoryLetter",
            9: "deadlinePreparatoryProcedureElectoral",
            10: "deadlineAdministrativeManagement",
        }

        cfg = Configuration.get_or_create("ejud")
        triage_workplace = json.loads(cfg.get("triageCenter", "[]"))
        main_triage_center = int(cfg.get("mainTriageCenter", 0)) or None

        if not main_triage_center:
            raise Exception(
                "Não foi definido um centro de triagem principal. Favor ajustar definições no configurador do eJud."
            )

        triage_workplace.append(main_triage_center)

        if self.lawsuit.type_lawsuit == 1 and (
            self.lawsuit.current_moviment().lotacao_destino
            and self.lawsuit.current_moviment().lotacao_destino.pk in triage_workplace
        ):
            max_number = cfg.get("dilationMaxTriage", None)
        else:
            max_number = cfg.get(label_map.get(self.lawsuit.type_lawsuit), None)

        if not max_number:
            raise Exception(
                "Não é permitido pedir dilação de prazo para %s."
                % self.lawsuit.get_type_lawsuit_display()
            )
        else:
            max_number = int(max_number or 0)
            number = (
                self.__class__.objects.exclude(pk=self.pk)
                .filter(
                    lawsuit=self.lawsuit,
                    type_lawsuit=self.lawsuit.type_lawsuit,
                    signed_by__isnull=False,
                    create_location=self.create_location,
                )
                .count()
            )

            log.debug([max_number, number])

            if max_number > 0 and number >= max_number:
                raise Exception(
                    "Procedimentos do tipo <b>%s</b> só podem ter o prazo dilatado <b>%d</b> %s e já teve <b>%d</b>."
                    % (
                        self.lawsuit.get_type_lawsuit_display(),
                        max_number,
                        "vez" if max_number < 2 else "vezes",
                        number,
                    )
                )

    @property
    def _deadline_days_for_type_lawsuit(self):
        type_map = {
            1: "deadlineFactNews",
            2: "deadlineCivilInvestigation",
            3: "deadlinePreparatoryProcedure",
            4: "deadlinePreparatoryCivilInvestigation",
            7: "deadlineAdministrativeProcedure",
            8: "deadlineRogatoryLetter",
            9: "deadlinePreparatoryProcedureElectoral",
            10: "deadlineAdministrativeManagement",
        }

        cfg = Configuration.get_or_create("ejud")

        triage_workplace = json.loads(cfg.get("triageCenter", "[]"))
        main_triage_center = int(cfg.get("mainTriageCenter", 0)) or None

        if not main_triage_center:
            raise Exception(
                "Não foi definido um centro de triagem principal. Favor ajustar definições no configurador do eJud."
            )

        triage_workplace.append(main_triage_center)

        current_movement = self.lawsuit.current_moviment()
        log.info(" -> (%s)", current_movement.lotacao_destino)

        if self.lawsuit.type_lawsuit == 1 and (
            current_movement.lotacao_destino
            and current_movement.lotacao_destino.pk in triage_workplace
        ):
            return int(cfg.get("deadlineTriage", 0) or 0)
        elif self.lawsuit.type_lawsuit == 1:
            """
            FIXME adicionar uma configuração para definir o tempo de dilação de parazo para Noticia de Fato.
            """
            return 90
        else:
            return int(cfg.get(type_map.get(self.lawsuit.type_lawsuit)) or 0)

    @property
    def begin_date_permited(self):
        days = int(self._deadline_days_for_type_lawsuit * 0.3)
        return self.lawsuit.deadline_date - timedelta(days=days if days < 30 else 30)

    def sign_part(self):
        with transaction.atomic():
            log.info(
                "Pedido de dilação de prazo para o procedimento %s do tipo %s",
                self.lawsuit.cache_number,
                self.lawsuit.get_type_lawsuit_display(),
            )

            if self.begin_date_permited > date.today():
                raise Exception(
                    "Só será permitido pedir dilação de prazo na data %s."
                    % DateUtils.date_to_str(self.begin_date_permited)
                )

            self.days = self._deadline_days_for_type_lawsuit
            self._validate_check_can_dilate()

            self.older_deadline = self.lawsuit.deadline_date
            self.type_lawsuit = self.lawsuit.type_lawsuit
            self.save()

            super(DilationPeriod, self).sign_part()

            self.lawsuit.remaining_days += self.days
            self.lawsuit.save()

            log.info("Novo periodo %s", self.lawsuit.deadline_date)
            log.info("Dilatar em %d dias", self.days)
            log.info("Novo prazo %s", self.lawsuit.deadline)

    @classmethod
    def extend_deadline(cls, lawsuit=None):
        with transaction.atomic():
            dilation = DilationPeriod(lawsuit=lawsuit)
            dilation.save()

            dilation.sign_part()


@type_part_lawsuit()
class AssessmentNoticeOffice(InitialPartlawsuit, PartLawsuit):
    notice_office_type = models.SmallIntegerField(
        choices=(
            (1, "Termo de Declaração"),
            (2, "Noticia de Fato"),
            (3, "Carta Precatória"),
            (4, "Procedimento de Gestão Administrativa"),
        )
    )
    interested = models.ForeignKey(
        "rh.Pessoa",
        related_name="in_assessment_notice_office",
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    at_where = models.ForeignKey(
        "rh.Localidade", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    main_matter = models.ForeignKey(
        LegalMatter, null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    is_criminal = models.BooleanField(default=False)
    only_notice = models.BooleanField(default=False)
    is_anonymus = models.BooleanField(default=False)
    location = models.ForeignKey(
        Lotacao,
        related_name="has_assessment_notice_office",
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    notice_title = models.CharField(max_length=200)
    notice = models.TextField()
    annotation = models.TextField(blank=True)
    protocol_origin = models.ForeignKey(
        Protocolo, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    movement_cache_rendered = models.TextField(blank=True, null=True)
    other_matters = models.ManyToManyField(
        LegalMatter, related_name="in_assessment_notice_office"
    )

    allow_instated = True

    allowed_in_instauration = True

    @property
    def codename(self):
        return self.get_notice_office_type_display()

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @property
    def lawsuit_title(self):
        return self.notice_title

    def _lawsuit_type(self):
        return 1 if self.signed_by else 6

    def _calculate_deadline_date(self):
        cfg = Configuration.get_or_create("ejud")

        return int(cfg.get("deadlineAssessmentNoticeOffice", 7) or 0)

    @property
    def title(self):
        return self.get_notice_office_type_display()

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-denunciation"

    def _validate_user(self):
        if self.is_anonymus and (
            not getattr(self, "interested", None)
            or not getattr(self.interested, "anonymousperson", None)
        ):
            log.info("Criar uma pessoa anonima")
            from web.models import TokenWebUser

            user = TokenWebUser()
            user.save()
            self.interested = user.person
            self.annotation = "".join(
                [
                    "<p>",
                    "    Seu atendimento foi registrado e poderá ser acompanhado pelo Portal de Atendimento ao Cidadão, ",
                    "    para isto você necessitará das seguintes credenciais:",
                    "</p>",
                    "<ul>",
                    "    <li>Token de acesso:<strong> %(token)s</strong></li>",
                    "</ul>",
                    "<p>",
                    "    Como medida de segurança, recomendamos que seja alterado com maior urgência esta senha, para isto ",
                    '    acesse o <a href="#">Portal de Atendimento ao Cidadão</a>.',
                    "</p>",
                ]
            ) % {
                "token": user.token,
            }
        elif self.interested and not getattr(self.interested, "web_user", False):
            log.info("Cria usuário para acessar web")
            from web.models import RegularWebUser

            user = RegularWebUser(
                person=self.interested,
                username=RegularWebUser.sugest_username(
                    (
                        "".join(
                            [
                                self.interested.nome.split(" ")[0],
                                self.interested.nome.split(" ")[-1],
                            ]
                        )
                    ).lower()
                ),
                password_expires=datetime.now(),
            )
            rnd_passowrd = RegularWebUser.sugest_password()
            user.set_password(rnd_passowrd)
            user.save()

            self.annotation = "".join(
                [
                    "<p>",
                    "    Seu atendimento foi registrado e poderá ser acompanhado pelo Portal de Atendimento ao Cidadão, ",
                    "    para isto você necessitará das seguintes credenciais:",
                    "</p>",
                    "<ul>",
                    "    <li>Nome do usuário:<strong> %(username)s</strong></li>",
                    "    <li>Senha: <strong>%(passwd)s</strong></li>",
                    "</ul>",
                    "<p>",
                    "    Como medida de segurança, recomendamos que seja alterado com maior urgência esta senha, para isto ",
                    '    acesse o <a href="#">Portal de Atendimento ao Cidadão</a>.',
                    "</p>",
                ]
            ) % {"username": user.username, "passwd": rnd_passowrd}
        else:
            log.info("tudo certo!!!")

    def validate_current_location(self):
        try:
            current_moviment = self.lawsuit.current_moviment()
            user = get_current_user()
            servidor = employee_from_user(user)
        except Servidor.DoesNotExist:
            raise Exception(
                "Um servidor que não esta ativo não pode assinar documentos."
            )
        except Exception as e:
            raise e
        else:
            log.info(
                "Movimentação corrente para: %s", current_moviment.lotacao_destino.pk
            )
            log.info("Usuário: %s", user)
            log.info("Servidor: %s", servidor)
            log.info("Locais de trabalho: %s", [l.pk for l in servidor.work_locations])

            if not self.lawsuit.is_acting:
                raise Exception("O documento não esta na posse do usuário.")

        return True

    def validate_ownership(self):
        if not self.lawsuit.is_acting:
            raise Exception(
                "Você não pode modificar um procedimento que não esta mais em sua posse."
            )

    def validate_interested(self):
        if not getattr(self, "interested", None):
            raise Exception("É necessário indicar um interessado.")

    @property
    def movement_render(self):
        if self.protocol_origin:
            data = [
                loader.get_template("judicial/movement_protocol.html").render(
                    {
                        "protocol": self.protocol_origin,
                    }
                )
            ]
            return "".join(data)
        else:
            return None

    @property
    def extra_pages_protocol(self):
        pages = []

        if self.can_read:
            pages.append({"at": self.signed_at, "page": self.movement_cache_rendered})
        return pages

    def _all_extra_pages_complete(self):
        pages = super(AssessmentNoticeOffice, self)._all_extra_pages_complete()
        if self.protocol_origin:
            pages += self.extra_pages_protocol

        return pages

    def _create_grant_confidential_access(self):
        grant = GrantConfidentialAccess()
        grant.apply_in = 2
        grant.location = self.create_location
        grant.lawsuit = self.lawsuit
        grant.save()
        grant.add_part(self)
        grant.by_confidential_protocol = True
        grant.sign_part()

    @property
    def is_protocol_secret(self):
        try:
            control = ProtocolControl.objects.get(document=self.protocol_origin)
            return control.is_secret
        except ProtocolControl.DoesNotExist as e:
            log.debug("Protocolo não tem controle associado.")
            return False

    def save(self, *args, **kwags):
        created = False

        with transaction.atomic():
            self._validate_user()
            self.validate_interested()
            if not self.pk:
                self.lawsuit = self._create_lawsuit(self.protocol_origin)
                created = True
            else:
                self.lawsuit.title = self.notice_title
                self.lawsuit.save()

            self.movement_cache_rendered = self.movement_render

        super(AssessmentNoticeOffice, self).save(*args, **kwags)

        if created:
            Interested(lawsuit=self.lawsuit, person=self.interested, direct=True).save()
        else:
            query = Interested.objects.filter(lawsuit=self.lawsuit)
            query.update(direct=False)

            if query.filter(person=self.interested).exists():
                query.filter(person=self.interested).update(direct=True)
            else:
                Interested(
                    lawsuit=self.lawsuit, person=self.interested, direct=True
                ).save()

        if created and self.protocol_origin:
            for attachment in self.protocol_origin.attachments.filter():
                Attached(
                    attached_document=self,
                    title=attachment.title,
                    file_descriptor=attachment.attach,
                ).save()

    def sign_part(self):
        with transaction.atomic():

            if not self.acting_zone:
                raise Exception("É necessário informar a Área de Atuação")

            if not self.is_instanted:
                log.info("gerando numero do procedimento...")
                self.lawsuit.year = date.today().year
                self.lawsuit.number_lawsuit = self.lawsuit.next_number(
                    self.lawsuit.year
                )

            cfg = Configuration.get_or_create("ejud")

            if self.notice_office_type == 3:
                self.lawsuit.type_lawsuit = 8
                self.lawsuit.remaining_days = int(
                    cfg.get("deadlineRogatoryLetter", 0) or 0
                )
            elif self.notice_office_type == 4:
                self.lawsuit.type_lawsuit = 10
                self.lawsuit.remaining_days = int(
                    cfg.get("deadlineAdministrativeManagement", 0) or 0
                )
            else:
                self.lawsuit.type_lawsuit = 1
                self.lawsuit.remaining_days = int(cfg.get("deadlineFactNews", 0) or 0)

            if not self.main_matter:
                raise Exception("É necessário informar o Assunto principal")

            self.lawsuit.main_matter = self.main_matter

            LawsuitMatter.register_others_matters(
                lawsuit=self.lawsuit, matters=[m for m in self.other_matters.filter()]
            )

            self.lawsuit.city_locations.add(self.at_where)
            self.lawsuit.save()

            LawsuitMatter.register_principal_matter(
                lawsuit=self.lawsuit,
                matter=self.main_matter,
            )

            super(AssessmentNoticeOffice, self).sign_part()

            if self.is_protocol_secret:
                self._create_grant_confidential_access()

            self.dispatch_comunication(subject="Comunicar %s" % self.title)

            # FIXME isto deve ser reescrito após implementação da edicação compartilhada de documento.
            current_moviment = None
            if self.lawsuit.origin.movimentacoes.filter(passo__gt=0).exists():
                current_moviment = self.lawsuit.current_moviment()
            else:
                current_moviment = self.lawsuit.origin.movimentacoes.last()

            old_fn = current_moviment.validate_possession_for_do_send

            def empty_fn(*args, **kwargs):
                pass

            current_moviment.validate_possession_for_do_send = empty_fn
            current_moviment.with_workflow = True

            self.lawsuit.send_to(
                to=self.lawsuit.location,
                force_current=current_moviment,
                parecer_template="<p>Para este protocolo foi gerado o procedimento %s.</p>"
                % self.lawsuit.cache_number,
            )
            current_moviment.validate_possession_for_do_send = old_fn

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(
            execution_organ=execution_organ, doc=self, protocol=self.lawsuit.origin
        )

        return rst


@type_part_lawsuit()
class PreInvestigationFact(PartLawsuit):
    justify = models.TextField()

    codename = "Investigação preliminar dos Fatos"
    only_responsible_sign = True

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(execution_organ=execution_organ, doc=self)

        return rst

    def sign_part(self):
        with transaction.atomic():
            super(PreInvestigationFact, self).sign_part()
            for diligence in self.diligences.filter():
                diligence.change_state_diligence(
                    diligence.delivery_status, "aguardando-distribuicao"
                )
                diligence.without_attached_documents = True
                diligence.with_manifestation = True
                diligence.save()

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-denunciation"

    def save(self, *args, **kwags):
        if self.lawsuit.type_lawsuit != 1 or False:
            raise Exception(
                "Este tipo de documento só pode ser proposto para Noticia de Fato Criminal"
            )
        super(PreInvestigationFact, self).save(*args, **kwags)


class DismembermentProcessMixin(object):

    codename = "Desmembramento de Procedimento"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    def delivery(self, change_title, matters, main_matter):
        lawsuit = OutCourtLawsuit(
            title=change_title,
            location=self.lawsuit.location,
            year=date.today().year,
            origin=self.lawsuit.origin,
            # deadline_cache=self.lawsuit.deadline_cache,
            remaining_days=self.lawsuit.remaining_days,
            type_lawsuit=self.lawsuit.type_lawsuit,
            main_matter=main_matter,
        )
        lawsuit.number_lawsuit = lawsuit.next_number(lawsuit.year)
        lawsuit.save()

        LawsuitMatter.register_principal_matter(lawsuit=lawsuit, matter=main_matter)

        LawsuitMatter.register_others_matters(
            lawsuit=lawsuit, matters=[m for m in matters.filter()]
        )

        for doc in self.lawsuit.all_signed_documents.filter():
            doc.my_origin.shared_with_lawsuit.add(lawsuit)

        lawsuit.send_to([lawsuit.location, lawsuit.location], "Para ser desmembrado.")

        return lawsuit


@type_part_lawsuit()
class DismembermentMultiProcess(DismembermentProcessMixin, PartLawsuit):

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-devolution-recommendation"

    def sign_part(self):
        with transaction.atomic():
            chunks = []
            if not self.chunks.exists():
                raise Exception(
                    "É necessário definir novo(s) título(s) para o(s) novo(s) procedimento(s)."
                )

            for chunk in self.chunks.filter():
                chunk.generated_lawsuit = self.delivery(
                    chunk.change_title, chunk.matters, chunk.main_matter
                )
                chunk.save()
                chunks.append(chunk)
            super(DismembermentMultiProcess, self).sign_part()

            for chunk in chunks:
                self.shared_with_lawsuit.add(chunk.generated_lawsuit)

                lawsuit = chunk.generated_lawsuit
                for part in lawsuit.all_signed_documents.filter():
                    EventControl.objects.create(
                        lawsuit=lawsuit,
                        part=part,
                        number_control=EventControl.number_control_of(
                            self.lawsuit, part
                        ),
                    )


class DismembermentMultiProcessChunk(AuditTimestampModel):
    change_title = models.CharField(max_length=255, blank=True)
    matters = models.ManyToManyField(
        LegalMatter, related_name="in_desmemberment_processes_chunk"
    )
    dismemberment = models.ForeignKey(
        DismembermentMultiProcess, related_name="chunks", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    generated_lawsuit = models.ForeignKey(
        OutCourtLawsuit,
        related_name="in_dismemberment_process_chunck",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    main_matter = models.ForeignKey(
        LegalMatter, related_name="+", blank=True, null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["change_title"]

    def __str__(self):
        return self.change_title

    def delete(self, *args, **kwargs):
        if self.dismemberment.read_only:
            raise Exception(
                "Não posso modificar um desmembramento que já foi assinado."
            )
        super(DismembermentMultiProcessChunk, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.dismemberment.read_only:
            raise Exception(
                "Não posso modificar um desmembramento que já foi assinado."
            )

        if not self.change_title:
            self.change_title = self.dismemberment.lawsuit.title

        created = not self.pk

        if not self.main_matter:
            self.main_matter = LawsuitMatter.get_principal_matter(
                lawsuit=self.dismemberment.lawsuit
            )

        super(DismembermentMultiProcessChunk, self).save(*args, **kwargs)

        if created:
            for matter in LawsuitMatter.get_others_matters(
                lawsuit=self.dismemberment.lawsuit
            ):
                self.matters.add(matter)


@type_part_lawsuit()
class DismembermentProcess(DismembermentProcessMixin, PartLawsuit):
    change_title = models.CharField(max_length=255, blank=True)
    matters = models.ManyToManyField(
        LegalMatter, related_name="in_desmemberment_processes"
    )
    justification = models.TextField()

    codename = "Desmembramento de Procedimento (Deprecated)"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-devolution-recommendation"

    def sign_part(self):
        with transaction.atomic():
            super(DismembermentProcess, self).sign_part()
            self.delivery(self.change_title, self.matters)

    @property
    def sign_part_authorized(self):
        if PartLawsuit.sign_part_authorized.fget(self):
            if not self.justification:
                raise Exception("Não foi inserido o texto na justificativa.")

            if self.signed:
                raise Exception("Não posso assinar um documento já assinado.")

            return True
        else:
            return False

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location
        attachments = self.attaches.filter()
        signed_by = person_from_user(self.signed_by)

        rst.update(
            execution_organ=execution_organ,
            attachments=attachments,
            signed_by=signed_by,
            sign={
                "organ": execution_organ,
                "moment_at": self.modified_at,
                "person": person_from_user(self.signed_by),
            },
            doc=self,
        )

        return rst

    def save(self, *args, **kwargs):
        if not self.change_title:
            self.change_title = self.lawsuit.title

        if not self.pk:
            if (
                self.lawsuit.parts.filter(
                    type_part=self._meta.model_name, signed_by=None
                ).count()
                > 0
            ):
                raise Exception("Há uma Devolução com Recomendação em aberto.")

        super(DismembermentProcess, self).save(*args, **kwargs)

        for m in self.lawsuit.matters.filter():
            if m not in self.matters.filter():
                self.matters.add(m)


@type_part_lawsuit()
class AdditionalDiligence(PartLawsuit):
    dispatch_title = models.CharField(max_length=300, null=True, blank=True)
    justification = models.TextField(null=True, blank=True)

    codename = "Diligências"

    @property
    def title(self):
        return (
            f"{self.codename} - {self.dispatch_title}"
            if self.dispatch_title
            else self.codename
        )

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + list(
            PartLawsuit.sign_permissions.fget(self)
        )

    def sign_part(self):
        with transaction.atomic():
            if not self.diligences.exists():
                raise Exception("Você deve pedir ao menos uma diligencia.")

            super(AdditionalDiligence, self).sign_part()

            for diligence in self.diligences.filter():
                diligence.change_state_diligence(
                    diligence.delivery_status, "aguardando-distribuicao"
                )
                diligence.without_attached_documents = True
                diligence.with_manifestation = True
                diligence.save()

    def extra_pages_of_diligences_deliveryattempt(self, diligence=None):
        pages = []
        if self.can_read:
            for delivery in diligence.deliveryattempt_set.filter():
                pages.append({"at": delivery.exit_date, "page": delivery.rendered})
        return pages

    def render_attaches_of_diligence(self, diligence):
        pages = []
        for attaches in diligence.attaches.filter():
            pages += [
                {
                    "page": page.get("page"),
                    "at": (
                        diligence.signed_at if diligence.signed_at else datetime.now()
                    ),
                }
                for page in attaches.extract_pages()
            ]
        return pages

    @property
    def extra_pages_of_diligences(self):
        pages = []

        if self.can_read:
            query = self.diligences.all()

            if not self.justification and self.diligences.exists():
                diligence = self.diligences.first()
                query = query.exclude(pk=diligence.pk)

                pages += self.render_attaches_of_diligence(diligence)
                pages += self.extra_pages_of_diligences_deliveryattempt(
                    diligence=self.diligences.first()
                )

            for diligence in query.order_by("signed_at"):
                pages.append(
                    {
                        "at": (
                            diligence.signed_at
                            if diligence.signed_at
                            else datetime.now()
                        ),
                        "page": diligence.rendered,
                    }
                )

                pages += self.render_attaches_of_diligence(diligence)
                pages += self.extra_pages_of_diligences_deliveryattempt(
                    diligence=diligence
                )

        return pages

    @property
    def rendered(self):
        if self.justification:
            return PartLawsuit.rendered.fget(self)
        elif self.diligences.exists():
            return self.diligences.first().rendered
        else:
            return ""

    @property
    def number_pages(self):
        qt = 0
        for at in self.attaches.filter():
            qt += at.number_pages if at.number_pages else 0

        for mn in self.manifestations.filter():
            qt += mn.number_pages

        for dl in self.diligences.filter():
            qt += dl.number_pages

        return qt

    def save(self, *args, **kwags):
        super(AdditionalDiligence, self).save(*args, **kwags)


@type_part_lawsuit()
class Recomendation(PartLawsuit):
    dispatch_title = models.CharField(max_length=300, null=True, blank=True)
    content = models.TextField()
    deadline = models.IntegerField(verbose_name="Prazo", null=True)
    deadline_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "DEADLINE_TYPE"),
        default=1,
        verbose_name="Tipo do Prazo",
    )
    finished_by = models.ForeignKey(
        "auth.user",
        related_name="has_finisher_recommendation",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    finished_at = models.DateTimeField(null=True, blank=True)
    remaining_days = models.SmallIntegerField(null=True, blank=True)

    codename = "Recomendação"
    only_responsible_sign = True

    @property
    def title(self):
        return (
            f"{self.codename} - {self.dispatch_title}"
            if self.dispatch_title
            else self.codename
        )

    def __str__(self):
        return "Recomendação em {}".format(self.lawsuit.cache_number)

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @property
    def is_finished(self):
        return True if self.finished_by else False

    @property
    def is_deadline_type_day(self):
        return int(self.deadline_type or 0) == 1

    @property
    def is_deadline_type_month(self):
        return int(self.deadline_type or 0) == 2

    @property
    def is_deadline_type_year(self):
        return int(self.deadline_type or 0) == 3

    @property
    def is_signed(self):
        return True if self.signed_by else False

    def calculate_remaining_days(self):
        deadline = 0
        days_relative = 0
        if self.is_deadline_type_day:
            days_relative = relativedelta(days=self.deadline)
            deadline = (datetime.now() + days_relative) - datetime.now()
        elif self.is_deadline_type_month:
            days_relative = relativedelta(months=self.deadline)
            deadline = (datetime.now() + days_relative) - datetime.now()
        elif self.is_deadline_type_year:
            days_relative = relativedelta(years=self.deadline)
            deadline = (datetime.now() + days_relative) - datetime.now()

        return deadline.days

    def sign_part(self):
        if self.is_signed:
            raise Exception("Esta recomendação já foi assinada.")

        with transaction.atomic():
            self.remaining_days = self.calculate_remaining_days()
            self.save()

            super(Recomendation, self).sign_part()

            for scientify_workplace in self.sciences.all():
                scientify_workplace.dispatch()

    def fulfilled(self):
        if self.is_finished:
            raise Exception("Este recomendação já foi cumprida.")

        if not self.is_signed:
            raise Exception("É necessário assinar a recomendação antes de finalizá-la.")

        self.finished_by = get_current_user()
        self.finished_at = datetime.now()
        self.skip_read_only_validate = True
        self.save()

    @classmethod
    def queryset_recomendation_to_decrement_day(cls, location=None, to_date=None):
        executed_today = DeadlineLog.queryset_recomendation_executed_to_date(
            to_date=to_date
        )
        return cls.objects.filter(
            Q(
                Q(signed_by__isnull=False)
                & Q(finished_by__isnull=True)
                & Q(remaining_days__isnull=False)
                & Q(lawsuit__location__localidade=location)
            )
        ).exclude(pk__in=executed_today)

    @classmethod
    def queryset_recomendation_to_weekend_decrement_day(
        cls, location=None, to_date=None
    ):
        return cls.queryset_recomendation_to_decrement_day(
            location=location, to_date=to_date
        ).exclude(Q(Q(remaining_days=1)))

    @classmethod
    def decrement_remaining_days(cls, query_set=[], dry_run=True):
        for recomendation in query_set:
            if not dry_run and recomendation.remaining_days is not None:

                DeadlineLog.register(
                    recomendation=recomendation,
                    days=recomendation.remaining_days,
                    observation="Inserido pelo sistema",
                )

                days = recomendation.remaining_days - 1
                cls.objects.filter(pk=recomendation.pk).update(remaining_days=days)


@type_part_lawsuit()
class Dispatch(PartLawsuit):
    dispatch_title = models.CharField(max_length=300, null=True, blank=True)
    content = models.TextField()

    """
    Note: iniciamente este documento foi criado como Despacho
    """
    codename = "Movimentação Geral - Deprecated"

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @property
    def title(self):
        return self.dispatch_title if self.dispatch_title else self.codename


class ScientifyWorkplace(AuditTimestampModel):
    part = models.ForeignKey(
        PartLawsuit, related_name="sciences", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    location = models.ForeignKey(
        Lotacao, related_name="in_sciences", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    protocol = models.ForeignKey(
        Protocolo,
        related_name="as_science",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    movement = models.ForeignKey(
        Movimentacao,
        related_name="as_science",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    content = models.TextField(null=True, blank=True)

    AUDITABLE = {"fields": ("location", "content")}

    def save(self, *args, **kwags):
        log.debug(self.old_fields)
        if self.pk and self.protocol and "location" in self.old_fields:
            raise Exception(
                "Não posso modificar o destinatário depois que o comunicado já foi enviado."
            )

        if self.pk and self.protocol and "content" in self.old_fields:
            raise Exception(
                "Não posso modificar o conteúdo do despacho despois que foi enviado o comunicado."
            )

        super(ScientifyWorkplace, self).save(*args, **kwags)

    @property
    def received_by(self):
        """
        Esta propriedade busca a informação de quem recebeu a comunicação.
        """
        if self.movement and self.movement.servidor_destino:
            return self.movement.servidor_destino.pessoa_fisica
        return None

    @property
    def received_at(self):
        """
        Esta propriedade busca a informação de quando a comunicação foi recebida.
        """
        if self.movement:
            return self.movement.data_recebimento
        return None

    def dispatch(self):
        """
        Este metodo é responsavel por entregar a comunicação ao departamento indicado em location.
        """
        if self.protocol:
            raise Exception(
                "Este documento já foi encaminhado e não pode ser encaminhado novamente."
            )

        if not self.part.signed_by:
            raise Exception(
                "Este recurso só pode ser usado após o promotor ter assinado o documento."
            )

        content = [
            re.sub(
                r"<!-- begin header -->.*<!-- end header -->",
                "",
                self.part.rendered.replace("\n", ""),
            )
        ]

        protocol = Protocolo.docketing(
            subject="Comunicar - %s" % str(self.part),
            document_type=TipoDocumento.objects.get(pk=51),
            interested=person_from_user(get_current_user()),
            home_court=self.part.lawsuit.location,
            content="".join(content),
        )

        current = Movimentacao.inbox_queryset().get(protocolo=protocol)

        current.do_send(
            location_destination=self.location.pk,
            employee_origin=employee_from_user(get_current_user()),
            advice=self.content,
            physical=False,
            opinion=True,
        )

        self.protocol = protocol
        self.movement = current.derivative_for.get(lotacao_destino=self.location)
        self.save()


class _SyncInterested:

    def sync_interesteds(self):
        query = Interested.objects.filter(lawsuit=self.lawsuit)

        if (
            query.filter(direct=True).exists()
            and not query.filter(direct=True)
            .filter(person=self.major_interested)
            .exists()
        ):
            Protocolo.objects.filter(pk=self.lawsuit.origin.pk).update(
                interessado=self.major_interested
            )
            Interested.objects.filter(lawsuit=self.lawsuit, direct=True).update(
                direct=False
            )
            Interested.objects.filter(
                person=self.major_interested, lawsuit=self.lawsuit
            ).delete()
            Interested(
                person=self.major_interested, direct=True, lawsuit=self.lawsuit
            ).save()
        elif not query.filter(person=self.major_interested).exists():
            Interested(
                lawsuit=self.lawsuit, person=self.major_interested, direct=True
            ).save()

        for interested in self.other_interesteds.filter():
            if not query.filter(person=interested, direct=False).exists():
                Interested(person=interested, lawsuit=self.lawsuit, direct=False).save()


class _SyncMatters:

    def sync_matters(self):
        LawsuitMatter.register_principal_matter(
            lawsuit=self.lawsuit,
            matter=self.main_matter,
        )

        LawsuitMatter.register_others_matters(
            lawsuit=self.lawsuit, matters=[m for m in self.other_matters.filter()]
        )


class _SyncBlockers:

    def sync_blokers(self):
        """
        Este metodo tem a função de sincronizar os investigados com as pessoas que foram apontados nesta portaria.
        """
        for person_bloker in self.blokers.all():
            person = person_bloker
            Klass = CommonPerson

            if hasattr(person_bloker, "pessoajuridica"):
                Klass = Company
                person = person_bloker.pessoajuridica
            elif hasattr(person_bloker, "pessoafisica"):
                Klass = Person
                person = person_bloker.pessoafisica

            if not Klass:
                raise Exception(
                    'Não consegui indentifica o tipo do investigado para "%s"'
                    % person_bloker.nome
                )
            else:
                try:
                    obj, created = Klass.objects.get_or_create(
                        bloke=person, lawsuit=self.lawsuit
                    )
                    if created:
                        obj.save()
                except Exception:
                    log.warn(
                        "Erro sincronizando os investigados para o procedimento %s",
                        self.lawsuit.cache_number,
                    )
                    log.warn("Não consegui sincronizar o apontado %s", person)


@type_part_lawsuit()
class OrdinaceReformulated(
    _SyncBlockers, _SyncMatters, _SyncInterested, InitialPartlawsuit, PartLawsuit
):
    type_ordinace = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_ORDINACE")
    )
    number_part = models.PositiveIntegerField(null=True, blank=True)
    year_number = models.SmallIntegerField(null=True, blank=True)
    formated_code = models.CharField(max_length=15, null=True, blank=True, unique=True)
    other_matters = models.ManyToManyField(
        LegalMatter, related_name="in_ordinaces_reformulated"
    )
    blokers = models.ManyToManyField("rh.Pessoa", related_name="as_blokers")
    change_title = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    extract_of_port = models.TextField(null=True, blank=True)
    publication = models.ForeignKey(
        "rh.Publicacao",
        related_name="as_ordinaces_reformulated",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    location = models.ForeignKey(
        "rh.Lotacao", blank=True, null=True, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    major_interested = models.ForeignKey(
        "rh.Pessoa", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    other_interesteds = models.ManyToManyField(
        "rh.Pessoa", related_name="as_other_interesteds_in_ordinace"
    )
    ordinance_supplemented = models.OneToOneField(
        "OrdinaceReformulated",
        blank=True,
        null=True,
        related_name="supplement",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    main_matter = models.ForeignKey(
        LegalMatter, related_name="+", blank=True, null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Portaria de Instauração"

    only_responsible_sign = True
    allow_instated = True

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @property
    def deadline_days(self):
        return self.deadline_days_for_type(self.type_ordinace)

    @classmethod
    def deadline_days_for_type(klass, type_ordinace):
        cfg = Configuration.objects.get(application="ejud")
        type_ordinace = int(type_ordinace or 0)

        type_map = {
            2: "deadlineCivilInvestigation",
            3: "deadlinePreparatoryProcedure",
            4: "deadlinePreparatoryCivilInvestigation",
            7: "deadlineAdministrativeProcedure",
            8: "deadlineRogatoryLetter",
            9: "deadlinePreparatoryProcedureElectoral",
            10: "deadlineAdministrativeManagement",
        }

        return int(cfg.get(type_map.get(type_ordinace, "unknow"), 0))

    def sign_part(self):
        """
        Este metodo é responsável por asinar a portaria de instauração.
        """
        if not self.main_matter:
            raise Exception("Campo assunto principal não preenchido.")

        if not self.major_interested:
            raise Exception("É necessário informar quem é o principal interessado.")

        if not self.content:
            raise Exception(
                "Nenhum conteúdo da portaria foi inserido, veja a sessão documento."
            )

        if not self.acting_zone:
            raise Exception("É necessário informar a Área de Atuação.")

        self.type_ordinace = int(self.type_ordinace or 0)

        with transaction.atomic():
            self.year_number = date.today().year
            self.number_part = self._next_number()
            self.formated_code = self.formated_number
            self.save()

            self.sync_interesteds()
            self.sync_matters()

            if not self.is_instanted:
                self._sign_lawsuit_prepare()

            self.lawsuit.title = self.change_title
            self.lawsuit.type_lawsuit = self.type_ordinace
            self.lawsuit.main_matter = self.main_matter
            self.lawsuit.save()

            self.page_number = 1
            self.cache_rendered = None
            super(OrdinaceReformulated, self).sign_part()

            self.signed_at = datetime.now()
            self.signed_by = get_current_user()
            self.dispatch_comunication(
                subject="Comunicar a %s" % str(self), external_number=self.formated_code
            )

            if self.type_ordinace in (2,):
                self.request_publication()

            if self.deadline_days > 0:
                # self.lawsuit.deadline_cache = date.today() + timedelta(days=self.deadline_days)
                self.lawsuit.remaining_days = self.deadline_days
            else:
                # self.lawsuit.deadline_cache = None
                self.lawsuit.remaining_days = None

            self.lawsuit.save()
            self.sync_blokers()

            # FIXME isto deve ser reescrito após implementação da edicação compartilhada de documento.
            current_moviment = None
            if self.lawsuit.origin.movimentacoes.filter(passo__gt=0).exists():
                current_moviment = self.lawsuit.current_moviment()
            else:
                current_moviment = self.lawsuit.origin.movimentacoes.last()

            old_fn = current_moviment.validate_possession_for_do_send

            def empty_fn(*args, **kwargs):
                pass

            current_moviment.validate_possession_for_do_send = empty_fn

            self.lawsuit.send_to(
                to=self.lawsuit.location, force_current=current_moviment
            )
            current_moviment.validate_possession_for_do_send = old_fn

    def _calculate_deadline_date(self):
        return None

    def _lawsuit_type(self):
        return self.type_ordinace

    @property
    def lawsuit_title(self):
        return self.change_title

    @property
    def content_processed(self):
        try:
            return re.sub(
                r"<!-- begin header -->.*<!-- end header -->",
                "",
                self.rendered.replace("\n", ""),
            )
        except Exception as e:
            return str(e)

    @property
    def rendered_extract_of_port(self):
        return loader.get_template("judicial/lawsuit/extract_of_port.html").render(
            {"doc": self}
        )

    def request_publication(self, update=True):
        """
        Este metodo é responsável por requisitar publicação no diário oficial do MP
        @param update boolean esta flag caso True irá salvar a associação da publicação na portaria.
        """
        cfg = Configuration.get_or_create("ejud")

        self.publication = Publication.request_publication(
            self.lawsuit.location,
            self.number_part,
            publication_type=int(cfg.get("typePublication", 0) or 0),
            year=self.year_number,
            expedition_at=date.today(),
            document=self.rendered_extract_of_port,
            document_read_only=True,
            internal=False,
            interested=[],
            publication_vehicle=cfg.get("vehiclePublication", None),
        )

        if update:
            self.__class__.objects.filter(pk=self.pk).update(
                publication=self.publication
            )

    def save(self, *args, **kwargs):
        created = self.pk is None
        if not getattr(self, "lawsuit", None) and self.location:
            log.info("creating lawsuit...")
            self.interested = self.major_interested
            self.lawsuit = self._create_lawsuit()
        elif not getattr(self, "lawsuit", None) and not self.location:
            raise Exception(
                "Para instauração inicial, deve ser informado o local de instauração."
            )

        if self.lawsuit and not self.lawsuit.origin and self.major_interested:
            self.interested = self.major_interested
            self.lawsuit.origin = self._docketing_protocol()
            self.lawsuit.save()

        if not self.change_title:
            self.change_title = self.lawsuit.title
        elif not self.lawsuit.title and self.change_title:
            self.lawsuit.title = self.change_title
            self.lawsuit.save()

        if not self.major_interested and self.lawsuit and self.lawsuit.origin:
            self.major_interested = self.lawsuit.origin.interessado

        if not self.main_matter:
            self.main_matter = LawsuitMatter.get_principal_matter(lawsuit=self.lawsuit)

        super(OrdinaceReformulated, self).save(*args, **kwargs)

        if created:
            for lm in self.lawsuit.in_lawsuit_matter.exclude(
                matter__in=self.other_matters.filter()
            ).filter(principal=False):
                self.other_matters.add(lm.matter)

        if self.major_interested:
            for interested in self.lawsuit.interested.exclude(
                pk__in=self.other_interesteds.filter()
            ).exclude(pk=self.major_interested.pk):
                self.other_interesteds.add(interested)

        for bloke in self.lawsuit.blokes.exclude(pk__in=self.blokers.filter()):
            self.blokers.add(bloke.my_origin.bloke)

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(doc=self, execution_organ=execution_organ)

        return rst

    def _next_number(self):
        Model = self.__class__

        older_max_number = 0
        if Ordinace.objects.filter(year=self.year_number).exists():
            older_max_number = (
                Ordinace.objects.filter(year=date.today().year)
                .aggregate(max_number=models.Max("number"))
                .get("max_number", 0)
            )

        max_number = (
            Model.objects.filter(year_number=date.today().year)
            .aggregate(max_number=models.Max("number_part"))
            .get("max_number", 0)
        )

        max_number = int(max_number or 0)
        older_max_number = int(older_max_number or 0)

        if older_max_number > max_number:
            return older_max_number + 1
        else:
            return int(max_number or 0) + 1

    @property
    def formated_number(self):

        choice = JudicialChoice.objects.get(
            app_label="judicial", name="TYPE_ORDINACE", value=self.type_ordinace
        )

        return "%s/%04d/%d" % (
            choice.cvalue,
            int(self.number_part or 0),
            int(self.year_number or 0),
        )

    @property
    def name_supplemented(self):
        if not self.ordinance_supplemented:
            return ""
        else:
            return "(Aditamento da portaria {0})".format(
                self.ordinance_supplemented.formated_number
            )

    @property
    def title(self):
        return " ".join([self.codename, self.formated_number, self.name_supplemented])

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-investigation"

    def create_supplement_instance(self):
        """
        Cria e retorna uma instância de OrdinanceReformulated, baseada na instância atual.
        """
        if not self.read_only:
            raise Exception("Essa portaria não encontra-se assinada.")

        with transaction.atomic():

            ordinace = OrdinaceReformulated(
                lawsuit=self.lawsuit,
                create_location=self.create_location,
                cache_rendered=None,
                type_part=self.type_part,
                signed_by=None,
                signed_at=None,
                created_by=get_current_user(),
                created_at=datetime.now(),
                modified_by=get_current_user(),
                modified_at=datetime.now(),
                page_number=None,
                is_public=self.is_public,
                legal_classification=self.legal_classification,
                acting_zone=self.acting_zone,
                type_ordinace=self.type_ordinace,
                number_part=None,
                year_number=None,
                formated_code=None,
                change_title=self.change_title,
                content=self.content,
                extract_of_port=self.extract_of_port,
                publication=self.publication,
                location=self.location,
                major_interested=self.major_interested,
                ordinance_supplemented=self,
            )

            ordinace.save()

            [ordinace.other_matters.add(a) for a in self.other_matters.all()]
            [
                ordinace.shared_with_lawsuit.add(a)
                for a in self.shared_with_lawsuit.all()
            ]
            [ordinace.blokers.add(a) for a in self.blokers.all()]
            [ordinace.other_interesteds.add(a) for a in self.other_interesteds.all()]

            """
                Copia as comunicações
            """
            for obj in self.sciences.filter():
                ScientifyWorkplace(
                    part=ordinace,
                    location=obj.location,
                    content=obj.content if obj.content else " ",
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    created_by=get_current_user(),
                    modified_by=get_current_user(),
                ).save()

            """
                Copia os anexos
            """
            for obj in self.attaches.filter():
                Attached(
                    attached_document=ordinace,
                    title=obj.title,
                    file_descriptor=obj.file_descriptor,
                ).save()

            return ordinace


class WorkerReminder(AuditTimestampModel):
    """Modelo responsável pela comunicação acerca de documentos entre membro e analista.

    Esse modelo tem como objetivo fornecer um mecanismo onde o usuário comunica a uma lista de pessoas, os documentos que foram ou necessitam ser analisados.

    Attributes:
        part (PartLawsuit): Documento do procedimento que esta sendo comunicado.
        receiver (Servidor): Destinatário da comunicação.
        observation (Text): Campo para observação.
        resolved (Boolean): flag para indicar que a comunicação/lembre foi resolvida.
        deadline (Date): data fim para resolução do lembrete
    """

    part = models.ForeignKey(
        PartLawsuit, related_name="worker_reminder", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    receiver = models.ForeignKey(
        Servidor, related_name="worker_reminder", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    deadline = models.DateField(null=True)
    priority = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "WORKER_REMINDER_PRIORITY")
    )
    resolved_at = models.DateTimeField(
        verbose_name="Concluído em", null=True, blank=True
    )
    resolved_by = models.ForeignKey(
        "auth.User",
        verbose_name="Concluído por",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ("-created_at",)

    @property
    def rendered(self):
        data = "<h2><spam>Observação:</spam></h2><p><br /></p> %s " % self.observation
        return data

    @property
    def rendered_appends(self):
        return self.part.rendered

    def check_permission(self, user, action, app_label, object_name):
        perm = "%(app_label)s.%(action)s_%(object_name)s" % vars()
        perm = perm.lower()

        log.info("check %s permission for %s" % (perm, user))
        if user.has_perm(perm) is True:
            log.info("user %s has permission %s" % (user, perm))
            return True
        else:
            log.warn("permission %s dained for %s" % (perm, user))
            return False

    @classmethod
    def delivery(cls, receiver, parts, deadline=None, observation="", priority=None):
        """Metodo que cria e distribui lembretes/comunicação.

        Cria para cada destinatário um lembrete. Cada lembrete terá um documento associado. Logo, a quantidade
        de lembretes é o produto de DESTINATÁRIOS x DOCUMENTOS.

        Args:
            receiver (List): Lista de pks de destinatários/servidor.
            parts (List): Lista de pks de documentos/Partlawsuit.
            deadline (Date): Prazo
            observation (Text): Informações sobre o lembrete,
            priority (Int): Valor da prioridade do lembrete

        """
        obj = cls()

        can = obj.check_permission(
            get_current_user(), "add", obj._meta.app_label, obj._meta.object_name
        )

        if can is False:
            raise Exception("Você não tem permissão para criar uma comunicação.")
        else:
            receiver = (
                receiver
                if isinstance(receiver, (tuple, list, set)) is True
                else [receiver]
            )
            parts = parts if isinstance(parts, (tuple, list, set)) is True else [parts]

            if not receiver:
                raise Exception("Destinatário não informado.")
            if not parts:
                raise Exception("Documento não informado.")
            if not priority:
                raise Exception("Informe a prioridade.")

            try:
                reminder = []
                for employee in Servidor.objects.filter(pk__in=receiver):
                    for part in PartLawsuit.objects.filter(pk__in=parts):
                        reminder.append(
                            WorkerReminder(
                                part=part,
                                receiver=employee,
                                deadline=deadline,
                                observation=observation,
                                created_by=get_current_user(),
                                modified_by=get_current_user(),
                                created_at=datetime.now(),
                                modified_at=datetime.now(),
                                priority=priority,
                            )
                        )

            except Exception as e:
                raise e
            else:
                if reminder:
                    with transaction.atomic():
                        WorkerReminder.objects.bulk_create(reminder)

    @property
    def can_check_resolved(self):
        return (
            True if self.receiver == employee_from_user(get_current_user()) else False
        )

    def check_resolved(self):

        can = self.check_permission(
            get_current_user(), "change", self._meta.app_label, self._meta.object_name
        )

        if can is False:
            raise Exception("Você não tem permissão para modificar a comunicação.")
        elif not self.resolved:
            if self.can_check_resolved:
                self.resolved = True
                self.resolved_by = get_current_user()
                self.resolved_at = datetime.now()
                self.save()
            else:
                raise Exception(
                    "Não pode marcar como concluído uma comunicação que não foi destinado a você."
                )
        else:
            raise Exception("A comunicação encontra-se marcada como resolvida.")

    @property
    def solicited_by(self):
        person = person_from_user(self.created_by, False)

        return person.nome if person else self.created_by.username

    @property
    def resolved_by_unicode(self):
        result = None

        if self.resolved_by:
            person = person_from_user(self.resolved_by, False)
            result = person.nome if person else self.resolved_by.username

        return result

    def save(self, *args, **kwargs):
        if self.pk:
            actual = self.__class__.objects.get(pk=self.pk)
            if actual.resolved:
                raise Exception("Não é possível modificar uma análise concluída")

        super(WorkerReminder, self).save(*args, **kwargs)


class JudicialLegalSign(object):

    @property
    def rendered(self):
        tpl = loader.get_template("judicial/legal_sign.html")
        return tpl.render({"sign": self})


class PartLegalSign(JudicialLegalSign, LegalSign):
    part = models.ForeignKey(
        PartLawsuit, related_name="legal_signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _fill(self, part):
        super(PartLegalSign, self)._fill()
        self.plain_content = part.rendered
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha224", self.content).hexdigest()

    @classmethod
    def sign(klass, part):
        obj = klass()
        obj.part = part
        obj._fill(part)
        obj.save()

        return obj


class JudicialDiligenceLegalSign(JudicialLegalSign, LegalSign):
    diligence = models.ForeignKey(
        JudicialDiligence, related_name="legal_signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _fill(self, diligence):
        super(JudicialDiligenceLegalSign, self)._fill()
        self.plain_content = diligence.rendered
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha224", self.content).hexdigest()

    @classmethod
    def sign(klass, diligence):
        obj = klass()
        obj.diligence = diligence
        obj._fill(diligence)
        obj.save()

        return obj


class ManifestationLegalSign(JudicialLegalSign, LegalSign):
    manifestation = models.ForeignKey(
        Manifestation, related_name="legal_signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _fill(self, manifestation):
        super(ManifestationLegalSign, self)._fill()
        self.plain_content = manifestation.renderer
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha224", self.content).hexdigest()

    @classmethod
    def sign(klass, manifestation):
        obj = klass()
        obj.manifestation = manifestation
        obj._fill(manifestation)
        obj.save()

        return obj


class DeliveryAttemptLegalSign(JudicialLegalSign, LegalSign):
    delivery_attempt = models.ForeignKey(
        DeliveryAttempt, related_name="legal_signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _fill(self, delivery_attempt):
        super(DeliveryAttemptLegalSign, self)._fill()
        self.plain_content = delivery_attempt.rendered
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha224", self.content).hexdigest()

    @classmethod
    def sign(klass, delivery_attempt):
        obj = klass()
        obj.delivery_attempt = delivery_attempt
        obj._fill(delivery_attempt)
        obj.save()

        return obj


class RequestExternalPartLegalSign(PartLegalSign):

    @property
    def who_person(self):
        my = self.part.my_origin
        who = my.person if my.person else my.as_representative_of
        return str(who.nome)


@type_part_lawsuit()
class DearchivingDispatch(PartLawsuit):
    dearchiving_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "DEARCHIVEDISPATCH_TYPE"),
        blank=True,
        null=True,
    )
    content = models.TextField(null=True, blank=True)

    codename = "Desarquivamento"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def _calculate_deadline_date(self):
        cfg = Configuration.objects.get(application="ejud")
        type_lawsuit = int(self.lawsuit.type_lawsuit or 0)

        type_map = {
            1: "deadlineFactNews",
            2: "deadlineCivilInvestigation",
            3: "deadlinePreparatoryProcedure",
            4: "deadlinePreparatoryCivilInvestigation",
            7: "deadlineAdministrativeProcedure",
            8: "deadlineRogatoryLetter",
            9: "deadlinePreparatoryProcedureElectoral",
            10: "deadlineAdministrativeManagement",
        }

        days = int(cfg.get(type_map.get(type_lawsuit, "undefined"), 0) or 0)

        return days

    def sign_part(self):
        with transaction.atomic():
            if not self.dearchiving_type:
                raise Exception("Informe o motivo do desarquivamento.")

            super(DearchivingDispatch, self).sign_part()

            protocol_pks = []
            connected_pks = []

            for l in self.lawsuit.has_connected.filter():
                connected_pks.append(l.pk)
                protocol_pks.append(l.origin.pk)

            protocol_pks.append(self.lawsuit.origin.pk)

            query = Movimentacao.closedbox_queryset()

            query.filter(protocolo__in=protocol_pks).update(data_finalizado=None)

            Protocolo.objects.filter(pk__in=protocol_pks).update(data_finalizado=None)

            OutCourtLawsuit.objects.filter(pk__in=connected_pks).update(
                closed_by=None, closed_at=None
            )

            self.lawsuit.closed_by = None
            self.lawsuit.closed_at = None

            self.lawsuit.remaining_days = self._calculate_deadline_date()
            self.lawsuit.save()

    def validate_ownership(self):
        if (
            not Movimentacao.closedbox_queryset()
            .filter(protocolo=self.lawsuit.origin)
            .exists()
        ):
            raise Exception(
                "Você só pode pedir desarquivamento de um procedimento que esteja arquivado em seu Órgão de Execução."
            )
        elif not self.lawsuit.closed_by or not self.lawsuit.closed_at:
            raise Exception(
                "Este documento só pode ser usado para procedimentos que encontram-se finalizados."
            )


@type_part_lawsuit()
class ArchivementNoticeOffice(PartLawsuit):
    cause = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "ARCHIVEMENT_NOTICE_OFFICE_CAUSE"),
        blank=True,
        null=True,
    )
    content = models.TextField(blank=True)

    codename = "Finalizar"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def sign_part(self, *args, **kwags):
        with transaction.atomic():
            if not self.cause:
                raise Exception("Informe o motivo do arquivamento.")

            # verifica se ha alguma suspensao de prazo ativa. Se hover desabilita-a
            if self.lawsuit.all_signed_documents.filter(
                suspenddeadline__active=True
            ).exists():
                for document in self.lawsuit.all_signed_documents.filter(
                    suspenddeadline__active=True
                ):
                    suspend = document.my_origin
                    suspend.active = False
                    suspend.skip_read_only_validate = True
                    suspend.save()

            super(ArchivementNoticeOffice, self).sign_part(*args, **kwags)
            self.lawsuit.send_to(to=[self.lawsuit.location], finalizado=True)

    def save(self, *args, **kwags):
        super(ArchivementNoticeOffice, self).save(*args, **kwags)


@type_part_lawsuit()
class DilationManifestation(PartLawsuit):
    manifestation = models.ForeignKey(
        Manifestation, related_name="dilations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    dilation_days = models.SmallIntegerField(default=0)
    older_deadline = models.DateField(null=True, blank=True)
    content = models.TextField()

    codename = "Dilação de prazo de Diligência"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def sign_part(self, *args, **kwags):
        with transaction.atomic():
            if not self.manifestation.deadline:
                raise Exception(
                    "Não posso pedir dilação de prazo para uma diligência que ainda não tem prazo definido."
                )

            days = relativedelta(days=self.dilation_days)
            self.older_deadline = self.manifestation.deadline

            super(DilationManifestation, self).sign_part(*args, **kwags)

            deadline = date.today() + days
            Manifestation.objects.filter(pk=self.manifestation.pk).update(
                deadline=deadline
            )


class OutCourtLawsuitLog(models.Model):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="logs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    type_lawsuit = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_LAWSUIT"),
        verbose_name="Tipo do Procedimento",
    )
    main_tag = models.ForeignKey(
        Tag,
        related_name="has_main_tag_in_lawsuit_log",
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    main_matter = models.ForeignKey(
        "judicial.LegalMatter",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    part = models.ForeignKey(
        PartLawsuit, related_name="in_log", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    location = models.ForeignKey(
        OrgaoGeral, related_name="in_log", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    deadline_days = models.IntegerField(null=True)
    initiator_at = models.DateTimeField(null=True, blank=True)
    acting_zone = models.ForeignKey(
        "ActingZone",
        related_name="in_log",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    at_moment = models.DateTimeField(null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def register(klass, lawsuit, part=None):

        if not part:
            part = lawsuit.last_part_lawsuit
        else:
            part.refresh_from_db()

        reg = klass(
            lawsuit=lawsuit,
            type_lawsuit=lawsuit.type_lawsuit,
            part=part,
            main_tag=lawsuit.main_tag,
            main_matter=lawsuit.main_matter,
            location=part.create_location,
            deadline_days=lawsuit.deadline,
            initiator_at=part.signed_at if part.my_origin.is_initiator else None,
            acting_zone=lawsuit.acting_zone,
            at_moment=part.at_moment(),
        )
        reg.save()

        return reg


class LawsuitChangeMovimentLog(models.Model):
    lawsuit_log = models.ForeignKey(
        OutCourtLawsuitLog,
        related_name="in_lawsuitmovimentlog",
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        OrgaoGeral, related_name="in_movimentlog", on_delete=models.CASCADE
    )
    movimented_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def register(klass, lawsuit_log, location):
        reg = klass(
            lawsuit_log=lawsuit_log,
            location=location,
            movimented_at=lawsuit_log.part.signed_at,
        )
        reg.save()

        return reg


@type_part_lawsuit()
class GeneralMotion(PartLawsuit):
    """GeneralMotion.

    Classe representando o documento de movimentação geral. Trata-se de um documento genérico
    cuja classificação será realizada através da indicação do Movimento Taxonômico, e seu corpo
    conterá a redação do despacho a ser realizado.

    Attributes:
        name (CharField): nome do movimento
        content (TextField): campo para redigir o despacho
    """

    name = models.CharField(max_length=100)
    content = models.TextField()

    codename = "Movimentação Geral"

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @property
    def title(self):
        return "%s - %s" % (
            (
                self.legal_classification.cnmp_code
                if self.legal_classification
                else None
            ),
            self.name,
        )

    @property
    def sign_permissions(self):
        return [
            (
                "judicial.can_sign_simples"
                if self.legal_classification.helper_can_sign
                else "judicial.can_sign"
            )
        ]

    def sign_part(self):
        with transaction.atomic():
            self.save()
            super(GeneralMotion, self).sign_part()

            if self.legal_classification.suspend_deadline:
                SuspendDeadline.create(lawsuit=self.lawsuit)

            if self.legal_classification.extend_deadline:
                DilationPeriod.extend_deadline(lawsuit=self.lawsuit)

            self.dispatch_comunication(
                subject="Comunicar a %s" % str(self),
            )

    def save(self, *args, **kwargs):
        if self.legal_classification is None:
            raise Exception("É necessário informar a classificação do movimento.")
        elif not hasattr(self.legal_classification, "legalmoviment"):
            raise Exception("A classificação deve ser do tipo Movimento.")

        super(GeneralMotion, self).save(*args, **kwargs)


@type_part_lawsuit()
class Unfold(PartLawsuit):
    unfold_document = models.ForeignKey(
        PartLawsuit, related_name="unfolder", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    codename = "Desentranhamento"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"]

    @property
    def unfold_permissions(self):
        return ["judicial.can_unfold_any_document"]

    @property
    def can_unfold(self):
        user = get_current_user()
        return self.unfold_document.signed_by == user or user.has_perms(
            self.unfold_permissions
        )

    def sign_part(self):
        if self.unfold_document.unfolded_by:
            raise Exception(
                "Não posso desentranhar um documento que já foi desentranhado."
            )

        with transaction.atomic():
            super(Unfold, self).sign_part()
            self.lawsuit.all_signed_documents.filter(pk=self.unfold_document.pk).update(
                unfolded_by=self.signed_by, unfolded_at=self.signed_at
            )

    def save(self, *args, **kwargs):
        if not self.can_unfold:
            raise Exception(
                "Usuário não possui permissões para desentranhar este documento."
            )

        super(Unfold, self).save(*args, **kwargs)


@type_part_lawsuit()
class UnConnect(PartLawsuit):
    unconnect_lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="unconnections", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Desanexação de Procedimento"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def sign_part(self):
        with transaction.atomic():
            super(UnConnect, self).sign_part()
            query = self.lawsuit._all_signed_documents(False).filter(
                connectionlawsuit__unconnected_by=None,
                connectionlawsuit__lawsuit_connected=self.unconnect_lawsuit,
            )

            if query.exists():
                ConnectionLawsuit.objects.filter(pk=query.last()).update(
                    unconnected_by=self.signed_by, unconnected_at=self.signed_at
                )

                parts_to_disconnected = self.unconnect_lawsuit._all_signed_documents(
                    False
                ).values_list("pk")

                for doc in self.lawsuit._all_signed_documents(False).filter(
                    pk__in=parts_to_disconnected
                ):
                    EventControl.objects.filter(lawsuit=self.lawsuit, part=doc).update(
                        discarded_by=self
                    )

                for doc in self.lawsuit._all_signed_documents(False).filter(
                    pk__in=parts_to_disconnected
                ):
                    doc.shared_with_lawsuit.remove(self.lawsuit)

                # self.unconnect_lawsuit.deadline_cache = OutCourtLawsuit.calculate_deadline_date(self.unconnect_lawsuit)
                self.unconnect_lawsuit.remaining_days = (
                    OutCourtLawsuit.remainig_days_type_lawsuit(self.unconnect_lawsuit)
                )
                self.unconnect_lawsuit.attached_lawsuit = None
                self.unconnect_lawsuit.save()
            else:
                raise Exception(
                    "Não consegui encontrar a conexão do procedimento %s, operação finalizada."
                    % self.unconnect_lawsuit.cache_number
                )


class ConfidentialAccess(PartLawsuit):
    part_lawsuit_access = models.ManyToManyField(
        PartLawsuitAccess, related_name="in_%(class)s"
    )
    apply_in = models.SmallIntegerField(
        verbose_name="Aplicar no",
        choices=((1, "OUTCOURTLAWSUIT"), (2, "PARTLAWSUIT"), (100, "UNDEFINED")),
        default=100,
    )

    class Meta:
        abstract = True

    def add_part(self, part=None):
        if part:
            self._create_part_lawsuit_access(part=part)

    def add_lawsuit(self, lawsuit=None):
        if lawsuit:
            self._create_part_lawsuit_access(lawsuit=lawsuit)

    def remove_part(self, part=None):
        if part:
            self._remove_part_lawsuit_access(part=part)

    def _create_part_lawsuit_access(self, lawsuit=None, part=None):
        with transaction.atomic():
            access = PartLawsuitAccess(
                lawsuit=lawsuit,
                part=part,
            )
            access.save()
            self.part_lawsuit_access.add(access)

    def _remove_part_lawsuit_access(self, part=None):
        with transaction.atomic():
            for access in self.part_lawsuit_access.filter(part=part):
                access.delete()

    @property
    def has_confidential_access(self):
        return PartLawsuitAccess.objects.filter(
            Q(
                Q(
                    Q(lawsuit=self.lawsuit)
                    | Q(part__in=self.lawsuit.all_signed_documents)
                )
                & Q(suspended_at=None)
            )
        ).exists()


@type_part_lawsuit()
class GrantConfidentialAccess(ConfidentialAccess):

    codename = "Decretar Sigilo"

    def _sign_part_authorized(self):
        if not getattr(self, "by_confidential_protocol", False):
            return super()._sign_part_authorized()
        return True

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def title(self):
        return "Decretar Sigilo"

    def save(self, *args, **kwargs):
        super(GrantConfidentialAccess, self).save(*args, **kwargs)

    def prepare(self):
        if self.apply_in not in [1, 2]:
            raise Exception(
                "Informe se o sigilo será aplicado ao Procedimento ou a um documento."
            )

        if self.apply_in == 2 and not self.part_lawsuit_access.exists():
            raise Exception("Informe os documentos que serão marcados com sigilos.")

        if self.apply_in == 1:
            self.add_lawsuit(lawsuit=self.lawsuit)
            for access in self.part_lawsuit_access.filter():
                self.remove_part(part=access.part)

    def sign_part(self):
        with transaction.atomic():
            self.prepare()

            for access in self.part_lawsuit_access.filter():
                access.sign()

            super(GrantConfidentialAccess, self).sign_part()

    def delete(self, *args, **kwargs):
        super(GrantConfidentialAccess, self).delete(*args, **kwargs)

    def _is_protocol_secret(self):
        protocol_control = self._has_protocol_control()
        if protocol_control:
            return protocol_control.is_secret

        return False

    def _has_protocol_control(self):
        try:
            control = ProtocolControl.objects.get(document=self.lawsuit.origin)
            return control
        except ProtocolControl.DoesNotExist as e:
            log.debug("Protocolo não tem controle associado.")
            return False

    def params(self):
        rst = super().params()

        protocol_control = self._has_protocol_control()
        if protocol_control and protocol_control.is_secret:
            rst.update({"confidential_protocol": protocol_control})

        return rst


@type_part_lawsuit()
class RevokeConfidentialAccess(ConfidentialAccess):

    codename = "Desclassificação de Sigilo"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    def set_apply_in(self):
        if PartLawsuitAccess.objects.filter(
            lawsuit=self.lawsuit, suspended_at=None
        ).exists():
            self.apply_in = 1
        elif PartLawsuitAccess.objects.filter(
            part__in=self.lawsuit.all_signed_documents, suspended_at=None
        ):
            self.apply_in = 2

    """Overwrite"""

    def add_part(self, part=None):
        for access in PartLawsuitAccess.objects.filter(suspended_at=None).filter(
            part=part
        ):
            self.part_lawsuit_access.add(access)

    """Overwrite"""

    def remove_part(self, part=None):
        for access in self.part_lawsuit_access.filter(part=part):
            self.part_lawsuit_access.remove(access)

    """Overwrite"""

    def add_lawsuit(self, lawsuit=None):
        for access in lawsuit.access_controls.filter(suspended_at=None):
            self.part_lawsuit_access.add(access)

    def _declassify_confidential_protocol(self):
        for pa in self.part_lawsuit_access.filter(
            part__lawsuit__origin__protocol_control__control_type__is_secret=True
        ):
            pa.part.lawsuit.origin.protocol_control.declassify(
                justification="Desclassificação de sigilo realizada pelo evento nº %d no procedimento extrajudicial nº %s"
                % (
                    self.partlawsuit_ptr.event_control.number_control,
                    self.partlawsuit_ptr.lawsuit.cache_number,
                )
            )

    def sign_part(self):
        with transaction.atomic():
            if not self.has_confidential_access:
                raise Exception("Não há sigilo para ser removido.")

            if self.apply_in == 1:
                self.add_lawsuit(lawsuit=self.lawsuit)

            for access in self.part_lawsuit_access.filter():
                access.delete()

            super(RevokeConfidentialAccess, self).sign_part()

            self._declassify_confidential_protocol()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.set_apply_in()

        super(RevokeConfidentialAccess, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.part_lawsuit_access.clear()
        super(RevokeConfidentialAccess, self).delete(*args, **kwargs)


class ActingZone(AuditTimestampModel):
    """ActingZone

    Classe das áreas de atuação
    """

    title = models.CharField(max_length=200, unique=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ("-enabled", "title")

    def __str__(self):
        return "%s" % self.title


@type_part_lawsuit()
class AdjustmentLawsuit(PartLawsuit):
    """AdjustmentLawsuit
    Classe utilizada para modificar informações de um procedimento

    """

    last_title = models.CharField(max_length=255, blank=True)
    new_title = models.CharField(max_length=255, blank=True)
    last_matters = models.ManyToManyField(LegalMatter, related_name="+")
    new_matters = models.ManyToManyField(LegalMatter, related_name="+")
    last_acting_zone = models.ForeignKey(
        ActingZone, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    new_acting_zone = models.ForeignKey(
        ActingZone, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    last_main_matter = models.ForeignKey(
        LegalMatter, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    new_main_matter = models.ForeignKey(
        LegalMatter, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Reautuação de Procedimento"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def sign_part(self):
        with transaction.atomic():
            if self.new_main_matter is None:
                raise Exception("É necessário informar o assunto principal.")

            save = False

            if self.new_title:
                self.lawsuit.title = self.new_title
                save = True

            if self.new_acting_zone:
                self.lawsuit.acting_zone = self.new_acting_zone
                save = True

            self.lawsuit.main_matter = self.new_main_matter

            LawsuitMatter.register_principal_matter(
                lawsuit=self.lawsuit,
                matter=self.new_main_matter,
            )

            LawsuitMatter.register_others_matters(
                lawsuit=self.lawsuit,
                matters=[m for m in self.new_matters.filter()],
            )

            if save:
                self.lawsuit.save()

            super(AdjustmentLawsuit, self).sign_part()

    def save(self, *args, **kwargs):
        created = self.pk is None
        if created:
            self.last_title = self.new_title = self.lawsuit.title
            self.last_acting_zone = self.new_acting_zone = self.lawsuit.acting_zone
            self.last_main_matter = self.new_main_matter = (
                LawsuitMatter.get_principal_matter(lawsuit=self.lawsuit)
            )
        super(AdjustmentLawsuit, self).save(*args, **kwargs)

        if created:
            for lm in self.lawsuit.in_lawsuit_matter.filter(principal=False):
                self.last_matters.add(lm.matter)
                self.new_matters.add(lm.matter)


@type_part_lawsuit()
class RequestExternalAccess(PartLawsuit):
    person = models.ForeignKey(
        "rh.Pessoa",
        related_name="with_external_access_lawsuit",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    as_representative_of = models.ForeignKey(
        "rh.Pessoa", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    request = models.TextField(blank=True, null=True)
    rendered_request_cache = models.TextField(null=True, blank=True)
    authorized_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    authorized_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    revoked_at = models.DateTimeField(null=True, blank=True)
    denied_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    denied_at = models.DateTimeField(null=True, blank=True)
    state = models.SmallIntegerField(
        verbose_name="Situação",
        choices=(
            (1, "NÃO AVALIADO"),
            (2, "AUTORIZADO"),
            (3, "REVOGADO"),
            (4, "NEGADO"),
        ),
        default=1,
    )

    codename = "Solicitação de acesso externo"

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @classmethod
    def authorizations_by_user(cls, user):
        return cls.objects.filter(
            person=user.person,
            authorized_at__isnull=False,
            denied_at__isnull=True,
            revoked_at__isnull=True,
        )

    def authorize(self, justification="", generate_part=True):
        with transaction.atomic():
            if self.authorized_by:
                raise Exception(
                    "Não foi possível realizar a ação. Essa requisição já encontra-se autorizada."
                )
            elif self.denied_by or self.revoked_by:
                raise Exception(
                    "Não foi possível realizar a ação. Verifique se a requisição encontra-se negada ou revogada."
                )
            self.state = 2
            self.authorized_by = get_current_user()
            self.authorized_at = datetime.now()
            self.skip_read_only_validate = True
            self.save()

            if generate_part:
                AuthorizationExternalAccess.generate_part(
                    request=self, state=1, justification=justification
                )

    def revoke(self, justification="", generate_part=True):
        with transaction.atomic():
            if self.revoked_by:
                raise Exception(
                    "Não foi possível realizar a ação. Essa requisição já encontra-se revogada."
                )
            elif not self.authorized_by:
                Exception(
                    "Não foi possível realizar a ação. Verifique se a requisição encontra-se autorizada ou negada."
                )
            self.state = 3
            self.revoked_by = get_current_user()
            self.revoked_at = datetime.now()
            self.skip_read_only_validate = True
            self.save()

            if generate_part:
                AuthorizationExternalAccess.generate_part(
                    request=self, state=2, justification=justification
                )

    def deny(self, justification="", generate_part=True):
        with transaction.atomic():
            if self.denied_by:
                raise Exception(
                    "Não foi possível realizar a ação. Essa requisição já encontra-se negada."
                )
            elif self.authorized_by or self.revoked_by:
                raise Exception(
                    "Não foi possível realizar a ação. Verifique se a requisição encontra-se autorizada ou revogada."
                )

            self.state = 4
            self.denied_by = get_current_user()
            self.denied_at = datetime.now()
            self.skip_read_only_validate = True
            self.save()

            if generate_part:
                AuthorizationExternalAccess.generate_part(
                    request=self, state=3, justification=justification
                )

    @property
    def pending(self):
        return self.state == 1

    @property
    def _renderer_request(self):
        tpl = loader.get_template("judicial/request-external-access.html")
        return tpl.render({"doc": self})

    @property
    def renderer_request(self):
        return (
            self.rendered_request_cache
            if self.rendered_request_cache
            else self._renderer_request
        )

    @property
    def get_part_legal_sign(self):
        return RequestExternalPartLegalSign

    def sign_part(self):
        with transaction.atomic():
            super(RequestExternalAccess, self).sign_part()

    @property
    def read_only(self):
        if getattr(self, "skip_read_only_validate", False):
            return False
        else:
            return True if self.signed_by else False

    def save(self, *args, **kwargs):
        current_movement = self.lawsuit.current_moviment

        def bypass_current_movement(*args, **kargs):
            return self.lawsuit.origin.movimentacoes.filter(
                lotacao_destino=self.lawsuit.location
            ).last()

        self.lawsuit.current_moviment = bypass_current_movement
        super(RequestExternalAccess, self).save(*args, **kwargs)

        self.lawsuit.current_moviment = current_movement

    def params(self):
        rst = {"doc": self, "execution_organ": self.lawsuit.location}

        return rst

    @property
    def get_legal_signs(self):
        return RequestExternalPartLegalSign.objects.filter(part=self)


@type_part_lawsuit()
class AuthorizationExternalAccess(PartLawsuit):
    request_external_access = models.ForeignKey(
        RequestExternalAccess,
        related_name="in_authorization_external_access",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    justification = models.TextField(blank=True)
    state = models.SmallIntegerField(
        verbose_name="Acesso",
        choices=((1, "DEFERIDO"), (2, "REVOGADO"), (3, "INDEFERIDO")),
    )

    codename = "Decisão de acesso externo"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def status(self):
        return self.get_state_display()

    @classmethod
    def generate_part(cls, request=None, state=None, justification=""):
        with transaction.atomic():
            instance = cls()
            instance.request_external_access = request
            instance.state = state
            instance.lawsuit = request.lawsuit
            instance.justification = justification
            instance.save()
            instance.change_request_external = False
            instance.sign_part()

    def change_request_external_access(self):
        if getattr(self, "change_request_external", True):
            if self.state == 1:
                self.request_external_access.authorize(generate_part=False)
            elif self.state == 2:
                self.request_external_access.revoke(generate_part=False)
            elif self.state == 3:
                self.request_external_access.deny(generate_part=False)
            else:
                raise Exception("Opcão inválida")

    def add_interested(self):
        if self.state == 1:
            obj, created = Interested.objects.get_or_create(
                person=self.request_external_access.person, lawsuit=self.lawsuit
            )

    def sign_part(self):
        with transaction.atomic():
            self.change_request_external_access()
            self.add_interested()

            super(AuthorizationExternalAccess, self).sign_part()

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)


class EventControl(models.Model):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    part = models.ForeignKey(
        PartLawsuit, related_name="has_event_controls", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    number_control = models.SmallIntegerField()
    discarded_by = models.ForeignKey(
        PartLawsuit,
        related_name="has_discard_event",
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ("lawsuit", "number_control")

    @classmethod
    def of_lawsuit(klass, lawsuit, part):
        query = klass.objects.filter(lawsuit=lawsuit, part=part, discarded_by=None)
        return query.get() if query.exists() else None

    @classmethod
    def number_control_of(klass, lawsuit, part):
        event = klass.of_lawsuit(lawsuit, part)
        return event.number_control if event else None

    @classmethod
    def factory(klass, lawsuit, part):
        next_number = 1

        if klass.objects.filter(lawsuit=lawsuit).exists():
            query = klass.objects.filter(lawsuit=lawsuit).aggregate(
                max_number=models.Max("number_control")
            )

            next_number = int(query.get("max_number") or 0) + 1

        return EventControl.objects.create(
            lawsuit=lawsuit, part=part, number_control=next_number
        )


class GerencialRemittenceInternal(RemittanceInternal):
    class Meta:
        proxy = True


class PouchedRemittance(RemittanceInternal):
    class Meta:
        proxy = True

    @property
    def model_part_type(self):
        return "remittanceinternal"

    def validate_ownership(self):
        pass

    @property
    def read_only(self):
        return False


class Pouch(AuditTimestampModel):
    pouch_number = models.SmallIntegerField(null=True, blank=True)
    pouch_year = models.SmallIntegerField(null=True, blank=True)
    cache_number = models.CharField(max_length=10, null=True, blank=True)
    from_location = models.ForeignKey(
        "rh.Lotacao", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    to_location = models.ForeignKey(
        "rh.Lotacao", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signed_by = models.ForeignKey(
        "auth.User", related_name="+", blank=True, null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signed_at = models.DateTimeField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-pouch_year", "-pouch_number")

    def __str__(self):
        return "De: %s para %s" % (str(self.from_location), str(self.to_location))

    @classmethod
    def next_number(klass, base_year):
        query = (
            klass.objects.filter(pouch_year=base_year)
            .order_by("pouch_number")
            .aggregate(max_number=models.Max("pouch_number"))
        )
        return int(query.get("max_number") or 0) + 1

    @property
    def is_read_only(self):
        return True if self.signed_by else False

    def delete(self, *args, **kwags):
        if self.is_read_only:
            raise Exception("Não psosso remover um Lote que já foi assinado.")
        super(Pouch, self).delete(*args, **kwags)

    def save(self, *args, **kwags):
        if self.is_read_only and not getattr(self, "skip_read_only_check", False):
            raise Exception("Não psosso alterar um Lote que já foi assinado.")
        super(Pouch, self).save(*args, **kwags)

    def add_items(self, lawsuits):
        if not self.is_read_only:
            for lawsuit in lawsuits:
                if lawsuit.location.pk != self.from_location.pk:
                    raise Exception(
                        "O procedimento %s não pertencem ao local de origem."
                        % lawsuit.cache_number
                    )
                else:
                    PouchLawsuit.objects.get_or_create(pouch=self, lawsuit=lawsuit)
        else:
            raise Exception("Não posso modificar um lote que já foi assinado.")

    def remove_items(self, lawsuits):
        if not self.is_read_only:
            PouchLawsuit.objects.filter(lawsuit__in=lawsuits).delete()
        else:
            raise Exception("Não posso modificar um lote que já foi assinado.")

    def delivery(self, lawsuit):
        if lawsuit.all_signed_documents.exists():
            return self._delivery_by_protocol(lawsuit)
        else:
            return self._delivery_by_location(lawsuit)

    def _delivery_by_location(self, lawsuit):
        OutCourtLawsuit.objects.filter(pk=lawsuit.pk).update(
            location_id=self.to_location.pk
        )

    def _delivery_by_protocol(self, lawsuit):
        lawsuit.read_only = False

        part = PouchedRemittance(
            lawsuit=lawsuit,
            department=self.to_location,
            text="".join(
                [
                    "Gerado por movimentação em Lote %s." % self.cache_number,
                    self.content,
                ]
            ),
        )

        def factory(lawsuit, from_location):
            def __current_moviment(*args, **kwargs):
                movement = getattr(lawsuit, "_current_moviment", None)
                if not movement:
                    movement = lawsuit.origin.movimentacoes.filter(
                        lotacao_destino=from_location, encaminhado=False
                    ).last()

                if movement:
                    movement.validate_possession_for_do_send = lambda: None

                log.debug([lawsuit, from_location, movement])

                return movement

            return __current_moviment

        part.save()
        part.lawsuit.current_moviment = factory(lawsuit, self.from_location)
        part.sign_part()

        return part

    def sign(self):
        from judicial.tasks import delivery_pouch

        with transaction.atomic():
            self.pouch_year = datetime.now().year
            self.pouch_number = self.next_number(self.pouch_year)
            self.cache_number = "%04d/%d" % (self.pouch_number, self.pouch_year)

            if self.is_read_only:
                raise Exception(
                    "Não posso assinar um lote que já se encontra assinado."
                )
            else:
                self.signed_by = get_current_user()
                self.signed_at = datetime.now()
                self.skip_read_only_check = True
                self.save()

                delivery_pouch.delay(self.pk, get_current_user().pk)


class PouchLawsuit(AuditTimestampModel):
    pouch = models.ForeignKey(Pouch, related_name="items", on_delete=models.PROTECT)
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="as_pouches_items", on_delete=models.PROTECT
    )
    movement_part = models.ForeignKey(
        PartLawsuit,
        related_name="as_item_of_pouches",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (("pouch", "lawsuit"),)

    def delivery(self):
        self.lawsuit.receive_movement_lot(self.pouch.from_location)
        self.movement_part = self.pouch.delivery(self.lawsuit)
        self.save()


class LawsuitMatter(AuditTimestampModel):
    principal = models.BooleanField(default=False)
    matter = models.ForeignKey(
        LegalMatter, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="in_lawsuit_matter", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ("-principal",)

    def __str__(self):
        return "%s" % self.matter.path

    @property
    def icons(self):
        return {
            "iconCls": "icon-judicial icon-ejud-%s"
            % ("active" if self.principal else "unsigned"),
            "title": "Assunto %s" % ("principal" if self.principal else "secundário"),
        }

    def change_all_for_secondary(self):
        for lm in self.lawsuit.in_lawsuit_matter.exclude(pk=self.pk).filter(
            principal=True
        ):
            lm.principal = False
            lm.save()

    def define_principal(self):
        with transaction.atomic():
            if self.__class__.objects.get(pk=self.pk).principal is False:
                self.principal = True
                self.save()

    @classmethod
    def _register_matter(cls, lawsuit=None, matter=None, principal=False):
        obj = cls()
        obj.lawsuit = lawsuit
        obj.matter = matter
        obj.principal = principal

        obj.save()

    @classmethod
    def register_principal_matter(cls, lawsuit=None, matter=None):
        if None in [lawsuit, matter]:
            raise Exception("Parâmetros inválidos.")
        with transaction.atomic():
            lawsuit = OutCourtLawsuit.objects.get(pk=lawsuit.pk)
            lawsuit.in_lawsuit_matter.filter(principal=True).delete()
            cls._register_matter(lawsuit=lawsuit, matter=matter, principal=True)

    @classmethod
    def register_others_matters(cls, lawsuit=None, matters=[]):
        if not lawsuit:
            raise Exception("Informe o procedimento.")
        with transaction.atomic():
            lawsuit = OutCourtLawsuit.objects.get(pk=lawsuit.pk)
            lawsuit.in_lawsuit_matter.filter(principal=False).delete()

            for matter in matters:
                cls._register_matter(lawsuit=lawsuit, matter=matter, principal=False)

    @classmethod
    def get_principal_matter(cls, lawsuit=None):
        return lawsuit.main_matter if lawsuit else None

    @classmethod
    def get_others_matters(cls, lawsuit=None):
        return LegalMatter.objects.filter(
            pk__in=cls.objects.filter(lawsuit=lawsuit, principal=False).values("matter")
        )

    def save(self, *args, **kwargs):
        swap_principal = False

        if self.principal:
            swap_principal = True
        super(LawsuitMatter, self).save(*args, **kwargs)

        if swap_principal:
            self.change_all_for_secondary()


class DeadlineLog(models.Model):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    manifestation = models.ForeignKey(
        Manifestation, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    recomendation = models.ForeignKey(
        Recomendation, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(blank=True)
    days = models.SmallIntegerField()
    executed_at = models.DateTimeField()
    reverted_at = models.DateTimeField(null=True)

    def undo(self):
        if not self.reverted_at:
            if self.lawsuit:
                self._undo_for_lawsuit()
            elif self.manifestation:
                self._undo_for_manifestation()
            elif self.recomendation:
                self._undo_for_recomendation()
            else:
                raise Exception("undo not implemented")
        else:
            raise Exception("este log já foi revertido")

    def _mark_reverted(self):
        self.reverted_at = datetime.now()
        self.save()

    def _undo_for_lawsuit(self):
        lawsuit = self.lawsuit
        OutCourtLawsuit.objects.filter(pk=lawsuit.pk).update(
            remaining_days=(
                lawsuit.remaining_days + 1 if lawsuit.remaining_days else None
            ),
            deadline_cache=(
                lawsuit.deadline_cache - relativedelta(days=1)
                if lawsuit.deadline_cache
                else None
            ),
        )

        self._mark_reverted()

    def _undo_for_manifestation(self):
        m = self.manifestation

        Manifestation.objects.filter(pk=m.pk).update(
            remaining_days=(m.remaining_days + 1),
            deadline=(m.deadline - relativedelta(days=1) if m.deadline else None),
        )

        self._mark_reverted()

    def _undo_for_recomendation(self):
        Recomendation.objects.filter(pk=self.recomendation.pk).update(
            remaining_days=(self.recomendation.remaining_days + 1)
        )

        self._mark_reverted()

    @classmethod
    def register(
        cls,
        lawsuit=None,
        manifestation=None,
        recomendation=None,
        days=None,
        observation="",
    ):
        try:
            obj = cls()
            obj.lawsuit = lawsuit
            obj.manifestation = manifestation
            obj.recomendation = recomendation
            obj.days = days
            obj.observation = observation
            obj.executed_at = datetime.now()
            obj.save()

        except Exception as e:
            log.info("Não foi possível registrar em DeadlineLog.")
            log.info("%s " % e)
        else:
            return obj

    @classmethod
    def queryset_lawsuit_executed_to_date(cls, to_date=None):
        return OutCourtLawsuit.objects.filter(
            pk__in=cls.objects.filter(
                executed_at__year=to_date.year,
                executed_at__month=to_date.month,
                executed_at__day=to_date.day,
            ).values_list("lawsuit", flat=True)
        )

    @classmethod
    def queryset_manifestation_executed_to_date(cls, to_date=None):
        return Manifestation.objects.filter(
            pk__in=cls.objects.filter(
                executed_at__year=to_date.year,
                executed_at__month=to_date.month,
                executed_at__day=to_date.day,
            ).values_list("manifestation", flat=True)
        )

    @classmethod
    def queryset_recomendation_executed_to_date(cls, to_date=None):
        return Recomendation.objects.filter(
            pk__in=cls.objects.filter(
                executed_at__year=to_date.year,
                executed_at__month=to_date.month,
                executed_at__day=to_date.day,
            ).values_list("recomendation", flat=True)
        )


@type_part_lawsuit()
class SuspendDeadline(PartLawsuit):
    remaining_days = models.SmallIntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)

    codename = "Suspensão de Prazo"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    def sign_part(self):
        with transaction.atomic():
            super(SuspendDeadline, self).sign_part()
            self.lawsuit.remaining_days = None
            self.lawsuit.save()

    @classmethod
    def create(cls, lawsuit=None):
        obj = cls(remaining_days=lawsuit.remaining_days, lawsuit=lawsuit)
        obj.save()
        obj.sign_part()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.remaining_days = self.lawsuit.remaining_days

            if self.lawsuit.all_own_signed_documents.filter(
                suspenddeadline__active=True
            ).exists():
                raise Exception("O prazo do procedimento já encontra-se suspenso")

        super(SuspendDeadline, self).save(*args, **kwargs)


@type_part_lawsuit()
class ResumeDeadline(PartLawsuit):
    suspend_deadline = models.OneToOneField(
        SuspendDeadline, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Reestabelecer Prazo"

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"]

    def params(self):
        params = super(ResumeDeadline, self).params()

        params.update(
            suspend_deadline_event=self.suspend_deadline.has_event_controls.get(
                lawsuit=self.lawsuit
            )
        )

        return params

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    def sign_part(self):
        with transaction.atomic():
            self.lawsuit.remaining_days = self.suspend_deadline.remaining_days
            self.suspend_deadline.active = False
            self.suspend_deadline.skip_read_only_validate = True
            self.suspend_deadline.save()
            self.lawsuit.save()
            super(ResumeDeadline, self).sign_part()

    def save(self, *args, **kwargs):

        if not hasattr(self, "suspend_deadline"):
            try:
                self.suspend_deadline = self.lawsuit.all_signed_documents.get(
                    suspenddeadline__active=True
                ).my_origin
            except PartLawsuit.DoesNotExist:
                raise Exception("O prazo do procedimento não encontra-se suspenso.")
            except Exception:
                raise Exception(
                    "Ocorreu um erro ao buscar uma suspensão de prazo ativa."
                )

        super(ResumeDeadline, self).save(*args, **kwargs)


@type_part_lawsuit()
class ArchivingRemittance(PartLawsuit):
    department = models.ForeignKey(
        Lotacao, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Remessa com Arquivamento"

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def sign_part(self):
        with transaction.atomic():
            super(ArchivingRemittance, self).sign_part()

            self.lawsuit.send_to(to=self.department, finalizado=True)

            self.lawsuit.location = self.department
            self.lawsuit.remaining_days = None
            self.lawsuit.save()

    def save(self, *args, **kwargs):

        super(ArchivingRemittance, self).save(*args, **kwargs)


class MovementLog(models.Model):
    """OutCourtLawsuit movements log
    This class controls all Procedure movementations
    """

    out_court_lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="movements", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    from_location = models.ForeignKey(
        "rh.OrgaoGeral",
        related_name="+",
        verbose_name="Lotação origem",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    sended_by = models.ForeignKey(
        User, related_name="+", verbose_name="Enviado por", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    sended_at = models.DateTimeField(verbose_name="Enviado em")
    to_location = models.ForeignKey(
        "rh.OrgaoGeral",
        related_name="+",
        verbose_name="Lotação destino",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    received_by = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        verbose_name="Recebido por",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    received_at = models.DateTimeField(null=True, verbose_name="Recebido em")
    main_tag = models.ForeignKey(
        Tag, related_name="+", null=True, on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("out_court_lawsuit", "sended_by", "sended_at"),)
        ordering = ("out_court_lawsuit", "sended_at")

    @classmethod
    def register(klass, lawsuit, of, to):
        klass.objects.create(
            out_court_lawsuit=lawsuit,
            from_location=of,
            sended_by=get_current_user(),
            sended_at=datetime.now(),
            to_location=to,
            main_tag=lawsuit.main_tag,
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            tag = Tag.objects.get(slug="nao-recebido", tag_type=1)
            self.out_court_lawsuit.tags.add(tag)

        super(MovementLog, self).save(*args, **kwargs)


class RequestCollaboration(models.Model):
    """Collaboration Requests
    This class has the purpose of storing requests for collaboration of a procedure
    """

    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="%(class)s", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    origin_location = models.ForeignKey(
        OrgaoGeral,
        related_name="%(class)s",
        verbose_name="Departamento de origem",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    requested_by = models.ForeignKey(
        User,
        related_name="%(class)s",
        blank=True,
        null=True,
        verbose_name="Pedido por",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Pedido em")
    canceled_by = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Cancelado por",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    canceled_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Cancelado em"
    )
    received_by = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Recebido por",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    received_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Recebido em"
    )
    type_collaboration = models.CharField(max_length=60, null=True, blank=True)
    protocol_movement = models.OneToOneField(
        Movimentacao,
        related_name="%(class)s",
        null=True,
        blank=True,
        verbose_name="Certidão de recebimento",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    # TODO: Mudar pra protocol_movement o nome do último campo criado

    @property
    def my_origin(self):
        if self.pk:
            if hasattr(self, self.type_collaboration):
                obj = getattr(self, self.type_collaboration, self)

                return obj
            else:
                return self
        else:
            return self

    @property
    def target(self):
        raise NotImplementedError("Not implemented")

    def is_to_user(self, user):
        raise NotImplementedError("Not implemented")

    def inactivate(self):
        self.lawsuit.validate_ownership()

        self.canceled_by = get_current_user()
        self.canceled_at = datetime.now()
        self.save()

    def validate(self):
        if not self.lawsuit.is_received:
            raise Exception(
                "Não é possivel solicitar colaboração para um procedimento que ainda não foi recebido."
            )

    def fill_content(self):
        tpl = loader.get_template("judicial/request_collaboration.html")

        return tpl.render(
            {
                "lawsuit": self.lawsuit.cache_number,
                "origin_location": self.origin_location.nome,
            }
        )

    def create_protocol(self):
        """
        Este método cria um protocolo eletrônico para cientificar.
        Levanta uma exceção se o protocolo já foi criado anteriormente.
        """

        protocol = Protocolo.docketing(
            subject="Pedido de Colaboração - %s" % str(self.my_origin.target),
            document_type=TipoDocumento.objects.get(nome="CIENTIFICAÇÃO"),
            interested=person_from_user(get_current_user()),
            home_court=self.origin_location,
            content=self.fill_content(),
        )

        send_params = {}
        destination = {}

        if self.type_collaboration == "requestcollaborationperson":
            send_params.update(person_destination=self.my_origin.target.pk)
            destination.update(destinatario=self.my_origin.target)
        else:
            send_params.update(location_destination=self.my_origin.target.pk)
            destination.update(lotacao_destino=self.my_origin.target)

        send_params.update(
            employee_origin=employee_from_user(get_current_user()),
            physical=False,
            opinion=True,
        )

        current = Movimentacao.inbox_queryset().get(protocolo=protocol)
        current.do_send(**send_params)

        self.protocol_movement = current.derivative_for.get(**destination)
        self.save()

    @property
    def protocol(self):
        protocol = None

        if self.protocol_movement:
            protocol = self.protocol_movement.protocolo

        return protocol

    def save(self, *args, **kwargs):
        super(RequestCollaboration, self).save(*args, **kwargs)

        if not self.protocol_movement:
            self.create_protocol()

    def __str__(self):
        return "%s %s %s" % (
            self.requested_by,
            self.lawsuit.cache_number,
            self.my_origin.target,
        )


class RequestCollaborationPerson(RequestCollaboration):
    person = models.ForeignKey(
        Pessoa, related_name="collaborations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    @property
    def target(self):
        return self.person

    def is_to_user(self, user):
        return self.person.pk == person_from_user(user).pk

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type_collaboration = self._meta.model_name
            self.requested_by = get_current_user()

            self.validate()

            if person_from_user(self.requested_by) == self.person:
                raise Exception("Não é possível solicitar colaboração para você mesmo")

            employees = Servidor.objects.filter(pessoa_fisica=self.person, ativo=True)
            if employees.exists():
                ns = NotifyStack(
                    employee=employees.first(), out_court_lawsuits=self.lawsuit
                )
                ns.notify("EJUD_COLLABORATION")

        return super(RequestCollaborationPerson, self).save(*args, **kwargs)


class RequestCollaborationGeneralOrgan(RequestCollaboration):
    general_organ = models.ForeignKey(
        OrgaoGeral, related_name="collaborations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    @property
    def target(self):
        return self.general_organ

    def is_to_user(self, user):
        employee = employee_from_user(user)
        workplaces = [sl.lotacao for sl in employee.work_assignment_effective_exercise]

        return True if self.general_organ.lotacao in workplaces else False

    def validate(self):
        if self.general_organ == self.lawsuit.location.orgaogeral_ptr:
            raise Exception(
                "Não é possível solicitar colaboração para o mesmo local do procedimento"
            )

        if not self.general_organ.ativo:
            raise Exception(
                "Não é possível solicitar colaboração para um local de trabalho inativo"
            )

        super().validate()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type_collaboration = self._meta.model_name
            self.requested_by = get_current_user()

            self.validate()

            for employee in self.general_organ.lotacao.employees:
                ns = NotifyStack(employee=employee, out_court_lawsuits=self.lawsuit)
                ns.notify("EJUD_COLLABORATION")

        return super(RequestCollaborationGeneralOrgan, self).save(*args, **kwargs)


class Reminder(AuditTimestampModel):
    PUBLIC = 1
    WORKPLACE = 2

    title = models.CharField(max_length=200)
    reminder_state = models.SmallIntegerField(
        choices=((1, "Urgente"), (2, "Rápido"), (3, "Normal")), default=3
    )
    reminder_type = models.CharField(max_length=60, db_index=True, blank=True)
    content = models.TextField()
    deactivated_by = models.ForeignKey(
        "auth.User",
        related_name="closeds_reminder",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    workplace = models.ForeignKey(
        Lotacao,
        related_name="workplaces_reminder",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    access_level = models.SmallIntegerField(
        choices=(
            (PUBLIC, "Para todo Ministério Público"),
            (WORKPLACE, "Para o departamento"),
        ),
        default=1,
    )

    class Meta:
        ordering = ("reminder_state", "-created_at")

    @property
    def my_origin(self):
        if self.pk:
            if hasattr(self, self.reminder_type):
                return getattr(self, self.reminder_type, self)
            else:
                return self
        else:
            return self

    @property
    def target(self):
        raise NotImplementedError("Not implemented")

    @property
    def rendered(self):
        employee = employee_from_user(self.created_by)

        tpl = loader.get_template("judicial/reminder/default.html")
        return tpl.render({"reminder": self, "created_by": employee})

    def deactivate(self):
        self.deactivated_by = get_current_user()
        self.save()

    @property
    def _get_location_reminder(self):
        raise NotImplementedError("Not implemented")

    def save(self, *args, **kwargs):
        if self.access_level == self.WORKPLACE:
            self.workplace = self.my_origin._get_location_reminder

        super().save(*args, **kwargs)


class LawsuitReminder(Reminder):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="reminders", on_delete=models.CASCADE
    )

    @property
    def target(self):
        return self.lawsuit

    def __str__(self):
        return "Reminder Lawsuit (%d) %s" % (self.pk, self.lawsuit.cache_number)

    @property
    def _get_location_reminder(self):
        return self.lawsuit.location

    def save(self, *args, **kwargs):
        self.reminder_type = self._meta.model_name
        super().save(*args, **kwargs)


class PartLawsuitReminder(Reminder):
    part_lawsuit = models.ForeignKey(
        PartLawsuit, related_name="reminders", on_delete=models.CASCADE
    )

    @property
    def target(self):
        return self.part_lawsuit

    def __str__(self):
        return "Reminder Part (%d) %s" % (self.pk, self.part_lawsuit.pk)

    @property
    def _get_location_reminder(self):
        return self.part_lawsuit.lawsuit.location

    def save(self, *args, **kwargs):
        self.reminder_type = self._meta.model_name
        super().save(*args, **kwargs)


class StatisticMarker(AuditTimestampModel):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=240, db_index=True, blank=True)
    acting_zone = models.ForeignKey(
        ActingZone,
        related_name="exclusives_statistic_markers",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


@type_part_lawsuit()
class LegacyImport(
    _SyncBlockers, _SyncInterested, _SyncMatters, InitialPartlawsuit, PartLawsuit
):
    type_lawsuit = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_LAWSUIT"), default=0
    )
    external_code = models.CharField(max_length=100, null=True)
    import_number = models.PositiveIntegerField(null=True, blank=True)
    import_year = models.SmallIntegerField(null=True, blank=True)
    import_code = models.CharField(max_length=30, null=True, blank=True)
    legacy_title = models.TextField()
    instauration_date = models.DateField()
    remaining_days = models.IntegerField(default=0)
    major_interested = models.ForeignKey(
        "rh.Pessoa", related_name="+", on_delete=models.PROTECT
    )
    other_interesteds = models.ManyToManyField(
        "rh.Pessoa", related_name="as_other_interesteds_in_legacy_import"
    )
    main_matter = models.ForeignKey(
        LegalMatter, related_name="+", on_delete=models.PROTECT
    )
    other_matters = models.ManyToManyField(LegalMatter, related_name="in_legacy_import")
    blokers = models.ManyToManyField(
        "rh.Pessoa", related_name="as_blokers_in_legacy_import"
    )
    city_location = models.ForeignKey(
        "rh.Localidade", related_name="+", on_delete=models.PROTECT
    )
    location = models.ForeignKey(
        ExecutionOrgan, related_name="+", on_delete=models.PROTECT
    )

    codename = "Certidão de Importação de Procedimento Físico"

    only_responsible_sign = True
    allow_instated = True

    @property
    def sign_permissions(self):
        return ["judicial.can_sign_simples"] + PartLawsuit.sign_permissions.fget(self)

    def _calculate_deadline_date(self):
        return None

    def _lawsuit_type(self):
        return self.type_lawsuit

    def at_moment(self):
        i_date = self.instauration_date
        return datetime(i_date.year, i_date.month, i_date.day, 0, 0, 0, 1)

    @property
    def lawsuit_title(self):
        return self.legacy_title

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    def _next_import_number(self):
        Model = self.__class__

        max_number = (
            Model.objects.filter(import_year=self.import_year)
            .aggregate(max_number=models.Max("import_number"))
            .get("max_number", 0)
        )

        return int(max_number or 0) + 1

    def sign_part(self):
        """
        Este metodo é responsável por asinar a portaria de instauração.
        """
        if not self.main_matter:
            raise Exception("Campo assunto principal não preenchido.")

        if not self.major_interested:
            raise Exception("É necessário informar quem é o principal interessado.")

        if not self.acting_zone:
            raise Exception("É necessário informar a Área de Atuação.")

        if not self.attaches.exists():
            raise Exception("Para este documento é importante ter pelo menos um anexo.")

        self.type_lawsuit = int(self.type_lawsuit or 0)

        with transaction.atomic():
            self.import_year = date.today().year
            self.import_number = self._next_import_number()
            self.import_code = "%04d/%4d" % (self.import_number, self.import_year)
            self.save()

            self.sync_interesteds()
            self.sync_matters()
            self.sync_blokers()

            if not self.is_instanted:
                self._sign_lawsuit_prepare()

            self.lawsuit.title = self.legacy_title
            self.lawsuit.type_lawsuit = self.type_lawsuit
            self.lawsuit.main_matter = self.main_matter
            self.lawsuit.remaining_days = self.remaining_days
            self.lawsuit.save()

            self.page_number = 1
            self.cache_rendered = None
            super().sign_part()

            self.signed_at = datetime.now()
            self.signed_by = get_current_user()
            self.dispatch_comunication(
                subject="Comunicar a %s" % str(self), external_number=self.import_code
            )

            # FIXME isto deve ser reescrito após implementação da edicação compartilhada de documento.
            current_moviment = None
            if self.lawsuit.origin.movimentacoes.filter(passo__gt=0).exists():
                current_moviment = self.lawsuit.current_moviment()
            else:
                current_moviment = self.lawsuit.origin.movimentacoes.last()

            old_fn = current_moviment.validate_possession_for_do_send

            def empty_fn(*args, **kwargs):
                pass

            current_moviment.validate_possession_for_do_send = empty_fn

            self.lawsuit.send_to(
                to=self.lawsuit.location, force_current=current_moviment
            )
            current_moviment.validate_possession_for_do_send = old_fn

    def save(self, *args, **kwargs):
        created = self.pk is None
        if not getattr(self, "lawsuit", None) and self.location:
            log.info("creating lawsuit...")
            self.interested = self.major_interested
            self.lawsuit = self._create_lawsuit()
        elif not getattr(self, "lawsuit", None) and not self.location:
            raise Exception(
                "Para instauração inicial, deve ser informado o local de instauração."
            )

        if self.lawsuit and not self.lawsuit.origin and self.major_interested:
            self.interested = self.major_interested
            self.lawsuit.origin = self._docketing_protocol()

        self.lawsuit.title = self.legacy_title
        self.lawsuit.save()

        if not self.major_interested and self.lawsuit and self.lawsuit.origin:
            self.major_interested = self.lawsuit.origin.interessado

        if not self.main_matter:
            self.main_matter = LawsuitMatter.get_principal_matter(lawsuit=self.lawsuit)

        super().save(*args, **kwargs)

        if created:
            for lm in self.lawsuit.in_lawsuit_matter.exclude(
                matter__in=self.other_matters.filter()
            ).filter(principal=False):
                self.other_matters.add(lm.matter)

        if self.major_interested:
            for interested in self.lawsuit.interested.exclude(
                pk__in=self.other_interesteds.filter()
            ).exclude(pk=self.major_interested.pk):
                self.other_interesteds.add(interested)

        for bloke in self.lawsuit.blokes.exclude(pk__in=self.blokers.filter()):
            self.blokers.add(bloke.my_origin.bloke)


class Secretary(AuditTimestampModel):
    title = models.CharField(max_length=100)
    location = models.ForeignKey(
        "rh.Lotacao", related_name="seretary", on_delete=models.CASCADE
    )
    execution_organs = models.ManyToManyField(
        ExecutionOrgan, related_name="as_secretaries"
    )

    def __str__(self):
        return self.title


class AuditDispatchSecretary(AuditTimestampModel):
    lawsuit = models.ForeignKey(
        OutCourtLawsuit, related_name="dispatches", on_delete=models.PROTECT
    )
    location = models.ForeignKey(
        "rh.Lotacao", related_name="dispatches", on_delete=models.CASCADE
    )
    secretary = models.ForeignKey(
        Secretary, related_name="dispatches", on_delete=models.PROTECT
    )
    type_dispatch = models.SmallIntegerField(
        choices=Choice.get_choices_for("judicial", "TYPE_AUDIT_DISPATCH_SECRETARY"),
        default=1,
        verbose_name="Tipo de despacho",
    )


class NoticeConfiguration(models.Model):
    type_ordinace = models.PositiveSmallIntegerField(
        verbose_name="Tipo", choices=TYPE_ORDINACE
    )
    legal_classification = models.ForeignKey(
        LegalClassification, verbose_name="Classificação", on_delete=models.PROTECT
    )
    departament = models.ManyToManyField(
        "rh.Lotacao", verbose_name="Departamento", related_name="departaments"
    )

    @property
    def departament_display(self):
        return " - ".join(self.departament.all().values_list("sigla", flat=True))

    class Meta:
        unique_together = ("type_ordinace", "legal_classification")
