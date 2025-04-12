# -*- coding: utf-8 -*-
import os
import random
import hashlib
from base64 import b64encode
from datetime import timedelta, date, datetime

from django.db import models
from django.db import transaction
from django.template import loader

from standard.models import Choice, Configuration
from contrib.middleware import get_current_user
from contrib.utils import getLogger, person_from_user, employee_from_user
from ged.models import Arquivo
from edocs.protocolo.models import LegalSign
from judicial.models import (
    LegalMatter,
    PartLawsuit,
    type_part_lawsuit,
    templated,
    Attached as BaseAttached,
    ExecutionOrgan,
    JudicialLegalSign,
    RemittanceInternal,
    MEANING_TYPE_ACTION,
    MEANING_TYPE_DOCUMENT,
)
from rh.models import (
    Publicacao as Publication,
    Cargo as JobPosition,
    Servidor as Employee,
)

log = getLogger(__name__)


class with_number_for_year(object):

    def next_number(self, year=None):
        year = year if year else date.today().year
        query = (
            self.__class__.objects.filter(year=year)
            .order_by("id")
            .aggregate(max_number=models.Max("number"))
        )

        return int(query.get("max_number") or 0) + 1


@type_part_lawsuit()
class DistributionRapporteur(with_number_for_year, PartLawsuit):
    part_origin = models.ForeignKey(
        PartLawsuit,
        related_name="has_origin_for_distribution_rapporteur",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    number = models.SmallIntegerField(blank=True)
    year = models.SmallIntegerField(blank=True)
    cached_number = models.CharField(
        max_length=10, db_index=True, unique=True, blank=True
    )

    codename = "Distribuição - Conselho"

    class Meta:
        permissions = (
            (
                "prepare_distribution_rapporteur",
                "Pode preparar distribuição de relatoria",
            ),
            ("can_sign_distribution_rapporteur", "Pode assinar distribuição"),
        )

    @property
    def meaning_type(self):
        return MEANING_TYPE_ACTION

    @property
    def sign_part_authorized(self):
        """
        1. Verificar se o usuário tem permissão para realizar a ação.
        """
        if not get_current_user().has_perm("council.can_sign_distribution_rapporteur"):
            raise Exception("Você não tem permissão para assinar este documento.")

        if self.convocation_notices.filter(convocation_state__in=(1, 2)).exists():
            raise Exception("Ainda temos editais de intimação pendentes de publicação.")

        for convocation in self.convocation_notices.exclude(
            convocation_state__in=(1, 2, 4)
        ):
            if not convocation.deadline_is_ended:
                raise Exception(
                    "Ainda existem editais de intimação com prazo correndo."
                )

        if not self.votes.exists():
            raise Exception(
                "Ainda não foi feita a preparação da concorrêcia para distribuição."
            )

        if not self.part_origin:
            self.part_origin = self.lawsuit.last_part_lawsuit

        if self.part_origin.manifestations.filter(
            deadline=None, signed_by=None
        ).exists():
            raise Exception(
                'Ainda existem diligencias em "%s" que ainda não foram entregues.'
                % self.part_origin
            )
        elif self.part_origin.manifestations.filter(
            deadline__gt=datetime.now()
        ).exists():
            raise Exception("Ainda existem diligencias com prazo correndo.")

        if not self.votes.exclude(vote=None):
            log.info("Ainda não foi feito o sorteio da relatoria.")
            self.distribute()

        return True

    def _all_extra_pages_complete(self):
        return (
            super(DistributionRapporteur, self)._all_extra_pages_complete()
            + self.extra_pages_of_convocation_notice
        )

    @property
    def extra_pages_of_convocation_notice(self):
        pages = []

        if self.can_read:
            for convocation in self.convocation_notices.filter():
                pages.append(
                    {"at": convocation.signed_at, "page": convocation.rendered}
                )

        return pages

    def sign_part(self):
        with transaction.atomic():
            super(DistributionRapporteur, self).sign_part()

    @property
    def rapporteur(self):
        return (
            self.rapporteur_councillor.employee if self.rapporteur_councillor else None
        )

    @property
    def rapporteur_councillor(self):
        if not getattr(self, "__cache_rapporteur_councillor", None):
            query = self.votes.exclude(vote__rapporteur=None)

            if query.exists():
                self.__cache_rapporteur_councillor = query.get()
            else:
                self.__cache_rapporteur_councillor = None

        return self.__cache_rapporteur_councillor

    def create_repporteur(self, councillor):
        log.info("Criando relatoria para %s", councillor.employee)
        Rapporteur(councillor=councillor, from_distribution=self).save()
        drs, created = DistributionRepporteurScore.objects.get_or_create(
            possession=councillor.possession
        )
        drs.increase()

    def create_vote(self, councillor, invalide=False):
        log.info("Criando cedula de voto para %s", councillor.employee)
        Vote(councillor=councillor, invalide=invalide, from_distribution=self).save()

    def distribute(self):
        sentence = (
            models.Q(incident_type=None)
            | models.Q(incident_type__lt=200)
            | models.Q(models.Q(incident_type__gte=200) & ~models.Q(substitute=None))
        )
        total = self.votes.filter().count()
        capable = self.votes.filter(sentence).count()

        if not (float(capable) / float(total) > 0.5):
            raise Exception(
                "É necessário convocar outros conselheiros para substituir os que tem incidentes negativos, não havera quorum."
            )

        if self.votes.filter(
            models.Q(incident_type__gt=100) & models.Q(incident_type__lt=200)
        ).exists():
            self._distribute_with_direction()
        else:
            self._distribute_without_direction()

        return self.rapporteur

    def _distribute_with_direction(self):
        councillor = self.votes.filter(incident_type__lt=200).get()
        self._dispatch_votes(councillor.possession)

    def _dispatch_votes(self, possession):
        self.create_repporteur(self.votes.get(possession=possession))

        sentence = (
            models.Q(incident_type=None)
            | models.Q(incident_type__lt=200)
            | models.Q(models.Q(incident_type__gte=200) & ~models.Q(substitute=None))
        )

        query = self.votes.filter(sentence)
        for councillor in query.exclude(possession=possession):
            self.create_vote(councillor)

        query = self.votes.exclude(sentence)
        for councillor in query.exclude(possession=possession):
            self.create_vote(councillor, True)

        self.distributed_by = get_current_user()
        self.distributed_at = datetime.now()
        self.save()

    def _distribute_without_direction(self):
        scores = []
        e_scores = []
        selected_drs = None

        with transaction.atomic():
            for vote in self.votes.filter(
                models.Q(incident_type=None) | models.Q(incident_type__lt=200)
            ):
                score, created = DistributionRepporteurScore.objects.get_or_create(
                    possession=vote.possession
                )
                scores.append(score.pk)

            for vote in self.votes.filter(models.Q(incident_type__gt=200)):
                score, created = DistributionRepporteurScore.objects.get_or_create(
                    possession=vote.possession
                )
                e_scores.append(score.pk)

            DistributionRepporteurScore.objects.filter(
                pk__in=e_scores, score__gt=0
            ).update(score=(models.F("score") - 1))

            query = DistributionRepporteurScore.objects.filter(pk__in=scores)
            while not query.filter(score__lte=0).exists():
                step = int(
                    query.order_by("score")
                    .aggregate(min_score=models.Min("score"))
                    .get("min_score")
                    or 0
                )
                log.info("Regulando concorrencia, tirando %d do score de todos.", step)
                query.filter().update(score=(models.F("score") - step))

            random.seed(os.urandom(4096))

            concurrency = [drs for drs in query.filter(score__lte=0)]
            log.debug(
                "Concurrency: %s",
                [
                    concurrenty.possession.servidor.pessoa_fisica
                    for concurrenty in concurrency
                ],
            )
            selected_drs = random.choice(concurrency)
            self._dispatch_votes(selected_drs.possession)

    def prepare(self):
        cfg = Configuration.get_or_create("ejud")

        if not get_current_user().has_perm("council.prepare_distribution_rapporteur"):
            raise Exception(
                "Você não tem permissão para preparar a lista de distribuição."
            )

        president_id = cfg.get("presidentCouncil", None)
        inspector_id = cfg.get("inspectorCouncil", None)
        elected_id = cfg.get("electedCouncil", None)

        president = JobPosition.objects.get(pk=president_id) if president_id else None
        inspector = JobPosition.objects.get(pk=inspector_id) if inspector_id else None
        elected = JobPosition.objects.get(pk=elected_id) if elected_id else None
        extra_filters = {
            "movimentacaopessoal__movimentacaoposse__out_off_distribution_list": False
        }

        log.info(
            "Procurador Geral: %s",
            (
                Employee.with_job_position_for_distribution(president)
                if president
                else None
            ),
        )
        log.info(
            "Corregedor Geral: %s",
            (
                Employee.with_job_position_for_distribution(inspector)
                if inspector
                else None
            ),
        )
        log.info(
            "Eleitos Geral: %s",
            Employee.with_job_position_for_distribution(elected) if elected else None,
        )

        if president:
            query = Employee.with_job_position_for_distribution(president)
            self.votes.filter(councillor_type=1).delete()
            if query.exists():
                log.debug(query.filter())
                obj, created = self.votes.get_or_create(
                    possession=query.get().posses_ativas.get(quadro__cargo=president),
                    councillor_type=1,
                )

        if inspector:
            query = Employee.with_job_position_for_distribution(inspector)
            self.votes.filter(councillor_type=2).delete()
            if query.exists():
                obj, created = self.votes.get_or_create(
                    possession=query.get().posses_ativas.get(quadro__cargo=inspector),
                    councillor_type=2,
                )

        if elected:
            self.votes.filter(councillor_type=3).delete()
            for employee in Employee.with_job_position_for_distribution(elected):
                obj, created = self.votes.get_or_create(
                    possession=employee.posses_ativas.get(quadro__cargo=elected),
                    councillor_type=3,
                )

    @classmethod
    def default_icon(klass):
        return "icon-council icon-judicial-rapporteur-distribution"

    @property
    def title(self):
        return " ".join([self.codename, self.cached_number])

    def params(self):
        rst = PartLawsuit.params(self)

        rst.update(execution_organ=self.lawsuit.location, doc=self)

        return rst

    def save(self, *args, **kwargs):
        if not self.number:
            self.year = date.today().year
            self.number = self.next_number()

        self.cached_number = "%03d/%d" % (self.number, self.year)

        super(DistributionRapporteur, self).save(*args, **kwargs)


@type_part_lawsuit()
class ConvocationNotice(templated, with_number_for_year, models.Model):
    number = models.SmallIntegerField(
        blank=True,
    )
    year = models.SmallIntegerField(
        blank=True,
    )
    cached_number = models.CharField(
        blank=True, max_length=10, db_index=True, unique=True
    )
    distribution_rapporteur = models.ForeignKey(
        DistributionRapporteur,
        related_name="convocation_notices",
        on_delete=models.PROTECT,
    )
    convocation_state = models.SmallIntegerField(
        choices=Choice.get_choices_for("council", "CONVOCATION_STATE"), default=1
    )
    convocation = models.TextField(null=True, blank=True)
    cached_convocation = models.TextField(null=True, blank=True)
    publication = models.ForeignKey(
        "rh.Publicacao",
        related_name="convocation_notices",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    deadline_date = models.DateField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )

    codename = "Edital de convocação - Deprecated"

    class Meta:
        ordering = ("-year", "-number")

    @property
    def my_origin(self):
        return self

    @property
    def deadline_is_ended(self):
        return (self.deadline_days < 0) if self.deadline_date else False

    @property
    def deadline_days(self):
        if self.deadline_date:
            return (self.deadline_date - date.today()).days
        else:
            return None

    def estimate_deadline(self, base_date):
        cfg = Configuration.get_or_create("ejud")

        deadline_days = timedelta(
            days=int(cfg.get("deadlineConvocationNotice", 0) or 0)
        )
        self.deadline_date = base_date + deadline_days

    def request_publication(self):
        if self.convocation_state == 1:
            with transaction.atomic():

                self.signed_by = get_current_user()
                self.signed_at = datetime.now()

                self.cached_convocation = None
                self.cached_convocation = self.rendered

                self.convocation_state = 2

                self.save()

                ConvocationNoticeLegalSign.sign(self)

                self.publication = Publication.request_publication(
                    self.execution_organ,
                    number=self.number,
                    year=self.year,
                    internal=True,
                    publication_type=3,
                    document=self.rendered,
                    document_read_only=True,
                )

                self.with_check_sign = False

                self.save()

        else:
            raise Exception(
                "Não posso pedir publicação de uma convocação que se encontra em %s"
                % self.get_convocation_state_display()
            )

    @property
    def execution_organ(self):
        return self.distribution_rapporteur.lawsuit.location

    def _renderer(self):
        params = {
            "distribution": self.distribution_rapporteur,
            "execution_organ": self.execution_organ,
            "doc": self,
        }

        return self.template.render(params)

    def change_state(self, state):
        pass

    @property
    def icon_convocation_state(self):
        icon_map = {
            1: "icon-council icon-judicial-document-edit",
            2: "icon-council icon-judicial-document-publishing",
            3: "icon-council icon-judicial-document-published",
            4: "icon-council icon-judicial-document-destroied",
        }

        return {
            "iconCls": icon_map.get(int(self.convocation_state or 0), None),
            "title": self.get_convocation_state_display(),
        }
        pass

    @property
    def icon_publication(self):
        rst = {
            "iconCls": "icon-council icon-judicial-uknow",
            "title": "Ainda não foi solicitada a publicação",
        }

        if self.publication:
            rst = self.publication.icon_publication_state

        return rst

    @property
    def icons(self):
        return [self.icon_publication, self.icon_convocation_state]

    @property
    def rendered(self):
        data = [
            self.cached_convocation if self.cached_convocation else self._renderer()
        ]

        data += [sign.rendered for sign in self.legal_signs.filter()]

        if self.legal_signs.filter().exists():
            data.append(
                loader.get_template("judicial/legal_sign_fundament.html").render({})
            )

        return "".join(data)

    def save(self, *args, **kwargs):
        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)
            if getattr(self, "with_check_sign", True) and older.signed_by:
                raise Exception("Não posso modificar um documento assinado.")
        if not self.number:
            self.year = date.today().year
            self.number = self.next_number()

        self.cached_number = "%04d/%d" % (self.number, self.year)

        super(ConvocationNotice, self).save(*args, **kwargs)


class DistributionRepporteurScore(models.Model):
    possession = models.ForeignKey(
        "rh.MovimentacaoPosse", related_name="+", on_delete=models.PROTECT
    )
    total = models.SmallIntegerField(default=0)
    score = models.SmallIntegerField(default=0)

    def increase(self):
        self.total += 1
        self.score += 1
        self.save()

    def decrease(self):
        self.total -= 1
        self.score -= 1
        self.save()


class Councillor(models.Model):
    distribution_rapporteur = models.ForeignKey(
        DistributionRapporteur, related_name="votes", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    councillor_type = models.SmallIntegerField(
        choices=Choice.get_choices_for(
            "council", "COUNCILLOR_TYPE", empty=True, empty_label="Nenhum"
        ),
        default=1,
    )
    possession = models.ForeignKey(
        "rh.MovimentacaoPosse", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    substitute = models.ForeignKey(
        "rh.Servidor", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    incident_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("council", "INCIDENT"), null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)
    cache_formated_comment = models.TextField(null=True, blank=True)

    @property
    def formated_comment(self):
        if not self.comment:
            return None
        if self.cache_formated_comment:
            return self.cache_formated_comment
        else:
            tpl = loader.get_template("council/councillor_comment.html")
            return tpl.render({"doc": self})

    def validate(self):
        older = None

        if self.pk:
            older = Councillor.objects.get(pk=self.pk)

        if older and hasattr(self, "vote") and hasattr(older.vote, "rapporteur"):
            raise Exception(
                "Despois da relatoria distribuida, não é mais possivel modificar este item."
            )

        if older and (
            hasattr(older.distribution_rapporteur, "colegialdecision")
            and older.distribution_rapporteur.colegialdecision.signed_by
        ):
            raise Exception("Não posso modificar depois que houve a decisão colegiada.")

        incident_type = int(self.incident_type or 0)
        if incident_type > 0 and incident_type < 200:
            log.info(
                "Chencando incidentes positivos para distribuição de relatoria %s",
                self.distribution_rapporteur,
            )

            query = self.__class__.objects.filter(
                distribution_rapporteur=self.distribution_rapporteur,
                incident_type__lt=200,
            ).exclude(incident_type=None)

            query = query if not self.pk else query.exclude(pk=self.pk)

            if query.exists():
                raise Exception("Não posso ter mais de um incidente do tipo positivo.")

        if not (incident_type >= 200) and self.substitute:
            raise Exception(
                "Não posso indicar um substituto se não for um caso de incidente negativo."
            )

    def save(self, *args, **kwargs):
        self.validate()
        super(Councillor, self).save(*args, **kwargs)

    @property
    def who_is(self):
        who = 1

        if hasattr(self, "vote") and hasattr(self.vote, "rapporteur"):
            who = 3
        elif hasattr(self, "vote") and not self.vote.invalide:
            who = 5 if self.councillor_type == 1 else 2
        elif hasattr(self, "vote"):
            who = 4

        return who

    @property
    def icon_who(self):
        who_map = {
            1: {
                "iconCls": "icon-council icon-judicial-uknow",
                "title": "A distribuição ainda não foi sorteada",
            },
            2: {
                "iconCls": "icon-council icon-judicial-has-vote",
                "title": "Como conselheiro",
            },
            3: {
                "iconCls": "icon-council icon-judicial-has-rapporteur",
                "title": "Como Relator",
            },
            4: {
                "iconCls": "icon-council icon-council icon-judicial-has-null-vote",
                "title": "Vote invalidado",
            },
            5: {
                "iconCls": "icon-council icon-judicial-has-president",
                "title": "Como Presidente",
            },
        }

        return who_map.get(self.who_is, {})

    @property
    def icon_with_substitute(self):
        if self.substitute:
            return {
                "iconCls": "icon-council icon-judicial-with-substitute",
                "title": "Subistituindo %s" % self.possession.servidor.pessoa_fisica,
            }

    @property
    def icons(self):
        return [self.icon_who, self.icon_with_substitute]

    @property
    def employee(self):
        return self.possession.servidor if not self.substitute else self.substitute

    @property
    def owner(self):
        return self.possession.servidor

    class Meta:
        ordering = (
            "councillor_type",
            "possession__servidor__pessoa_fisica__nome",
        )


class Vote(models.Model):
    from_distribution = models.ForeignKey(
        DistributionRapporteur,
        related_name="rapporteur_votes",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    councillor = models.OneToOneField(
        Councillor, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    invalide = models.BooleanField(default=False)
    vote_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("council", "VOTE_TYPE"), null=True, blank=True
    )
    observation = models.TextField(null=True, blank=True)
    signed_by = models.ForeignKey(
        "auth.user", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signed_at = models.DateTimeField(null=True, blank=True)
    rendered_cache = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("councillor__possession__servidor__pessoa_fisica__nome",)

    def save(self, *args, **kwags):
        if self.read_only:
            raise Exception("Não é permitido modificar este voto.")

        super(Vote, self).save(*args, **kwags)

    def sign(self):
        if not self.read_only:
            self.signed_by = get_current_user()
            self.signed_at = datetime.now()
            self.rendered_cache = self.rendered
            self.save()

    @property
    def read_only(self):
        employee = employee_from_user(get_current_user())

        if self.pk:
            older = Vote.objects.get(pk=self.pk)

            if employee.work_locations.filter(pk=self.lawsuit.location).exists():
                return True if older.signed_by else False
            else:
                return True
        else:
            return False

    @property
    def lawsuit(self):
        return self.from_distribution.lawsuit

    @property
    def params(self):
        return {
            "doc": self.from_distribution,
            "rapporteur_document": self.from_distribution.colegialdecision.rapporteur_document,
            "vote": self,
        }

    def _renderer(self):
        return loader.get_template("judicial/council/vote.html").render(self.params)

    @property
    def rendered(self):
        return self.rendered_cache if self.rendered_cache else self._renderer()

    @property
    def vote(self):
        if self.vote_type:
            return self.get_vote_type_display()
        else:
            return "Voto não computado"

    @property
    def icons(self):
        return self.councillor.icons


class Rapporteur(Vote):
    pass


class VoteAttached(BaseAttached):
    vote = models.ForeignKey(
        Vote, related_name="attaches", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def save(self, *args, **kwags):
        document = self.vote.from_distribution

        if hasattr(document, "colegialdecision"):
            document = document.colegialdecision

        self.attached_document = document
        super(VoteAttached, self).save(*args, **kwags)


@type_part_lawsuit()
class RapporteurDocument(PartLawsuit):
    from_distribution = models.ForeignKey(
        DistributionRapporteur,
        related_name="rapporteur_document",
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    rapporteur = models.ForeignKey(
        Rapporteur, related_name="document", blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    rapporteur_vote_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("council", "RAPPORTEUR_VOTE_TYPE"),
        null=True,
        blank=True,
    )
    content = models.TextField(null=True, blank=True)
    reconsideration = models.OneToOneField(
        "self",
        related_name="reconsiderated",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Voto do Relator"

    def __str__(self):
        if self.rapporteur_vote_type:
            return " ".join(
                [
                    self.get_rapporteur_vote_type_display(),
                    "de",
                    # str(self.part_origin)
                ]
            )
        else:
            return "Undefined"

    def save(self, *args, **kwags):
        if not hasattr(self, "from_distribution"):
            """
            Pega a distribuição mais recente assinada, que não teve decisão colegiada.
            """
            query = DistributionRapporteur.objects.filter(
                pk__in=self.lawsuit.all_signed_documents.filter(
                    type_part="distributionrapporteur"
                ).values("pk")
            ).filter(colegialdecision=None)

            if query.exists():
                part = query.order_by("-signed_at").first()
                self.from_distribution = part.my_origin
            else:
                raise Exception(
                    'Não consegui definir qual "Distribuição Colegiada" deu origem a esta relatoria.'
                )

        if not hasattr(self, "rapporteur") and hasattr(self, "from_distribution"):
            councillor = self.from_distribution.votes.exclude(
                vote__rapporteur=None
            ).get()
            self.rapporteur = councillor.vote.rapporteur

        super(RapporteurDocument, self).save(*args, **kwags)

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    @property
    def part_origin(self):
        if hasattr(self.rapporteur.councillor.distribution_rapporteur, "part_origin"):
            return self.rapporteur.councillor.distribution_rapporteur.part_origin
        return None

    def reconsiderate(self):
        obj = self.__class__(
            # part_origin=self.part_origin,
            from_distribution=self.from_distribution,
            rapporteur=self.rapporteur,
            rapporteur_vote_type=self.rapporteur_vote_type,
            content=self.content,
            lawsuit=self.lawsuit,
            reconsideration=self,
        )

        obj.save()

        query = ColegialDecision.objects.filter(part_origin=self.part_origin)
        if query.exclude(signed_by=None).exists():
            raise Exception(
                "Não posso reconsiderar uma relatório que já foi levada a decisão colegiada."
            )
        else:
            for decision in query:
                decision.delete()

        return obj

    def effective_archivement(self):
        self.lawsuit.location = self.from_distribution.part_origin.create_location
        self.lawsuit.closed_by = get_current_user()
        self.lawsuit.closed_at = datetime.now()
        self.lawsuit.save()

        self.lawsuit.send_to(
            to=self.from_distribution.part_origin.create_location, finalizado=True
        )

    def effective_change_execution_organ(self):
        SwitchExecutionOrgan(
            lawsuit=self.lawsuit,
            from_colegial_decision=self.from_distribution.colegialdecision,
        ).save()

    def effectivate_return_execution_organ(self):
        RemittanceInternal(
            lawsuit=self.lawsuit,
            text="empty",
            department=self.from_distribution.part_origin.create_location,
        ).save()

    def effective_invalid(self):
        raise Exception(
            "Este relatório foi invalidade pois foi declarado %s.",
            self.get_rapporteur_vote_type_display(),
        )

    def effective(self, agree):
        yes_agree = no_agree = self.effective_invalid

        decisions = {
            1: {
                True: self.effective_archivement,
                False: self.effective_change_execution_organ,
            },
            2: {
                True: self.effective_change_execution_organ,
                False: self.effective_archivement,
            },
            3: {
                True: self.effectivate_return_execution_organ,
                False: self.effective_archivement,
            },
        }

        if self.rapporteur_vote_type < 200:
            decision_fn = decisions[self.rapporteur_vote_type].get(
                agree, self.effective_invalid
            )
            decision_fn()
        else:
            self.effective_invalid()

    def dispatch(self):
        self.rapporteur_vote_type = int(self.rapporteur_vote_type or 0)

        if self.rapporteur_vote_type > 200:
            log.info(
                "O relator se declarou %s", self.get_rapporteur_vote_type_display()
            )
            self._send_to_council()
            distribution = DistributionRapporteur(
                lawsuit=self.lawsuit, part_origin=self.part_origin
            )
            distribution.save()
            distribution.prepare()

            query = Councillor.objects.filter(
                distribution_rapporteur=distribution.part_origin.has_origin_for_distribution_rapporteur.filter()
            ).filter(incident_type__gt=100)

            for info in query:
                distribution.votes.filter(possession=info.possession).update(
                    incident_type=info.incident_type, comment=info.comment
                )

            distribution.votes.filter(
                possession=self.rapporteur.councillor.possession
            ).update(incident_type=self.rapporteur_vote_type, comment=self.content)
        else:
            log.info(
                "O voto do relator foi entregue e este é %s",
                self.get_rapporteur_vote_type_display(),
            )
            self._send_to_council()
            ColegialDecision(
                part_origin=self.part_origin,
                lawsuit=self.lawsuit,
                from_distribution=self.from_distribution,
            ).save()

    def sign_part(self):
        with transaction.atomic():
            super(RapporteurDocument, self).sign_part()

            self.dispatch()

    @classmethod
    def default_icon(klass):
        return "icon-council icon-judicial-rapporteur-document"

    def params(self):
        rst = PartLawsuit.params(self)

        rst.update(
            execution_organ=self.lawsuit.location,
            doc=self,
            sign={
                "organ": self.lawsuit.location,
                "moment_at": self.signed_at,
                "person": person_from_user(self.signed_by),
            },
        )

        return rst


@type_part_lawsuit()
class ColegialDecision(with_number_for_year, PartLawsuit):
    from_distribution = models.OneToOneField(
        DistributionRapporteur, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    part_origin = models.ForeignKey(
        PartLawsuit,
        related_name="has_origin_for_colegial_decision",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    number = models.SmallIntegerField(blank=True)
    year = models.SmallIntegerField(blank=True)
    cached_number = models.CharField(
        blank=True, max_length=10, db_index=True, unique=True
    )
    resume = models.TextField(null=True, blank=True)

    codename = "Decisão Colegiada"

    @classmethod
    def default_icon(klass):
        return "icon-council icon-judicial-colegial-decision"

    @property
    def votes(self):
        return self.from_distribution.rapporteur_votes.filter(invalide=False)

    @property
    def president_vote(self):
        return self.votes.filter(councillor__councillor_type=1)

    @property
    def rapporteur_vote(self):
        return self.votes.exclude(rapporteur=None).get()

    @property
    def rapporteur_document(self):
        return self.rapporteur_vote.rapporteur.document.filter(
            reconsiderated=None
        ).get()

    @property
    def summary(self):
        query = self.votes.filter()

        return {
            "total": query.count(),
            "yes": query.filter(vote_type=1).count(),
            "no": query.filter(vote_type=2).count(),
            "indecision": query.filter(vote_type=3).count(),
            "pendent": query.filter(vote_type=None).count(),
            "computed": query.exclude(vote_type=None).count(),
            "minimal": (query.count() / 2) + 1,
        }

    def effectivate_decision(self):
        total_votes = self.summary.get("total")
        yes_votes = self.summary.get("yes")
        no_votes = self.summary.get("no")
        indecision_votes = self.summary.get("indecision")
        minimal_votes = self.summary.get("minimal")

        if (yes_votes + no_votes) < minimal_votes:
            raise Exception(
                "Não foram computados o numéro minimo de %d votos." % minimal_votes
            )

        if yes_votes == no_votes:
            yes_votes += self.president_vote.filter(vote_type=1).count()
            no_votes += self.president_vote.filter(vote_type=2).count()

        if yes_votes > no_votes:
            """
            desabilitado a pedido servidores do conselho.

            self.rapporteur_document.effective(True)
            """
        elif yes_votes < no_votes:
            """
            desabilitado a pedido servidores do conselho.

            self.rapporteur_document.effective(False)
            """
        else:
            raise Exception("o presidente não votou")

    def sign_part(self):
        with transaction.atomic():
            super(ColegialDecision, self).sign_part()
            for vote in self.votes.filter(signed_by=None):
                vote.sign()

            self.effectivate_decision()

    @property
    def extra_pages_votes(self):
        return [
            {
                "page": vote.rendered,
                "at": self.signed_at if self.signed_at else datetime.now(),
            }
            for vote in self.votes
        ]

    def _all_extra_pages_complete(self):
        return (
            super(ColegialDecision, self)._all_extra_pages_complete()
            + self.extra_pages_votes
        )

    def save(self, *args, **kwargs):
        if not self.number:
            self.year = date.today().year
            self.number = self.next_number()

        self.cached_number = "%03d/%d" % (self.number, self.year)

        super(ColegialDecision, self).save(*args, **kwargs)


class Session(with_number_for_year, models.Model):
    number = models.SmallIntegerField(blank=True)
    year = models.SmallIntegerField(blank=True)
    cached_number = models.CharField(
        blank=True, max_length=10, db_index=True, unique=True
    )
    session_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("council", "SESSION_TYPE"), null=True, blank=True
    )
    session_status = models.SmallIntegerField(
        choices=Choice.get_choices_for("council", "SESSION_STATUS"),
        null=True,
        blank=True,
    )
    expected_date = models.DateField(null=True, blank=True)
    file_document = models.ForeignKey(
        Arquivo, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def next_number(self, year=None):
        year = year if year else date.today().year
        query = (
            self.__class__.objects.filter()
            .order_by("id")
            .aggregate(max_number=models.Max("number"))
        )

        return int(query.get("max_number") or 0) + 1

    @property
    def icon_session_type(self):
        if self.session_type == 1:
            return {
                "iconCls": "icon-council icon-judicial-session-ordinary",
                "title": "Ordinária",
            }
        elif self.session_type == 2:
            return {
                "iconCls": "icon-council icon-judicial-session-extra-ordinary",
                "title": "Extraordinária",
            }
        else:
            return {"iconCls": "icon-judicial icon-ejud-unsigned", "title": ""}

    @property
    def icon_session_status(self):
        if self.session_status == 1:
            return {
                "iconCls": "icon-judicial icon-ejud-open-proccess",
                "title": "Aberta",
            }
        elif self.session_status == 2:
            return {
                "iconCls": "icon-council icon-judicial-document-edit",
                "title": "Em execução",
            }
        elif self.session_status == 3:
            return {"iconCls": "icon-core icon-core-success", "title": "Finalizada"}
        else:
            return {"iconCls": "icon-judicial icon-ejud-unsigned", "title": ""}

    @property
    def icons(self):
        return [self.icon_session_type, self.icon_session_status]

    def save(self, *args, **kwargs):
        if not self.number:
            self.year = date.today().year
            self.number = self.next_number()

        self.cached_number = "%03d/%d" % (self.number, self.year)

        super(Session, self).save(*args, **kwargs)


class SessionItem(models.Model):
    session = models.ForeignKey(
        Session, related_name="session_items", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # part = models.ForeignKey(PartLawsuit, related_name='session_items', on_delete=models.CASCADE) # Parametro "on_delete" adicionado. (Django 2)
    title = models.CharField(max_length=200, null=True, blank=True)
    text = models.TextField()
    flag = models.BooleanField(default=False)

    @property
    def icon_flag(self):
        if self.flag:
            return {
                "iconCls": "icon-council icon-judicial-item-checked",
                "title": "Checado",
            }
        else:
            return {
                "iconCls": "icon-council icon-judicial-item-unchecked",
                "title": "Não checado",
            }

    @property
    def icon_decision(self):
        return {"iconCls": "icon-judicial icon-ejud-unsigned", "title": ""}

    @property
    def icons(self):
        return [
            self.icon_flag,
            self.icon_decision,
        ]


@type_part_lawsuit()
class DevolutionRecommendation(PartLawsuit):
    justification = models.TextField()
    devolution_to = models.ForeignKey(
        ExecutionOrgan,
        related_name="in_devolution_recommendation",
        verbose_name="Devolvido para",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Devolução com Recomendação"

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-devolution-recommendation"

    def sign_part(self):
        with transaction.atomic():
            super(DevolutionRecommendation, self).sign_part()

            current_moviment = self.lawsuit.current_moviment()
            current_moviment.do_send(
                location_destination=self.devolution_to.pk, advice=self.justification
            )

            self.lawsuit.location = self.devolution_to
            self.lawsuit.save()

    @property
    def sign_part_authorized(self):

        if not self.justification:
            raise Exception("Não foi inserido o texto na justificativa.")

        if self.signed:
            raise Exception("Não posso assinar um documento já assinado.")

        if self.devolution_to not in self.lawsuit.my_tracks_executionorgan:
            raise Exception(
                "Informe um destino válido para realizar a devolução com recomendação."
            )

        return True

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location
        attachments = self.attaches.filter()
        signed_by = person_from_user(self.signed_by)

        rst.update(
            execution_organ=execution_organ,
            attachments=attachments,
            signed_by=signed_by,
            doc=self,
        )

        return rst

    def save(self, *args, **kwargs):
        if not self.pk:
            if (
                self.lawsuit.parts.filter(
                    type_part=self._meta.model_name, signed_by=None
                ).count()
                > 0
            ):
                raise Exception("Há uma Devolução com Recomendação em aberto.")

        super(DevolutionRecommendation, self).save(*args, **kwargs)


@type_part_lawsuit()
class SwitchExecutionOrgan(PartLawsuit):
    from_colegial_decision = models.OneToOneField(
        ColegialDecision, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    legal_matter = models.ForeignKey(
        LegalMatter, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    execution_organ = models.ForeignKey(
        ExecutionOrgan,
        related_name="delegations",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField()

    codename = "Indicação de outro Orgão de Execução"

    def sign_part(self):
        with transaction.atomic():
            super(SwitchExecutionOrgan, self).sign_part()
            self.lawsuit.send_to(to=self.execution_organ)
            self.lawsuit.location = self.execution_organ
            self.lawsuit.save()


class ConvocationNoticeLegalSign(JudicialLegalSign, LegalSign):
    convocation = models.ForeignKey(
        ConvocationNotice, related_name="legal_signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _fill(self, convocation):
        super(ConvocationNoticeLegalSign, self)._fill()
        self.plain_content = convocation.rendered
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha224", self.content).hexdigest()

    @classmethod
    def sign(klass, convocation):
        obj = klass()
        obj.convocation = convocation
        obj._fill(convocation)
        obj.save()

        return obj
