# -*- coding:utf-8 -*-

from base64 import b64encode
import datetime
import hashlib
import os
import shutil
from statistics import mode
import tempfile
import uuid

from threading import Thread
from django.contrib.auth.models import User

from django.db import models, transaction
from django.db.models.fields import BooleanField, DateField, DateTimeField
from django.db.models.signals import post_save
from django.dispatch import receiver

from common.official_journal.odm import JournalODM
from contrib import mongo
from contrib.helpers import pdf_extract_text
from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user
from edocs.protocolo.models import LegalSign, Protocolo
from ged.models import Arquivo as File
from standard.models import AuditTimestampModel

from rh.models import OrgaoGeral

from django.template import loader


log = getLogger()


class JournalBase(AuditTimestampModel):
    UID = models.CharField(blank=True, max_length=50, db_index=True)
    name = models.CharField(blank=True, max_length=150)
    published_date = models.DateTimeField(blank=True, null=True, db_index=True)
    ged = models.ForeignKey(
        File,
        blank=True,
        null=True,
        related_name="official_journals",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    text = models.TextField(blank=True)

    class Meta:
        ordering = ["published_date"]

    def save(self, *args, **kwargs):

        if not self.UID:
            self.UID = str(uuid.uuid4())

        log.debug(
            "Ged?: %s, Was changed?: %s, text?: %s"
            % (bool(self.ged), self.ged_was_changed(), len(self.text) > 0)
        )

        if self.ged and self.ged.mimetype != "application/pdf":
            raise Exception("O arquivo do diário oficial deve ser no formato pdf.")

            # log.debug('Starting task')
            # Thread(target=extract_and_save_text, args=(self.UID, log)).start()
            # Task.start(extract_text, uuid=self.UID)

            # name = '%s.pdf' % self.ged.file
            # filename = os.path.join(tempfile.gettempdir(), name)
            # shutil.copy(self.ged.absolute_path, filename)
            # log.info('Extract text from Journal with UUID %s', self.UID)
            # '''
            # FIXME: Deve ser verificado qual problema esta ocorrendo no processamento
            # do diário 953 foi desabilitado para que não fosse penalizada a publicação.
            # seria interessando levar esta implementação para o celery
            # '''
            # # self.text = pdf_extract_text(filename)
            # log.info('Done')

            # os.remove(filename)
        log.debug("Saving")
        super(JournalBase, self).save(*args, **kwargs)

    def ged_was_changed(self):
        db = mongo.connect().get_database("fulltextIndex")
        doc = db.officialJournals.find_one({"UID": self.UID}) or {}
        return doc.get("hash") != self.ged.file

    @property
    def file_hash(self):
        return self.ged.file if self.ged else ""

    @property
    def file_url(self):
        return self.ged.complete_permalink() if self.ged else ""

    @property
    def year(self):
        date = self.published_date if self.published_date else self.created_at
        return date.year

    @property
    def month(self):
        date = self.published_date if self.published_date else self.created_at
        return date.month

    def delete(self, *args, **kwargs):
        if self.published_date:
            raise Exception("Não é permitido deletar um item já publicado.")

        db = mongo.connect().get_database("fulltextIndex")
        db.officialJournals.delete_one({"UID": self.UID})

        super(JournalBase, self).delete(*args, **kwargs)

    def publish(self, date=None):
        if not self.ged:
            raise Exception("Não é permitido publicar sem documento anexado.")

        if not self.published_date:
            self.published_date = datetime.datetime.now() if not date else date

    @classmethod
    def published(cls, date=None):
        if not date:
            date = datetime.datetime.now()
        return models.Q(published_date__lte=date)

    def __str__(self):
        return str(self.name)


class Journal(JournalBase):
    code = models.IntegerField(blank=True, db_index=True)
    extra = models.BooleanField(default=False)

    journalbase_ptr = models.OneToOneField(
        JournalBase,
        parent_link=True,
        related_name="journal_child",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-code"]

    @classmethod
    def get_code(cls):
        last_journal = cls.objects.order_by("-code").first()
        if not last_journal:
            return 1
        return last_journal.code + 1

    @property
    def fullname(self):
        year = self.published_date.year if self.published_date else self.created_at.year
        extra = "- EDIÇÃO EXTRA" if self.extra else ""
        return "%s de %s %s" % (self.name, year, extra)

    def save(self, *args, **kwargs):

        if not self.code:
            self.code = Journal.get_code()

        self.name = "Diário Oficial Nº %s" % self.code
        super(Journal, self).save(*args, **kwargs)

        JournalODM().mapper.save(self)

    def __str__(self):
        return self.fullname


class Suplement(JournalBase):
    # Parametro "on_delete" adicionado. (Django 2)
    journal = models.ForeignKey(
        Journal, related_name="suplements", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        super(Suplement, self).save(*args, **kwargs)

        JournalODM().mapper.save(self.journal)


@receiver(post_save, sender=Journal)
def extract_and_save_text(sender, **kwargs):
    ilog = getLogger()
    instance = kwargs.get("instance")
    user = get_current_user()
    ilog.debug("instance: %s, current_user: %s" % (instance, user))
    Thread(target=process_extract_and_save_text, args=(instance, user)).start()


def process_extract_and_save_text(instance, current_user):
    ilog = getLogger()
    ilog.debug("Thread params %s:%s" % (instance, current_user))
    set_current_user(current_user)
    if instance.ged and (instance.ged_was_changed() or not instance.text):
        try:
            with transaction.atomic():
                name = "%s.pdf" % instance.ged.file
                filename = os.path.join(tempfile.gettempdir(), name)
                shutil.copy(instance.ged.absolute_path, filename)
                ilog.debug("File %s exists?: %s" % (filename, os.path.exists(filename)))
                ilog.debug("Extract text from Journal UUID %s", instance.UID)

                instance.text = pdf_extract_text(filename)
                ilog.debug(instance.text)
                instance.save()
                os.remove(filename)
                ilog.debug("Done")
        except Exception as e:
            ilog.exception(e)
            ilog.debug(e)


class OfficialDiary(AuditTimestampModel):
    title = models.CharField(max_length=200, blank=True, null=True)
    create_date = models.DateField(auto_now_add=True, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    published_for = models.CharField(max_length=200, blank=True, null=True)
    filename = models.CharField(max_length=300, null=True, blank=True)
    signed_by = models.ForeignKey(
        "auth.user",
        related_name="as_signed_by_in_doe",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = (
            ("can_sign", "Pode assinar qualquer documento"),
            (
                "can_sign_simples",
                "Pode assinar qualquer documento classificado como simples",
            ),
            ("can_unfold_any_document", "Pode desentranhar qualquer documento"),
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-create_date", "-published_date")

    @property
    def my_origin(self):
        return self

    @property
    def can_read(self):
        """Retorna True se o usuário corrente estiver autorizado a ler
        o conteúdo do documento. Caso contrário, retorna False.

        Verifica se este procotolo possui controle de acesso. Se possui,
        então verifica se o usuário corrente está autorizado a ler o seu
        conteúdo. Mas se não existe controle de acesso, retorna True por
        padrão.
        """
        if hasattr(self, "doe_control"):
            return self.doe_control.can_read
        return True

    @property
    def rendered(self):
        if self.can_read:
            return loader.get_template("official_diary/legal_sign_doe.html").render(
                {"instance": self}
            )
        else:
            return loader.get_template("protocolo/access-denied.html").render(
                {"protocol": self.protocol}
            )

    @property
    def get_doe_legal_sign(self):
        return DoeLegalSign

    @property
    def need_sign(self):
        # verificação:se o documento ja foi assinado retornar mensagem..
        return False

    @property
    def sign_permissions(self):
        return ["official_journal.can_sign"]

    @property
    def sign_doe_authorized(self):
        return self._sign_doe_authorized()

    def _sign_doe_authorized(self):
        user = get_current_user()

        flag = False
        for perm in self.sign_permissions:
            if user.has_perm(perm):
                flag = True
                break

        return flag

    def sign_doe(self):

        if self.sign_doe_authorized:
            self.signed_by = get_current_user()
            self.my_origin.get_doe_legal_sign.sign(self.my_origin)
            self.signed_at = datetime.datetime.now()
            self.save()

        else:
            raise Exception(
                "O usuário %s não tem permissão para assinar esse documento"
                % get_current_user()
            )

    def save(self, *args, **kwargs):

        if not self.title:
            code = Journal.get_code()
            self.title = "Diário Preliminar Nº %s" % code

        super(OfficialDiary, self).save(*args, **kwargs)


class Document(AuditTimestampModel):
    official_diary = models.ForeignKey(
        "OfficialDiary",
        related_name="documents",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    department_origin = models.ForeignKey(
        OrgaoGeral, related_name="department_origin", on_delete=models.PROTECT
    )
    protocol = models.ForeignKey(
        Protocolo, related_name="diary_protocol", on_delete=models.CASCADE
    )
    content = models.TextField(blank=True)
    send_date = DateField(auto_now_add=True, null=True)
    ativo = BooleanField(default=True)

    def __str__(self):
        return self.protocol.codigo

    class Meta:
        ordering = ("-send_date",)

    def status_icons(self):
        return [
            {
                "title": (
                    "ativo"
                    if self.ativo and self.official_diary != None
                    else (
                        "aguardando"
                        if self.ativo and self.official_diary == None
                        else "pendente"
                    )
                ),
                "iconCls": (
                    "icon-16px icon-core icon-core-success"
                    if self.ativo and self.official_diary != None
                    else (
                        "icon-16px icon-crgmpe icon-crgmpe-waiting"
                        if self.ativo and self.official_diary == None
                        else "icon-16px icon-core icon-core-warn"
                    )
                ),
            }
        ]


class Devolution(AuditTimestampModel):
    devolution = models.TextField()
    devolution_date = DateTimeField(auto_now_add=True, null=True)
    devolution_for = models.ForeignKey(
        User, related_name="devolution_for", blank=True, on_delete=models.PROTECT
    )
    document = models.ForeignKey(
        Document, related_name="document", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.devolution_for = get_current_user()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-devolution_date",)


class DiaryOrder(AuditTimestampModel):
    title = models.CharField(max_length=255)
    general_organ = models.ManyToManyField(OrgaoGeral, related_name="general_organ")
    order = models.IntegerField(unique=True)

    def __str__(self):
        return self.title

    # def general_organ_unicode(self):
    #     return str(self.general_organ)


class OfficialDiaryLegalSign(object):
    # renderizar template
    @property
    def rendered(self):
        tpl = loader.get_template("official_diary/legal_sign_doe.html")
        return tpl.render({"sign": self})


class DoeLegalSign(OfficialDiaryLegalSign, LegalSign):
    doe = models.ForeignKey(
        OfficialDiary, related_name="legal_sign_doe", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s" % (self.doe.title)

    # carregamento do conteudo da assinatura pelo LegalSign
    def _fill(self, doe):
        super(DoeLegalSign, self)._fill()
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha224", self.content).hexdigest()
        self.plain_content = self.rendered

        log.debug("@ aki" * 80)
        log.debug(self.plain_content)

    @classmethod
    def sign(klass, doe):
        obj = klass()
        obj.doe = doe
        obj._fill(doe)
        obj.save()

        return obj
