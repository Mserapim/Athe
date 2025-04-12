# -*- coding: utf-8 -*-
from nis import cat
from standard.models import AuditTimestampModel
from django.db import models
from django.db.models import Q
from rh.models import Lotacao as Location, Servidor as Employee
from rh.afastamento.models import BaseLicencaAfastamento
from judicial.models import (
    LegalClass,
    LegalMatter,
    LegalClassification,
    LegalProcedure,
    LegalMoviment as LegalMovement,
)
from django.contrib.auth.models import User
from contrib.utils import getLogger, employee_from_user, DateUtils, person_from_user
from contrib.daterange import NewDateRange
from django.db.models import Max
from contrib.middleware import get_current_user
from django.template import loader
from standard.models import Configuration, Choice
from edocs.protocolo.models import Movimentacao, Protocolo, TipoDocumento
from datetime import datetime, time, timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


log = getLogger(__name__)


class YearBase(AuditTimestampModel):
    """
    Ano referência para o questionário
    """

    title = models.CharField(max_length=4, unique=True)
    activated = models.BooleanField(default=True)
    valid_of = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-title", "-valid_of"]
        verbose_name = "Ano Base"

    def __str__(self):
        return str(self.title)

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        rst = []

        if self.activated:
            rst.append({"title": "Ativo", "iconCls": "icon-raf icon-raf-activated"})
        else:
            rst.append(
                {"title": "Desativado", "iconCls": "icon-raf icon-raf-deactivated"}
            )

        return rst


class TypeQuiz(AuditTimestampModel):
    """
    Tipo de questionário
    """

    title = models.CharField(max_length=100, unique=True)
    group = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("raf", "GROUP"),
        verbose_name="Grupo",
    )
    species = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("raf", "SPECIES"),
        verbose_name="Espécie",
    )

    class Meta:
        verbose_name = "Tipo de Questionário"

    def __str__(self):
        return (
            (str(self.get_group_display() + " - ") if self.group else "")
            + (str(self.get_species_display() + " - ") if self.species else "")
            + self.title
        )


class FunctionalActivityReport(AuditTimestampModel):
    """
    Relatório de atividade funcional do membro
    """

    employee = models.ForeignKey(
        Employee, related_name="functionalactivityreports", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    closed = models.BooleanField(default=False)
    yearbase = models.ForeignKey(
        YearBase, related_name="functionalactivityreports", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    submitted_by = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    submitted_at = models.DateTimeField(null=True, blank=True)
    departure = models.BooleanField(default=False)
    departures = models.ManyToManyField(BaseLicencaAfastamento, related_name="+")
    open_date = models.DateTimeField(null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "RAF"
        ordering = ["-year", "month"]
        unique_together = ("employee", "year", "month")
        permissions = (("can_management_raf", "Pode gerenciar o RAF"),)

    def __str__(self):
        return str(self.employee)

    @property
    def previous_raf(self):
        previous_month = self.month - 1 if self.month > 1 else 12
        previous_year = self.year if self.month > 1 else self.year - 1
        previous = FunctionalActivityReport.objects.filter(
            employee=self.employee, month=previous_month, year=previous_year
        ).first()
        return previous

    @property
    def next_raf(self):
        next_month = self.month + 1 if self.month < 12 else 1
        next_year = self.year + 1 if self.month == 12 else self.year
        next_raf = FunctionalActivityReport.objects.filter(
            employee=self.employee, month=next_month, year=next_year
        ).first()
        return next_raf

    @property
    def submitted(self):
        return self.submitted_by is not None

    @property
    def icons(self):
        # return self.icons_list
        return self.icons_status

    def get_departures(self):
        ret = ""
        for d in self.departures.all().order_by("data_inicio"):
            ret = ret + "<br />- <b>%s: %s à %s</b>" % (
                d.situation_unicode,
                DateUtils.date_to_str(d.data_inicio),
                DateUtils.date_to_str(d.data_fim) if d.data_fim else "----",
            )
        return ret

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.closed:
            item = {"title": "Fechado", "iconCls": "icon-raf icon-raf-close"}
        else:
            item = {"title": "Aberto", "iconCls": "icon-raf icon-raf-open"}
        if self.submitted:
            item = {"title": "Submetido", "iconCls": "icon-raf icon-raf-tick"}
        rst.append(item)
        if self.departure:
            item = {
                "title": "Membro afastado no período %s" % (self.get_departures()),
                "iconCls": "icon-core icon-core-set-employee",
            }
            rst.append(item)
        return rst

    @property
    def icons_list(self):
        item = None
        rst = []
        if self.closed:
            item = {"title": "Fechado", "iconCls": "icon-raf icon-raf-close"}
        else:
            item = {"title": "Aberto", "iconCls": "icon-raf icon-raf-open"}
        rst.append(item)
        if self.submitted:
            item = [{"title": "Submetido", "iconCls": "icon-raf icon-raf-tick"}]
            rst = rst + item
        if self.departure:
            item = [
                {
                    "title": "Membro afastado no período %s" % (self.get_departures()),
                    "iconCls": "icon-core icon-core-set-employee",
                }
            ]
            rst = rst + item
        return rst

    def submit(self):
        test = self.previous_raf.submitted if self.previous_raf else True
        if test:
            employee = employee_from_user(get_current_user())
            if self.closed:
                historic = HistoricRAF()
                historic.raf = self
                historic.action = 6
                historic.save()
                raise Exception(
                    "Você não pode submeter o RAF, pois encontra-se fechado."
                )
            if self.submitted:
                historic = HistoricRAF()
                historic.raf = self
                historic.action = 7
                historic.save()
                raise Exception("RAF já submetido")
            if self.employee.pk != employee.pk:
                historic = HistoricRAF()
                historic.raf = self
                historic.action = 8
                historic.save()
                raise Exception("Você não pode submeter o RAF.")
            if (
                ActivityAdjustment.objects.filter(
                    activity__workerlocation__raf=self, situation__in=[0, 1]
                ).count()
                > 0
            ):
                historic = HistoricRAF()
                historic.raf = self
                historic.action = 10
                historic.save()
                raise Exception(
                    "Você não pode submeter o RAF.<br/>Existem pedidos de ajuste aguardando análise."
                )
            else:
                self.submitted_by = get_current_user()
                self.submitted_at = datetime.now()
                self.save()
                historic = HistoricRAF()
                historic.raf = self
                historic.action = 4
                historic.save()
                self.close()
        else:
            historic = HistoricRAF()
            historic.raf = self
            historic.action = 9
            historic.save()
            raise Exception(
                "Você não pode submeter o RAF atual enquanto o RAF do mês anterior, %s/%s, não for submetido."
                % (self.previous_raf.month, self.previous_raf.year)
            )

    def deadline_extend_by_days(self, days):
        try:
            if self.departure is False:
                self.open_date = datetime.today()
                self.close_date = datetime.today() + timedelta(days=days)
                self.open()
        except Exception as e:
            raise e

    def open(self):
        self.closed = False
        self.submitted_by = None
        self.submitted_at = None
        self.save()
        historic = HistoricRAF()
        historic.raf = self
        historic.action = 2
        historic.save()

    def close(self):
        self.closed = True
        self.save()
        historic = HistoricRAF()
        historic.raf = self
        historic.action = 3
        historic.save()

    def addWorkerLocation(self, location):
        wl = WorkerLocation()
        wl.location = Location.objects.get(pk=location)
        wl.raf = self
        wl.save()

    @classmethod
    def _get_or_create_raf(cls, employee, month, year):
        raf = FunctionalActivityReport.objects.filter(
            employee=employee, month=month, year=year
        ).first()
        if raf is None:
            raf = FunctionalActivityReport()
            raf.employee = employee
            raf.month = month
            raf.year = year
            raf.yearbase = YearBase.objects.get(activated=True)
            raf.closed = True
            raf.save()
        return raf

    @classmethod
    def _get_raf_locations_employee(cls, employee, month, year):
        month_reference = NewDateRange.from_month(month=month, year=year)
        listaD = employee._raw_locations()

        return listaD.filter(
            ~Q(lotacao__executionorgan=None)
            & Q(designacao=True)
            & Q(
                Q(
                    data_vigencia_inicio__range=[
                        month_reference.first,
                        month_reference.last,
                    ]
                )
                | Q(
                    Q(data_vigencia_inicio__lte=month_reference.first)
                    & Q(
                        Q(
                            data_vigencia_fim__range=[
                                month_reference.first,
                                month_reference.last,
                            ]
                        )
                        | Q(data_vigencia_fim__gte=month_reference.last)
                        | Q(data_vigencia_fim=None)
                    )
                )
            )
        )

    @classmethod
    def create_raf_from(cls, list_employee=None, month=None, year=None):

        for membro in list_employee.order_by("pessoa_fisica__nome"):
            if membro.ativo:
                raf = cls._get_or_create_raf(membro, month, year)

                listaExercicio = cls._get_raf_locations_employee(membro, month, year)

                for d in listaExercicio.order_by("lotacao__nome"):
                    WorkerLocation.get_or_create_workerlocation(raf, d.lotacao)

                for special in SpecialOrgan.objects.filter(
                    location__responsavel=membro
                ):
                    raf = cls._get_or_create_raf(
                        special.location.responsavel, month, year
                    )
                    WorkerLocation.get_or_create_workerlocation(raf, special.location)

    def save(self, *args, **kargs):
        created = False
        if self.pk is None:
            created = True
        super(FunctionalActivityReport, self).save(*args, **kargs)
        if created is True:
            historic = HistoricRAF()
            historic.raf = self
            historic.action = 1
            historic.save()

    @classmethod
    def _person_list_can_receive_edoc(cls, rafs):

        member_person = rafs.filter(
            employee__pessoa_fisica__enable_protocol=True
        ).values_list("employee__pessoa_fisica__pk", flat=True)

        trust_person = TrustRelationship.objects.filter(
            employee__pessoa_fisica__in=rafs.values_list(
                "employee__pessoa_fisica__pk", flat=True
            ),
            activated=True,
            trust_employee__pessoa_fisica__enable_protocol=True,
        ).values_list("trust_employee__pessoa_fisica__pk", flat=True)

        return list(member_person.union(trust_person))

    @classmethod
    def send_doc_comunicate(cls, month: int, year: int, subject: str, content: str):
        try:
            rafs = cls.objects.filter(month=month, year=year)
            persons = cls._person_list_can_receive_edoc(rafs)

            cfg = Configuration.get_or_create("raf")
            home_court = Location.objects.filter(pk=int(cfg.get("location", 0))).first()

            if not home_court:
                raise Exception("Lotacao de origem nao definida.")

            protocol = Protocolo.docketing(
                subject=subject,
                document_type=TipoDocumento.objects.filter(
                    pk=int(cfg.get("documentType", 0))
                ).first(),
                interested=person_from_user(get_current_user()),
                home_court=home_court,
                content=content,
            )

            current = Movimentacao.inbox_queryset().get(protocolo=protocol)

            current.do_send(
                person_destination=persons,
                employee_origin=employee_from_user(get_current_user()),
                physical=False,
                opinion=True,
                use_async=True,
            )
        except Exception as e:
            raise e


class HistoricRAF(AuditTimestampModel):
    """
    Histórico de ação realizadas no RAF de um membro
    """

    raf = models.ForeignKey(
        FunctionalActivityReport, related_name="historics", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    action = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("raf", "HISTORIC_RAF"),
        verbose_name="Ação",
        default=1,
    )

    class Meta:
        verbose_name = "Histórico do RAF"


class WorkerLocation(AuditTimestampModel):
    """
    Relação promotoria/raf
    """

    location = models.ForeignKey(
        Location, related_name="workerlocations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    raf = models.ForeignKey(
        FunctionalActivityReport,
        related_name="workerlocations",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Promotoria"
        ordering = ["location"]
        unique_together = ("location", "raf")

    def __str__(self):
        return "%s - %s" % (self.location, self.raf)

    @classmethod
    def get_or_create_workerlocation(cls, raf, location):
        worklocation = WorkerLocation.objects.filter(raf=raf, location=location).first()
        if worklocation is None:
            worklocation = cls()
            worklocation.raf = raf
            worklocation.location = location
            worklocation.save()
        return worklocation


class Quiz(AuditTimestampModel):
    """
    Questionário
    """

    typequiz = models.ForeignKey(
        TypeQuiz, related_name="quizzes", on_delete=models.PROTECT
    )
    yearbase = models.ForeignKey(
        YearBase, related_name="quizzes", on_delete=models.PROTECT
    )
    activated = models.BooleanField(default=True)
    number_order = models.PositiveSmallIntegerField(null=True, blank=True)
    legalclasses = models.ManyToManyField(LegalClass, related_name="quizzes")
    exclude_classes = models.ManyToManyField(LegalClass, related_name="exclude_quizzez")

    class Meta:
        verbose_name = "Questionário"
        ordering = ["yearbase", "number_order", "typequiz__title"]
        unique_together = ("typequiz", "yearbase", "activated")

    def __str__(self):
        return "%s - %s " % (self.typequiz, self.yearbase)

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        rst = []

        if self.activated:
            rst.append({"title": "Ativo", "iconCls": "icon-raf icon-raf-activated"})
        else:
            rst.append(
                {"title": "Desativado", "iconCls": "icon-raf icon-raf-deactivated"}
            )

        return rst

    def __copy_taxonomy_to_item(self, item=None, old=None):

        bulk = []
        for obj in old.taxonomyclassification_set.all():
            bulk.append(
                TaxonomyClassification(
                    item=item if hasattr(item, "subitems") else None,
                    subitem=item if hasattr(item, "items") else None,
                    classification=obj.classification,
                    exclude_classification=obj.exclude_classification,
                    created_by=get_current_user(),
                    modified_by=get_current_user(),
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                )
            )

        TaxonomyClassification.objects.bulk_create(bulk)

    def __create_copy_item(self, item=None, quiz=None, nocnmp=False):

        old = item.__class__.objects.get(pk=item.pk)

        item.pk = None
        item.id = None
        item.quiz_id = None
        item.quiz = quiz

        item.created_by = get_current_user()
        item.modified_by = get_current_user()
        item.created_at = datetime.now()
        item.modified_at = datetime.now()

        # if hasattr(item, 'items'):
        #     item.items.clear()
        # elif hasattr(item, 'subitems'):
        #     item.subitems.clear()
        if nocnmp:
            item.cnmp = False

        item.save()

        self.__copy_taxonomy_to_item(item=item, old=old)

    def create_from(self, yearbase=None, typequiz=None):

        try:

            if not (
                YearBase.objects.filter(pk=yearbase).exists()
                and TypeQuiz.objects.filter(pk=typequiz).exists()
            ):
                raise Exception("Ano base ou tipo do questionário não informado.")

            legalclass = self.legalclasses.all()
            exclude_classes = self.exclude_classes.all()

            quiz = Quiz(
                yearbase=YearBase.objects.get(pk=yearbase),
                typequiz=TypeQuiz.objects.get(pk=typequiz),
                activated=self.activated,
            )

            quiz.number_order = Quiz.next_number_order(quiz)
            quiz.save()
            quiz.legalclasses.add(*legalclass)
            quiz.exclude_classes.add(*exclude_classes)

            for item in self.item_set.all():
                self.__create_copy_item(item=item, quiz=quiz)

            for item in self.subitem_set.all():
                self.__create_copy_item(item=item, quiz=quiz)

            for item in quiz.item_set.filter():
                for subitem in quiz.subitem_set.filter():
                    item.subitems.add(subitem)

        except Exception as e:
            raise e

    @classmethod
    def next_number_order(cls, instance):
        value = (
            Quiz.objects.filter(yearbase=instance.yearbase)
            .aggregate(Max("number_order"))
            .get("number_order__max")
        )
        return value + 1 if value else 1

    def swap_order(self, other):
        """Troca a ordem do questionário por outro.

        Args:
            other (Quiz): Questionario que sera trocado.

        """
        number = self.number_order

        self.number_order = other.number_order
        other.number_order = number

        self.save()
        other.save()

    def save(self, *args, **kargs):
        if self.pk is None:
            self.number_order = Quiz.next_number_order(self)

        super(Quiz, self).save(*args, **kargs)

    def delete(self, *args, **kargs):

        for quiz in Quiz.objects.filter(
            yearbase=self.yearbase, number_order__gt=self.number_order
        ):
            quiz.number_order -= 1
            quiz.save()

        super(Quiz, self).delete(*args, **kargs)

    def force_ordenation_item(self):
        order = 1
        for item in self.item_set.filter():
            Item.objects.filter(pk=item.pk).update(number_order=order)
            order += 1

    def force_ordenation_subitem(self):
        order = 1
        for item in self.subitem_set.filter():
            SubItem.objects.filter(pk=item.pk).update(number_order=order)
            order += 1

    @classmethod
    def __copy_itens_origem_destination(cls, quiz_origem, quiz_destination):
        origem = cls.objects.get(pk=quiz_origem)
        destino = cls.objects.get(pk=quiz_destination)

        exclude_itens_title = destino.item_set.filter().values_list("title", flat=True)
        exclude_subitens_title = destino.subitem_set.filter().values_list(
            "title", flat=True
        )

        for item in origem.item_set.exclude(title__in=exclude_itens_title):
            origem.__create_copy_item(item=item, quiz=destino, nocnmp=True)
            # print(item)

        for item in origem.subitem_set.exclude(title__in=exclude_subitens_title):
            origem.__create_copy_item(item=item, quiz=destino, nocnmp=True)
            # print(item)

        for item in destino.item_set.filter():
            for subitem in destino.subitem_set.filter():
                item.subitems.add(subitem)


class ItemBase(AuditTimestampModel):
    """
    Modelo comum à itens e seus sub-itens
    """

    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    activated = models.BooleanField(default=True)
    cnmp = models.BooleanField(default=True)
    number_order = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["quiz__number_order", "number_order"]
        unique_together = ("quiz", "title")

    def __str__(self):
        return "%s" % self.title

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        rst = []

        if self.activated:
            rst.append({"title": "Ativo", "iconCls": "icon-raf icon-raf-activated"})
        else:
            rst.append(
                {"title": "Desativado", "iconCls": "icon-raf icon-raf-deactivated"}
            )

        if self.cnmp:
            rst.append({"title": "CNMP", "iconCls": "icon-raf icon-raf-cnmp"})

        return rst

    @classmethod
    def next_number_order(cls, instance):
        """
        Verifica qual e o maior numero ja gerado para a referida categoria
        (item ou subitem), entao cria-se um novo numero de ordem. Caso ainda
        nao exista um numero, e retornado o valor "1" como ponto de partida.
        """

        value = (
            instance.__class__.objects.filter(quiz=instance.quiz)
            .aggregate(Max("number_order"))
            .get("number_order__max")
        )

        return (value or 0) + 1

    def sync_created_obj(self):
        """
        sincroniza o item recem criado para que possua os mesmos
        subitems dos demais itens no questionario em questao.

        sincroniza o subitem recem criado para que seja
        relacionado com todos os itens do mesmo questionario.
        """
        if self._meta.model_name == "item":
            for si in SubItem.objects.filter(quiz=self.quiz):
                si.items.add(self)
        elif self._meta.model_name == "subitem":
            for i in Item.objects.filter(quiz=self.quiz):
                i.subitems.add(self)

    def swap_order(self, other):
        """Troca a ordem do item por outro.

        Args:
            other (ItemBase): ItemBase subclass instance utilizado para troca.

        """
        number = self.number_order

        self.number_order = other.number_order
        other.number_order = number

        self.save()
        other.save()

    def save(self, *args, **kargs):
        is_new = False if self.pk else True

        if self.pk is None:
            self.number_order = ItemBase.next_number_order(self)

        super(ItemBase, self).save(*args, **kargs)

        if is_new:
            self.sync_created_obj()


class SubItem(ItemBase):
    """
    SubItem/Movimento
    """

    manual_amount = models.BooleanField(default=False)
    description = models.TextField(
        verbose_name="Descrição",
        blank=True,
        null=True,
        default="Sem descrição cadastrada.",
    )
    blocked = models.BooleanField(default=False)
    productivy = models.BooleanField(default=False)
    productivity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("corregedoria", "SCORE_TABLE"),
        verbose_name="Produtividade",
    )
    typesubitem = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("raf", "TYPE_SUBITEM"),
        verbose_name="Tipo",
        default=0,
    )
    legal_classification = models.ManyToManyField(
        LegalClassification,
        through="TaxonomyClassification",
        through_fields=("subitem", "classification"),
    )

    class Meta:
        verbose_name = "SubItem/Movimento"
        ordering = ["number_order"]

    @property
    def icons_status(self):
        rst = super(SubItem, self).icons_status
        rst = rst + self.typeicons
        if self.productivity != 1:
            rst.append({"title": "Produtividade", "iconCls": "icon-core icon-core-add"})
        return rst

    @property
    def css_icon_si(self):
        return {
            True: "icon-raf icon-raf-manual-amount",
            False: "icon-raf icon-raf-auto-amount",
        }.get(self.manual_amount)

    @property
    def css_title_si(self):
        return {True: "Contagem Manual", False: "Contagem Automática"}.get(
            self.manual_amount
        )

    @property
    def typeicons(self):
        rst = [{"title": self.css_title_si, "iconCls": self.css_icon_si}]
        if self.blocked:
            rst.append(
                {
                    "title": "Bloqueado para edição",
                    "iconCls": "icon-core icon-core-delete",
                }
            )
        return rst

    def copy_me(self):
        try:
            raise Exception("Not implemented!")
            # old = item = self.__class__.objects.get(pk=self.pk)
            # classification = old.classification.all()
            # exclude_classification = old.exclude_classification.all()
            # item.pk = None
            # item.created_by = get_current_user()
            # item.modified_by = get_current_user()
            # item.created_at = datetime.now()
            # item.modified_at = datetime.now()
            # item.save()
            # item.legalclasses.add(*legalclass)
            # item.exclude_classes.add(*exclude_classes)
            # #
            # for item in quiz.item_set.filter():
            #     for subitem in quiz.subitem_set.filter():
            #         item.subitems.add(subitem)

        except Exception as e:
            raise e

    def delete(self, *args, **kargs):
        """
        Quando deletar a instancia, deve-se refazer a ordenacao
        """
        deleted = self

        super(SubItem, self).delete(*args, **kargs)

        for sb in SubItem.objects.filter(
            quiz=deleted.quiz, number_order__gt=deleted.number_order
        ):
            sb.number_order = sb.number_order - 1
            sb.save()


class SubItemCalculate(AuditTimestampModel):
    """
    SubItem/Movimento
    """

    subitem = models.ForeignKey(
        SubItem,
        related_name="be_calculated",
        verbose_name="subitem_a ser calculado",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    from_the_sum = models.ForeignKey(
        SubItem,
        related_name="for_calculation",
        verbose_name="subitem para calculo",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    affectation = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("raf", "AFFECTATION"),
        verbose_name="Afetar",
        default=1,
    )
    previous_month = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Calculo para Subitem"
        ordering = ["subitem", "from_the_sum"]

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        rst = []
        if self.previous_month:
            rst.append(
                {"title": "Mês anterior", "iconCls": "icon-core icon-core-success"}
            )
        return rst


class Item(ItemBase):
    """
    Item/Assunto
    """

    subitems = models.ManyToManyField(SubItem, related_name="items")

    legal_classification = models.ManyToManyField(
        LegalClassification,
        through="TaxonomyClassification",
        through_fields=("item", "classification"),
    )

    class Meta:
        verbose_name = "Item/Assunto"
        ordering = ["number_order"]

    def delete(self, *args, **kargs):
        """
        Quando deletar a instancia, deve-se refazer a ordenacao
        """
        deleted = self

        super(Item, self).delete(*args, **kargs)

        for it in Item.objects.filter(
            quiz=deleted.quiz, number_order__gt=deleted.number_order
        ):
            it.number_order = it.number_order - 1
            it.save()


class TaxonomyClassification(AuditTimestampModel):
    item = models.ForeignKey(
        Item, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    subitem = models.ForeignKey(
        SubItem, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    classification = models.ForeignKey(
        LegalClassification, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    exclude_classification = models.ForeignKey(
        LegalClassification,
        null=True,
        blank=True,
        related_name="itembase_exclude_classification",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s - %s" % (self.cnmp_code, self.title)

    @property
    def cnmp_code(self):
        return (
            self.classification.cnmp_code
            if self.classification
            else self.exclude_classification.cnmp_code
        )

    @property
    def title(self):
        return (
            self.classification if self.classification else self.exclude_classification
        )

    def save(self, *args, **kwargs):
        if not (self.item or self.subitem):
            raise Exception(
                "Ocorreu um erro ao adicionar a classificação. Item ou subitem não informado."
            )
        elif not (self.classification or self.exclude_classification):
            raise Exception(
                "Ocorreu um erro ao adicionar a classificação. Classificação não informada."
            )

        super(TaxonomyClassification, self).save(*args, **kwargs)


class Activity(AuditTimestampModel):
    """
    Dado referente ao número de atividades realizadas no período referência
    """

    workerlocation = models.ForeignKey(
        WorkerLocation, related_name="activities", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    item = models.ForeignKey(
        Item, related_name="activities", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    subitem = models.ForeignKey(
        SubItem, related_name="activities", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    amount_athenas = models.IntegerField(null=True, blank=True)
    amount_submitted = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Atividade"
        unique_together = ("workerlocation", "item", "subitem")

    def __str__(self):
        return "%s - %s - %s - %s" % (
            self.workerlocation.location,
            self.item.quiz,
            self.item,
            self.subitem,
        )

    @property
    def amount(self):
        amount = (
            self.amount_submitted
            if self.amount_submitted is not None
            else self.amount_athenas
        )

        adjustment = self.last_adjustment
        if adjustment:
            if int(adjustment.situation) in [0, 1]:
                amount = adjustment.amount
        return amount

    @property
    def can_add_adjustment(self):
        last = self.last_adjustment

        if last is None:
            return True
        else:
            return int(last.situation) in [2, 3, 4]

    @property
    def last_adjustment(self):

        query = self.adjustment.filter().order_by("created_at")

        if query.exists():
            return query.last()
        else:
            return None

    @property
    def icons(self):
        rst = {"title": "Sem pedido de ajuste", "iconCls": "icon-core icon-core-blank"}

        return self.last_adjustment.icons if self.last_adjustment else rst

    @classmethod
    def get_or_create(cls, workerlocation=None, item=None, subitem=None):
        try:
            if None in [workerlocation, item, subitem]:
                raise Exception("Parametro informado não pode ser vazio.")

            obj = None
            activity = cls.objects.filter(
                workerlocation=workerlocation, item=item, subitem=subitem
            )
            if activity:
                obj = activity.first()
            else:
                obj = cls()
                obj.workerlocation = workerlocation
                obj.item = item
                obj.subitem = subitem
                obj.save()

        except Exception as e:
            return None
        else:
            return obj

    def validate_permission(self):
        current_user = get_current_user()
        if current_user.username != "athenas":
            if not current_user.has_perm("raf.can_sign_adjustment"):
                employee = employee_from_user(current_user)
                if self.workerlocation.raf.employee.pk != employee.pk:
                    if (
                        TrustRelationship.objects.exclude(activated=False)
                        .filter(
                            employee=self.workerlocation.raf.employee,
                            trust_employee=employee,
                        )
                        .exists()
                        is False
                    ):
                        raise Exception(
                            "Você não tem relação de confiança com o membro"
                        )

    def validate_raf(self):
        current_user = get_current_user()
        if current_user.username != "athenas":
            if not get_current_user().has_perm("raf.can_sign_adjustment"):
                if self.workerlocation.raf.submitted or self.workerlocation.raf.closed:
                    raise Exception(
                        "O RAF encontra-se fechado ou já foi submetido. Por isso não é possível criar uma atividade."
                    )

    def recalculate_activity(self, subitem):
        total = 0
        for fts in subitem.be_calculated.all():
            act = Activity.objects.filter(
                workerlocation=self.workerlocation,
                item=self.item,
                subitem=fts.from_the_sum,
            ).first()
            if act:
                parcela = (act.amount_submitted if act.amount_submitted else 0) * (
                    -1 if fts.affectation != 1 else 1
                )
                total += parcela
        activity = Activity.objects.filter(
            workerlocation=self.workerlocation, item=self.item, subitem=subitem
        ).first()
        if not activity:
            activity = Activity()
            activity.workerlocation = self.workerlocation
            activity.item = self.item
            activity.subitem = subitem
            activity.save()
        activity.amount_submitted = total
        activity.save()

    def recalculate_activity_next_month(self, subitem):
        next_raf = self.workerlocation.raf.next_raf
        if next_raf:
            next_workerlocation = WorkerLocation.objects.filter(
                raf=next_raf, location=self.workerlocation.location
            ).first()
            if not next_workerlocation:
                next_workerlocation = WorkerLocation()
                next_workerlocation.raf = next_raf
                next_workerlocation.location = self.workerlocation.location
                next_workerlocation.save()
            total = 0
            for fts in subitem.be_calculated.all():
                act = Activity.objects.filter(
                    workerlocation=self.workerlocation,
                    item=self.item,
                    subitem=fts.from_the_sum,
                ).first()
                if act:
                    parcela = (act.amount_submitted if act.amount_submitted else 0) * (
                        -1 if fts.affectation != 1 else 1
                    )
                    total += parcela
            next_act = Activity.objects.filter(
                workerlocation=next_workerlocation, item=self.item, subitem=subitem
            ).first()
            if not next_act:
                next_act = Activity()
                next_act.workerlocation = next_workerlocation
                next_act.item = self.item
                next_act.subitem = subitem
                next_act.save()
            next_act.amount_submitted = total
            next_act.save()

    def save(self, recalculate=True, *args, **kargs):
        self.validate_permission()
        self.validate_raf()
        super(Activity, self).save(*args, **kargs)
        if recalculate is True:
            for sc in SubItemCalculate.objects.filter(from_the_sum=self.subitem):
                if sc.previous_month is False:
                    self.recalculate_activity(sc.subitem)
            for sc in SubItemCalculate.objects.filter(from_the_sum=self.subitem):
                if sc.previous_month is True:
                    value = (self.amount_submitted if self.amount_submitted else 0) - (
                        self.old_fields.get("amount_submitted")
                        if self.old_fields.get("amount_submitted")
                        else 0
                    )
                    self.recalculate_activity_next_month(sc.subitem)


class ActivityAdjustment(AuditTimestampModel):
    """Classe de ajuste de atividades.

    Utilizado para justificar os novos valores a fim de corrigir o valor aferido na atividade (Activity).

    Attributes:

        amount (Integer): Quantidade de atividades para ser retificada
        situation (Choice): Status da solicitação de ajuste
        conversation (Conversation) : Contem a troca de informacoes sobre o pedido de ajuste

    situation values:
        0 - Não avaliado
        1 - Em análise
        2 - Deferido
        3 - Indeferido
        4 - Cancelado
        5 - Não envidado
    """

    activity = models.ForeignKey(
        "Activity", related_name="adjustment", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    amount = models.IntegerField(null=True, blank=True)
    situation = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("raf", "ADJUSTMENT_SITUATION"),
        verbose_name="Situação",
        default=5,
    )
    initial_message = models.TextField(null=True, blank=True)
    conversation = models.OneToOneField(
        "Conversation", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Ajuste de Atividade"
        ordering = ["created_at"]
        permissions = (
            ("can_sign_adjustment", "Pode aceitar/rejeitar pedido de ajuste"),
        )

    def __str__(self):
        return "%s - %s - %s - %s" % (
            self.activity.workerlocation.location.sigla,
            self.activity.item.quiz.typequiz.title,
            self.activity.item,
            self.activity.subitem,
        )

    @property
    def subject(self):
        return (
            "[RAF] Resposta à solicitação de alteração do RAF %s/%s do questionário %s da %s "
            % (
                self.activity.workerlocation.raf.month,
                self.activity.workerlocation.raf.year,
                self.activity.item.quiz,
                self.activity.workerlocation.location,
            )
        )

    @property
    def status(self):
        return {
            0: "Não avaliado",
            1: "Aguardando informações",
            2: "Deferido",
            3: "Indeferido",
            4: "Cancelado",
            5: "Não enviado",
            6: "Avaliado",
        }.get(int(self.situation), "Status não definido")

    @property
    def css_icon_cls(self):
        return {
            0: "icon-core icon-core-waiting",
            1: "icon-fopag icon-blueprint-pencil",
            2: "icon-core icon-core-success",
            3: "icon-core icon-core-error",
            4: "icon-core icon-core-delete",
            5: "icon-fopag icon-forward-progression",
            6: "icon-core icon-core-update-manage",
        }.get(int(self.situation), "Status não definido")

    @property
    def icons(self):
        return {"title": self.status, "iconCls": self.css_icon_cls}

    @property
    def rendered(self):
        tpl = loader.get_template("raf/content.html")

        return tpl.render(
            {
                "doc": self,
                "raf": self.activity.workerlocation.raf,
                "quiz": self.activity.item.quiz,
                "prosecutor": self.activity.workerlocation.raf.employee.pessoa_fisica.nome,
            }
        )

    @property
    def created_at_formatted(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def action(self, situation="", answer=""):
        try:
            if not get_current_user().has_perm("raf.can_sign_adjustment") and int(
                situation
            ) in [2, 3]:
                raise Exception(
                    "Você não tem permissão para deferir/indeferir a solicitação."
                )
            if not int(situation) in [2, 3, 4, 6]:
                raise Exception("Situação informada é inválida.")
            if int(situation) == 4:
                if self.situation not in [0, 5]:
                    raise Exception(
                        'Cancelamento só possível para solicitações nos estados "NÃO ENVIADO" e "NÃO AVALIADO".'
                    )
                if self.dataadjustment.exclude(situation__in=[0]).exists():
                    raise Exception(
                        "Solicitação em atendimento, cancelamento não permitido."
                    )
            self.situation = int(situation)
            if self.situation == 2:
                answer = "Solicitação foi deferida."
            self.save()
            for da in self.dataadjustment.all():
                # da.action(situation=self.situation, answer=answer)
                da.situation = self.situation
                da.save()
        except Exception as e:
            raise e

    def undoAction(self, answer=""):
        try:
            if not get_current_user().has_perm("raf.can_sign_adjustment"):
                raise Exception(
                    "Você não tem permissão para desfazer a decisão da solicitação."
                )
            if self.situation not in [2, 3, 4, 6]:
                raise Exception("Solicitação de ajuste não está finalizada.")
            self.situation = 0
            self.save()
            cfg = Configuration.get_or_create("raf")
            origin = Location.objects.get(pk=int(cfg.get("location", 0)))
            self.__undo_amount_activity()
            for da in self.dataadjustment.all():
                da.situation = 0
                da.save()
                da.conversation.finalized = False
                da.conversation.save()
                answer = "Desfeita decisão da solicitação. <p>%s</p>" % (answer)
                da.conversation.create_content(
                    origin=origin, message=answer, situation=0
                )
                autoreference = AutoReference.objects.filter(
                    process_number=da.process_number,
                    activity=da.activityadjustment.activity,
                    source_add=da.source,
                    date__year=da.date.year,
                    date__month=da.date.month,
                    date__day=da.date.day,
                ).first()
                if da.operation == 1:
                    if autoreference:
                        autoreference.delete()
                if da.operation == 2:
                    if autoreference:
                        autoreference.removed = False
                        autoreference.save()
        except Exception as e:
            raise e

    def validate_permission(self):
        employee = employee_from_user(get_current_user())
        if not get_current_user().has_perm("raf.can_sign_adjustment"):
            if self.activity.workerlocation.raf.employee.pk != employee.pk:
                if (
                    TrustRelationship.objects.exclude(activated=False)
                    .filter(
                        employee=self.activity.workerlocation.raf.employee,
                        trust_employee=employee,
                    )
                    .exists()
                    is False
                ):
                    raise Exception("Você não tem relação de confiança com o membro")

    def validate_raf(self):
        if not get_current_user().has_perm("raf.can_sign_adjustment"):
            if (
                self.activity.workerlocation.raf.submitted
                or self.activity.workerlocation.raf.closed
            ):
                raise Exception(
                    "O RAF encontra-se fechado ou já foi submetido. Por isso não é possível realizar essa ação."
                )

    def __undo_amount_activity(self):
        value = self.activity.amount_athenas
        for a in self.activity.adjustment.order_by("created_at"):
            if a.situation == 2:
                value = a.amount
        self.activity.amount_submitted = value
        self.activity.save()

    def __update_amount_activity(self, recalculate=False):
        self.activity.amount_submitted = self.amount
        self.activity.save(recalculate=recalculate)

    def validate_configurations(self):
        try:
            cfg = Configuration.get_or_create("raf")
            TipoDocumento.objects.get(pk=int(cfg.get("documentType", 0)))
            Location.objects.get(pk=int(cfg.get("location", 0)))
        except self.model.DoesNotExist:
            raise Exception("Parâmentros de configuração do RAF não foram informados.")

    @property
    def can_add_adjustment(self):
        return self.activity.can_add_adjustment

    def save(self, *args, **kargs):
        if (
            not self.pk
            and ActivityAdjustment.objects.filter(
                activity=self.activity, situation__in=[0, 1, 5]
            ).exists()
            and not self.can_add_adjustment
        ):
            raise Exception(
                "Existe uma solicitação de ajuste para essa atividade em análise."
            )
        self.validate_permission()
        self.validate_raf()
        self.validate_configurations()
        super(ActivityAdjustment, self).save(*args, **kargs)
        if self.situation in [6]:
            self.__update_amount_activity(recalculate=True)


class DataAdjustment(AuditTimestampModel):
    """
    Listagem de processos/procedimentos a serem adicionados em atividade

    operation values:
        1 - Adicionar
        2 - Remover
    """

    activityadjustment = models.ForeignKey(
        ActivityAdjustment, related_name="dataadjustment", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    operation = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("raf", "ADJUSTMENT_OPERATION"),
        verbose_name="Ação da Solicitação de Ajuste",
        default=1,
    )
    process_number = models.TextField(verbose_name="Numero de identificação")
    source = situation = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("raf", "ACTIVITY_SOURCE"),
        verbose_name="Origem",
        default=1,
    )
    date = models.DateField(verbose_name="Data da atividade", null=True)
    legalclass = models.ForeignKey(
        LegalClass,
        related_name="dataadjustment_legalclass",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    legalmatter = models.ForeignKey(
        LegalClassification,
        related_name="dataadjustment_legalmatter",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    movement = models.ForeignKey(
        LegalMovement, related_name="dataadjustment_movement", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    initial_message = models.TextField(blank=True)
    situation = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("raf", "DATAADJUSTMENT_SITUATION"),
        verbose_name="Situação",
    )
    conversation = models.OneToOneField(
        "Conversation", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = (
            "Listagem de processos/procedimentos a serem adicionados em atividade"
        )
        ordering = ["operation", "date"]

    @property
    def employee(self):
        return employee_from_user(self.created_by).pessoa_fisica.nome

    @property
    def status(self):
        return {
            0: "Não avaliado",
            1: "Aguardando informações",
            2: "Deferido",
            3: "Indeferido",
            4: "Cancelado",
            5: "Não enviado",
        }.get(int(self.situation), "Status não definido")

    @property
    def css_icon_cls(self):
        return {
            0: "icon-core icon-core-waiting",
            1: "icon-fopag icon-blueprint-pencil",
            2: "icon-core icon-core-success",
            3: "icon-core icon-core-error",
            4: "icon-core icon-core-delete",
            5: "icon-fopag icon-forward-progression",
        }.get(int(self.situation))

    @property
    def icons(self):
        return {"title": self.status, "iconCls": self.css_icon_cls}

    @property
    def process_number_formatted(self):
        ret = self.process_number
        if self.source == 1:
            f = "{:>20}".format(self.process_number.strip()).replace(" ", "0")
            ret = "{:07d}-{}.{}.{}.{}".format(
                int(f[0:7]), f[7:9], f[9:13], f[13:16], f[16:20]
            )
        if self.source == 2:
            f = "{:>11}".format(self.process_number.strip()).replace(" ", "0")
            ret = "{}.{}".format(f[0:4], f[4:12])
        return ret

    @property
    def rendered(self):
        tpl = loader.get_template("raf/dataadjustment_content.html")

        return tpl.render(
            {
                "doc": self,
                "raf": self.activityadjustment.activity.workerlocation.raf,
                "quiz": self.activityadjustment.activity.item.quiz,
                "prosecutor": self.activityadjustment.activity.workerlocation.raf.employee.pessoa_fisica.nome,
            }
        )

    def get_countdata(self):
        adj = self.activityadjustment
        count = 0
        for d in adj.dataadjustment.all():
            if d.situation not in [3, 4]:
                count = count + (1 if d.operation == 1 else -1)
        return count

    def action(self, situation=None, answer=None):
        try:
            if not get_current_user().has_perm("raf.can_sign_adjustment") and int(
                situation
            ) in [2, 3]:
                raise Exception(
                    "Você não tem permissão para deferir/indeferir a solicitação."
                )
            if not int(situation) in [2, 3, 4]:
                raise Exception("Situação informada é inválida.")
            if not answer:
                raise Exception("Informe a justificativa.")
            if int(situation, 0) == 3:
                answer = "Item indeferido.<br />" + answer
            cfg = Configuration.get_or_create("raf")
            origin = Location.objects.get(pk=int(cfg.get("location", 0)))
            self.situation = int(situation, 0)
            self.save()
        except Exception as e:
            raise e
        else:
            self.conversation.create_content(
                origin=origin, message=answer, situation=situation, finish=True
            )

    def update_activityadjustment(self):
        adjustment = self.activityadjustment
        if adjustment.situation in [0, 1, 2, 4, 5]:
            adjustment.amount = (
                adjustment.activity.amount_submitted
                if adjustment.activity.amount_submitted
                else 0
            ) + self.get_countdata()
            adjustment.save()

    def clear_process_number(self):
        erase = ".-,/"
        ret = self.process_number
        for i in range(0, len(erase)):
            ret = ret.replace(erase[i], "")
        return ret

    def save(self, *args, **kargs):
        if not self.initial_message:
            raise Exception("Informe a justificativa.")
        if self.pk is None:
            self.situation = 5
        if self.conversation is None:
            self.conversation = Conversation.get_or_create(dataadjustment=self)
        self.process_number = self.clear_process_number()
        super(DataAdjustment, self).save(*args, **kargs)
        self.update_activityadjustment()
        if self.situation == 2:
            if self.operation == 1:
                autoreference = AutoReference()
                autoreference.activity = self.activityadjustment.activity
                autoreference.is_adjustment = True
                autoreference.removed = False
                autoreference.source = self.get_source_display()
                autoreference.source_add = self.source
                if self.source == 1:
                    autoreference.process_number = int(
                        self.process_number.replace(".", "")
                        .replace("-", "")
                        .replace("/", "")
                    )
                else:
                    autoreference.process_number = self.process_number
                autoreference.date = self.date
                autoreference.content_object = self
                autoreference.save()
            if self.operation == 2:
                autoreference = AutoReference.objects.filter(
                    process_number=self.process_number,
                    activity=self.activityadjustment.activity,
                    source_add=self.source,
                    date__year=self.date.year,
                    date__month=self.date.month,
                    date__day=self.date.day,
                ).first()
                if autoreference:
                    autoreference.removed = True
                    autoreference.save()
        # if self.situation == 4:
        #     answer = u'Solicitação cancelada pelo usuário'
        #     cfg = Configuration.get_or_create('raf')
        #     origin = Location.objects.get(pk=int(cfg.get('location', 0)))
        #     self.conversation.create_content(origin=origin, message=answer, situation=self.situation, finish=True)

    def delete(self, *args, **kargs):
        super(DataAdjustment, self).delete(*args, **kargs)
        self.update_activityadjustment()
        log.info("Remover o AutoReference...")


class Conversation(AuditTimestampModel):
    finalized = models.BooleanField(default=False)
    locations = models.ManyToManyField(Location)
    last_content = models.OneToOneField(
        "ConversationContent",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    @property
    def created_at_formatted(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    @classmethod
    def get_or_create(cls, adjustment=None, dataadjustment=None):
        if adjustment is not None:
            if adjustment.conversation:
                return adjustment.conversation
            else:
                cfg = Configuration.get_or_create("raf")
                conversation = Conversation(finalized=False)
                conversation.save()
                conversation.locations.add(
                    Location.objects.get(pk=int(cfg.get("location", 0)))
                )
                conversation.locations.add(adjustment.activity.workerlocation.location)
                return conversation
        if dataadjustment is not None:
            if dataadjustment.conversation:
                return dataadjustment.conversation
            else:
                cfg = Configuration.get_or_create("raf")
                conversation = Conversation(finalized=False)
                conversation.save()
                conversation.locations.add(
                    Location.objects.get(pk=int(cfg.get("location", 0)))
                )
                conversation.locations.add(
                    dataadjustment.activityadjustment.activity.workerlocation.location
                )
                return conversation

    def updateGerador(self, situation=None):
        adjustment = ActivityAdjustment.objects.filter(conversation=self).first()
        if adjustment:
            adjustment.situation = situation
            adjustment.save()
        dataadjustment = DataAdjustment.objects.filter(conversation=self).first()
        if dataadjustment:
            dataadjustment.situation = situation
            dataadjustment.save()
            adj = ActivityAdjustment.objects.filter(
                pk=dataadjustment.activityadjustment.pk
            ).first()
            if (
                DataAdjustment.objects.filter(activityadjustment=adj)
                .exclude(situation__in=[2, 3])
                .exists()
                is False
            ):
                adj.situation = 6
            else:
                if (
                    DataAdjustment.objects.filter(activityadjustment=adj)
                    .exclude(situation__in=[4])
                    .exists()
                    is False
                ):
                    adj.situation = 4
            adj.save()
            # adj = ActivityAdjustment.objects.filter(pk=dataadjustment.activityadjustment.pk).first()
            # adj.situation = situation if DataAdjustment.objects.filter(activityadjustment=adj).exclude(situation__in=[2, 3]).exists() else 6
            # adj.save()

    def create_content(self, message="", origin=None, situation=None, finish=False):
        if self.finalized:
            raise Exception("A Comunicação encontra-se encerrada.")
        else:
            self.finalized = finish
            content = ConversationContent(
                conversation=self,
                message=message,
                origin=origin,
            )
            content.save()
            self.last_content = content
            self.save()
            self.updateGerador(situation=situation)


class ConversationContent(AuditTimestampModel):
    conversation = models.ForeignKey(
        Conversation, related_name="contents", on_delete=models.CASCADE
    )
    origin = models.ForeignKey(
        Location, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        Employee, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    message = models.TextField()
    step = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["created_at"]

    @property
    def created_at_formatted(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def save(self, *args, **kwargs):
        self.employee = employee_from_user(get_current_user())
        self.step = (
            int(
                self.__class__.objects.filter(conversation=self.conversation)
                .aggregate(Max("step"))
                .get("step__max")
                or 0
            )
            + 1
        )
        super(ConversationContent, self).save(*args, **kwargs)


class AutoReference(AuditTimestampModel):
    """
    Auto referência
    """

    activity = models.ForeignKey(
        Activity, related_name="autoreference", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    source = models.TextField(verbose_name="Origem da informação")
    source_add = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("raf", "ACTIVITY_SOURCE"),
        default=1,
    )
    is_adjustment = models.BooleanField(default=False, null=True, blank=True)
    removed = models.BooleanField(default=False, null=True, blank=True)
    process_number = models.TextField(verbose_name="Numero de identificação")
    date = models.DateTimeField(verbose_name="Data da atividade", null=True)
    obj = models.TextField(verbose_name="JSON de referencia")

    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Auto Referência"

    def __str__(self):
        return str(self.activity)

    @property
    def process_number_formatted(self):
        ret = self.process_number
        if self.source_add == 1:
            f = "{:>20}".format(self.process_number.strip()).replace(" ", "0")
            ret = "{:07d}-{}.{}.{}.{}".format(
                int(f[0:7]), f[7:9], f[9:13], f[13:16], f[16:20]
            )
        # if self.source_add == 2:
        #     f = '{:>11}'.format(self.process_number.strip()).replace(' ', '0')
        #     ret = '{}.{}'.format(f[0:4], f[4:12]):
        return ret


class TrustRelationship(AuditTimestampModel):
    """
    Docstring da classe
    """

    employee = models.ForeignKey(
        Employee, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    trust_employee = models.ForeignKey(
        Employee, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    activated = models.BooleanField(default=True)

    class Meta:
        ordering = ["employee"]
        verbose_name = "Relação de confiança"
        unique_together = ("employee", "trust_employee")

    def __str__(self):  # __str__(self)
        return " %s" % self.employee

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        rst = []

        if self.activated:
            rst.append({"title": "Ativo", "iconCls": "icon-raf icon-raf-activated"})
        else:
            rst.append(
                {"title": "Desativado", "iconCls": "icon-raf icon-raf-deactivated"}
            )

        return rst

    @classmethod
    def queryset_relationship_from_employee(
        cls, activated=True, employee=None, pklist=False
    ):
        from django.db.models import Q

        if employee is None:
            employee = employee_from_user(get_current_user())

        query_trust = Q(
            Q(Q(activated=activated) & Q(trust_employee=employee))
            | Q(employee=employee)
        )

        query = cls.objects.none()

        if pklist:
            query = cls.objects.filter(query_trust).values_list("employee", flat=True)
        else:
            query = cls.objects.filter(query_trust)

        return query

    @classmethod
    def queryset_raf_trust_from_current_user(cls, raf):
        try:
            queryset = cls.queryset_relationship_from_employee()
            return queryset.filter(employee=raf.employee)
        except Exception:
            return cls.objects.none()

    def save(self, *args, **kwargs):
        super(TrustRelationship, self).save(*args, **kwargs)


class DataEProc(models.Model):
    """
    Retorno da consulta RAF_EPROC
    """

    mes_referencia = models.CharField(max_length=2, null=True)
    ano_referencia = models.CharField(max_length=4, null=True)
    membro = models.CharField(max_length=100, null=True)
    promotoria = models.CharField(max_length=150)
    promotoria_slugfy = models.CharField(max_length=150)
    processo = models.CharField(max_length=100, null=True)
    codclasse = models.CharField(max_length=100, null=True)
    codassuntoprincipal = models.CharField(max_length=100, null=True)
    codmovimento = models.CharField(max_length=100, null=True)
    datamovimento = models.CharField(max_length=100, null=True)
    semintimacao = models.CharField(max_length=100, null=True)
    instancia = models.CharField(max_length=100, null=True)
    # analise = models.CharField(max_length=100, null=True)
    analise = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("raf", "ANALISE"),
        verbose_name="Análise",
        default=0,
    )
    processo_formatado = models.CharField(max_length=100, null=True)
    # informacoes legadas
    dataintimacao = models.CharField(max_length=100, null=True)
    intimacao = models.CharField(max_length=250, null=True)
    dataabriuprazo = models.CharField(max_length=100, null=True)
    manifestacaoabertura = models.CharField(max_length=250, null=True)
    datafechouprazo = models.CharField(max_length=100, null=True)
    manifestacaofechamento = models.CharField(max_length=250, null=True)
    codmanifestacaofechamento = models.CharField(max_length=100, null=True)
    datamanifestacaodecurso = models.CharField(max_length=100, null=True)
    manifestacaodecurso = models.CharField(max_length=250, null=True)
    codmanifestacaodecurso = models.CharField(max_length=100, null=True)
    classe = models.CharField(max_length=350, null=True)
    assuntoprincipal = models.CharField(max_length=350, null=True)
    assuntosecundario = models.CharField(max_length=350, null=True)
    codassuntosecundario = models.CharField(max_length=100, null=True)
    orgao = models.CharField(max_length=150, null=True)

    class Meta:
        ordering = ["membro", "promotoria", "datamovimento"]
        verbose_name = "DataEproc"

    def __str__(self):
        return "%s - %s" % (str(self.processo), str(self.promotoria))

    @property
    def processo_formatted(self):
        return self.process_formatted()

    def process_formatted(self):
        f = "{:>20}".format(self.processo).replace(" ", "0")
        ff = "{:07d}-{}.{}.{}.{}".format(
            int(f[0:7]), f[7:9], f[9:13], f[13:16], f[16:20]
        )
        return ff

    def save(self, *args, **kargs):
        if self.pk is None:
            self.processo_formatado = self.process_formatted()
        super(DataEProc, self).save(*args, **kargs)


class DataEExt(models.Model):
    """
    Relacao de Movimentos importados do e-Ext
    """

    month = models.CharField(max_length=2, null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)
    employee = models.ForeignKey(
        Employee, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    employee_registration = models.IntegerField(default=0)
    location = models.ForeignKey(
        Location, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    proccess_number = models.CharField(max_length=100, null=True, blank=True)
    legalclass = models.ForeignKey(
        LegalClass, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    legalmatter = models.ForeignKey(
        LegalMatter, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    legalmovement = models.ForeignKey(
        LegalClassification,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    date_movement = models.DateTimeField(
        verbose_name="Data da atividade", null=True, blank=True
    )
    analisys = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("raf", "ANALISE"),
        verbose_name="Análise",
        default=0,
    )
    codmovement = models.IntegerField(blank=True, null=True)
    codmatter = models.IntegerField(blank=True, null=True)
    codclass = models.IntegerField(blank=True, null=True)
    signed_by_user = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["employee", "location", "date_movement"]
        verbose_name = "DataEExt"

    def __str__(self):
        return "%s - %s" % (str(self.proccess_number), str(self.location))

    @classmethod
    def create_in_bulk(cls, extract=None):
        extract = extract or []

        for params in extract:
            obj = None
            obj = cls(**params)
            obj.save()

    @classmethod
    def extract_extrajudicial_movements(cls, employee, initial_date, final_date):
        from judicial.models import PartLawsuit, OutCourtLawsuitLog, LawsuitMatter

        if employee.user is None:
            return []

        def get_matter(part):
            if part.main_matter:
                return part.main_matter
            else:
                lawsuitmatter = (
                    LawsuitMatter.objects.filter(lawsuit=part.lawsuit)
                    .filter(principal=True)
                    .first()
                )
                return getattr(lawsuitmatter, "matter", None)

        def get_classification(obj, kind):
            if kind == "legalclass" and obj.main_tag:
                c = getattr(obj.main_tag.classification, "legalclass", None)
                if c:
                    return c, c.cnmp_code
                else:
                    return None, None
            elif kind == "legalmatter":
                m = get_matter(obj)
                if m:
                    return m, m.cnmp_code
                else:
                    return None, None
            elif kind == "legalmovement":
                if obj.part.legal_classification:
                    return (
                        obj.part.legal_classification,
                        obj.part.legal_classification.cnmp_code,
                    )
                else:
                    return None, None
            else:
                return None, None

        format_date = lambda x: datetime.strptime(x, "%Y-%m-%d").date()
        if type(initial_date) == str:
            initial_date = format_date(initial_date)
        if type(final_date) == str:
            final_date = format_date(final_date)

        employee_locations = (
            employee.get_work_assignment()
            .filter(
                Q(
                    Q(
                        ~Q(data_vigencia_fim__lte=initial_date)
                        & ~Q(data_vigencia_inicio__gte=final_date)
                    )
                )
            )
            .values_list("lotacao", "data_vigencia_inicio", "data_vigencia_fim")
        )

        if employee_locations:

            assistant_filter_query = Q()

            for el in employee_locations:
                start = initial_date if el[1] <= initial_date else el[1]
                end = final_date if el[2] is None or el[2] >= final_date else el[2]

                start = datetime.combine(start, time.min)
                end = datetime.combine(end, time.max)

                assistant_filter_query.add(
                    (Q(location__id=el[0]) & Q(part__signed_at__range=(start, end))),
                    Q.OR,
                )

            assistant_signed = OutCourtLawsuitLog.objects.filter(
                assistant_filter_query
            ).order_by("location", "part__signed_at")

        else:
            assistant_signed = OutCourtLawsuitLog.objects.none()

        member_signed = OutCourtLawsuitLog.objects.filter(
            Q(
                Q(part__signed_by=employee.user)
                & Q(
                    Q(part__signed_at__gte=initial_date)
                    & Q(part__signed_at__lte=final_date)
                )
            )
        ).order_by("lawsuit__cache_number", "part__signed_at")

        lawsuit_log = member_signed.union(assistant_signed)

        rst = []
        for obj in lawsuit_log:
            legalclass, codclass = get_classification(obj, "legalclass")
            legalmatter, codmatter = get_classification(obj, "legalmatter")
            legalmovement, codmovement = get_classification(obj, "legalmovement")

            rst.append(
                {
                    "month": obj.part.signed_at.month,
                    "year": obj.part.signed_at.year,
                    "employee": employee,
                    "employee_registration": employee.matricula,
                    "location": getattr(obj.location, "lotacao", None),
                    "proccess_number": obj.lawsuit.cache_number,
                    "legalclass": legalclass,
                    "codclass": codclass,
                    "legalmatter": legalmatter,
                    "codmatter": codmatter,
                    "legalmovement": legalmovement,
                    "codmovement": codmovement,
                    "date_movement": obj.part.signed_at,
                    "analisys": 0,
                    "signed_by_user": obj.part.signed_by,
                }
            )

        return rst

    def save(self, *args, **kargs):
        super(DataEExt, self).save(*args, **kargs)


class NonProceduralActivities(AuditTimestampModel):
    """Atividades não procedimentais para o app do raf"""

    member = models.ForeignKey(
        Employee,
        verbose_name="Membro",
        related_name="nonproceduralactivities",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    legal_procedure = models.ForeignKey(
        LegalProcedure,
        verbose_name="Procedimento Legal",
        related_name="nonproceduralactivities",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    date = models.DateField(verbose_name="Data")
    description = models.TextField(verbose_name="Descrição", blank=True, null=True)
    title = models.CharField(verbose_name="Título", max_length=128)

    class Meta:
        verbose_name = "Atividades não procedimentais"
        ordering = ["-date"]

    def __str__(self):
        return self.title


class SearchByNumber(models.Model):
    """Pesquisa por numero sobre VW SearchByNumber"""

    contenttype = models.CharField(max_length=100)
    source = models.SmallIntegerField()
    process_number = models.CharField(max_length=100)
    process_number_formatted = models.CharField(max_length=100)
    matricula = models.IntegerField()
    membro = models.CharField(max_length=200)
    month = models.IntegerField()
    year = models.IntegerField()
    date = models.DateField()
    analisys = models.PositiveSmallIntegerField(
        null=True,
        choices=Choice.get_choices_for("raf", "ANALISE"),
        verbose_name="Análise",
    )
    situation = models.IntegerField(null=True)
    operation = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("raf", "ADJUSTMENT_OPERATION"),
        verbose_name="Ação da Solicitação de Ajuste",
        default=1,
    )

    class Meta:
        db_table = "raf_searchbynumber_vw"
        ordering = ["process_number_formatted", "date"]
        managed = False


class SpecialOrgan(AuditTimestampModel):
    location = models.ForeignKey(Location, related_name="+", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Orgao Especial"
        ordering = ["location"]


class Solicitation(AuditTimestampModel):
    """
    Modelo de registros de solicitacoes relacionadas ao RAF.
    """

    KIND_REOPENING = 0
    STATUS_UNVALUED = 0
    STATUS_ACCEPTED = 1
    STATUS_DENIED = 2

    KIND_CHOICES = ((KIND_REOPENING, "Reabertura de prazo"),)

    STATUS_CHOICES = (
        (STATUS_UNVALUED, "Não avaliado"),
        (STATUS_ACCEPTED, "Deferido"),
        (STATUS_DENIED, "Indeferido"),
    )

    raf = models.ForeignKey(
        FunctionalActivityReport, related_name="solicitations", on_delete=models.CASCADE
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, verbose_name="situação", default=0
    )
    kind = models.PositiveSmallIntegerField(choices=KIND_CHOICES, verbose_name="tipo")

    def __str__(self):
        return (
            f"RAF {self.raf.month}/{self.raf.year} - {self.raf.employee.pessoa_fisica}"
        )

    def _reopening_action(self):
        try:
            if not (
                self.raf.open_date
                and (datetime.now().date() >= self.raf.open_date.date())
            ):
                raise Exception("RAF selecionado não pode ser reaberto no momento.")

            if self.raf.closed is False:
                raise Exception("RAF selecionado já encontra-se aberto")

            if self.__class__.objects.filter(
                raf=self.raf, status=self.__class__.STATUS_UNVALUED
            ):
                raise Exception(
                    "Já existe uma solicitação de reabertura para esse RAF."
                )

            if TrustRelationship.queryset_raf_trust_from_current_user(self.raf):
                self.kind = self.__class__.KIND_REOPENING
                self.save()
            else:
                raise Exception(
                    "Você não tem permissão/relação de confiança para solicitar reabertura."
                )

        except Exception as e:
            raise e

    @classmethod
    def register(cls, raf, kind):
        if kind == cls.KIND_REOPENING:
            obj = cls(raf=raf)
            obj._reopening_action()

    @property
    def has_permission_management(self):
        try:
            user = get_current_user()
            if user is None:
                raise Exception("Usuário nao definido")
            return user.has_perm("raf.can_management_raf")
        except Exception as e:
            raise e

    def accept_kind_reopening(self):
        if self.status == Solicitation.STATUS_UNVALUED:
            self.raf.deadline_extend_by_days(days=11)
            self.status = Solicitation.STATUS_ACCEPTED
            self.save()

    def accept(self):
        if self.has_permission_management:
            if self.kind == Solicitation.KIND_REOPENING:
                self.accept_kind_reopening()
        else:
            raise Exception("Usuário não tem permissão para gerenciar solicitações")

    def save(self, *args, **kwargs):
        super(Solicitation, self).save(*args, **kwargs)
