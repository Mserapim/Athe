# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

from django.db import models, transaction
from django.db.models import Max, Min, Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from contrib.daterange import NewDateRange
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from ged.models import Arquivo as File
from rh.models import Localidade
from standard.models import AuditTimestampModel, Choice
from auditlog.registry import auditlog


log = getLogger(__name__)


class NonWorkingDay(AuditTimestampModel):
    description = models.CharField("Descrição", max_length=50)
    is_partial = models.BooleanField("Parcial", default=False)
    start_date = models.DateTimeField("Data inicial")
    end_date = models.DateTimeField("Data final", blank=True, null=True)
    abrangency = models.PositiveSmallIntegerField(
        "Abrangência",
        choices=Choice.get_choices_for("usefulday", "ABRANGENCY"),
        blank=True,
        null=True,
    )
    kind = models.PositiveSmallIntegerField(
        "Tipo", choices=Choice.get_choices_for("usefulday", "KIND")
    )
    document = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        verbose_name="Arquivo",
        blank=True,
        null=True,
        related_name="%(class)ss",
    )
    places = models.ManyToManyField(
        Localidade, related_name="%(class)ss", verbose_name="Cidades", blank=True
    )

    class Meta:
        ordering = ("start_date", "abrangency")

    def __str__(self):
        return "%s" % self.description

    @property
    def date_period(self):
        """Data/Período

        Retorna a data ou período de ocorrência do evento
        """

        def partial_strfdatetime():
            if self.end_date:
                return " a " + datetime.strftime(self.end_date, "%d/%m/%Y às %H:%M")
            return ""

        def total_strfdate():
            if self.end_date:
                return " a " + datetime.strftime(self.end_date, "%d/%m/%Y")
            return ""

        STRF_DATE_MAP = {
            1: {False: datetime.strftime(self.start_date, "%d/%m/%Y")},  # Feriado
            2: {  # PF
                True: datetime.strftime(self.start_date, "%d/%m/%Y às %H:%M")
                + partial_strfdatetime(),
                False: datetime.strftime(self.start_date, "%d/%m/%Y")
                + total_strfdate(),
            },
            3: {  # Suspensão
                True: datetime.strftime(self.start_date, "%d/%m/%Y às %H:%M")
                + partial_strfdatetime(),
                False: datetime.strftime(self.start_date, "%d/%m/%Y")
                + total_strfdate(),
            },
            4: {  # Recesso
                True: datetime.strftime(self.start_date, "%d/%m/%Y às %H:%M")
                + partial_strfdatetime(),
                False: datetime.strftime(self.start_date, "%d/%m/%Y")
                + total_strfdate(),
            },
        }

        strf_date = STRF_DATE_MAP.get(self.kind).get(self.is_partial)

        return strf_date

    @property
    def has_places(self):
        return True if self.places.count() > 0 else False

    @classmethod
    def get_year_list(cls):
        """Fornece uma lista de ano/calendário

        Cria uma lista referência dos ano/calendário que podem
        ser usados como parâmetro de cópia para outro ano/calendário
        """

        min_year = cls.objects.aggregate(min=Min("start_date")).get("min").year
        max_year = cls.objects.aggregate(max=Max("start_date")).get("max").year

        return list(range(min_year, max_year + 2))

    @classmethod
    def copy(cls, opts):
        """Copia datas ou intervalos destas

        Realiza uma cópia de eventos de data de um ano base definido
        pelo usuário. Este último ainda pode informar o tipo de data
        que quer que seja copiado para o "novo" ano.
        """

        base_year = opts.get("base_year", None)
        destiny_year = opts.get("destiny_year", None)

        if base_year and destiny_year:
            if base_year != destiny_year:
                kinds = []
                if opts.get("holiday", None):
                    kinds.append(1)
                if opts.get("facultative", None):
                    kinds.append(2)
                if opts.get("suspension", None):
                    kinds.append(3)
                if opts.get("recess", None):
                    kinds.append(4)

                if len(kinds) == 0:
                    raise Exception(
                        "Não há o que copiar, já que não foi selecionado nenhum tipo de data"
                    )

                query = NonWorkingDay.objects.filter(
                    start_date__year=base_year, kind__in=kinds
                )

                with transaction.atomic():
                    for i in query:
                        end_date = None

                        start_date = i.start_date.replace(year=int(destiny_year))
                        if i.end_date:
                            interval = i.end_date - i.start_date
                            end_date = start_date + interval

                        object, created = cls.objects.get_or_create(
                            description=i.description,
                            is_partial=i.is_partial,
                            start_date=start_date,
                            end_date=end_date,
                            abrangency=i.abrangency,
                            kind=i.kind,
                            document=i.document,
                            # places=i.places
                        )
                        object.places.add(*[o for o in i.places.all()])

            else:
                raise Exception("Favor, informar ano base diferente do ano destino")
        else:
            raise Exception("Ano base ou destino são inválido(s)")

    def validate_dates(self):
        if self.kind == 3:  # kind = 3 (Suspensão)
            if self.end_date is None:
                raise Exception("O campo data final deve ser preenchido.")

        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise Exception("A data de inicio deve ser menor que a data final")

    def clean_places_and_delete_current_parsenonworkingday(self):
        if self.pk:
            if self.old_fields.get("is_partial") or self.is_partial:
                check_processed = self.parsenonworkingdays.filter(processed=True)
                if check_processed:
                    raise Exception(
                        "Não posso alterar o campo Parcial. O registro já foi processado."
                    )

            if self.old_fields.get("end_date"):
                check_processed = self.parsenonworkingdays.filter(
                    processed=True
                ).exclude(
                    parse_date__gte=self.start_date, parse_date__lte=self.end_date
                )

                if check_processed:
                    raise Exception(
                        "Existem registros processados fora do intervalo de datas informado."
                    )

            elif self.old_fields.get("start_date"):
                if self.end_date:
                    check_processed = self.parsenonworkingdays.filter(
                        processed=True
                    ).exclude(
                        parse_date__gte=self.start_date, parse_date__lte=self.end_date
                    )
                else:
                    check_processed = self.parsenonworkingdays.filter(
                        processed=True, parse_date=self.old_fields.get("start_date")
                    )

                if check_processed:
                    raise Exception(
                        "Não é possível modificar a data. O registro já foi processado."
                    )

            if self.old_fields.get("abrangency"):
                if self.parsenonworkingdays.filter(processed=True):
                    raise Exception(
                        "Não é possível editar este registro. Ele já foi processado."
                    )

                if self.old_fields.get("abrangency") == 3:
                    self.places.clear()

            self.parsenonworkingdays.filter(processed=False).delete()

    def insert_in_parsenonworkingday(self):
        objs = []
        _start_date = self.start_date.date()
        _end_date = self.end_date.date() if self.end_date else None

        def create_objects_parsenonworkingday():
            objs.append(
                ParseNonWorkingDay(
                    nonworkingday=self,
                    parse_date=_start_date,
                    place=place,
                    created_by=get_current_user(),
                    modified_by=get_current_user(),
                )
            )

        if self.abrangency == 3:
            _places = self.places.all()

            if _end_date:
                while _start_date <= _end_date:
                    if _places:
                        for place in _places:
                            if not self.parsenonworkingdays.filter(
                                parse_date=_start_date, place=place
                            ):
                                create_objects_parsenonworkingday()
                    _start_date = _start_date + timedelta(days=1)
            else:
                if _places:
                    for place in _places:
                        if not self.parsenonworkingdays.filter(
                            parse_date=_start_date, place=place
                        ):
                            create_objects_parsenonworkingday()

        else:
            place = None
            if _end_date:
                while _start_date <= _end_date:
                    if not self.parsenonworkingdays.filter(parse_date=_start_date):
                        create_objects_parsenonworkingday()
                    _start_date = _start_date + timedelta(days=1)
            else:
                if not self.parsenonworkingdays.filter(parse_date=_start_date):
                    create_objects_parsenonworkingday()

        ParseNonWorkingDay.objects.bulk_create(objs)

    def validar_datas_recesso(self):
        if self.kind == 4:  # Recesso
            if self.end_date:
                if not (
                    (
                        self.start_date.date()
                        >= datetime(self.start_date.year, 12, 20).date()
                        and self.end_date.date()
                        <= datetime(self.start_date.year + 1, 1, 6).date()
                    )
                    or (
                        self.start_date.date()
                        >= datetime(self.start_date.year - 1, 12, 20).date()
                        and self.end_date.date()
                        <= datetime(self.start_date.year, 1, 6).date()
                    )
                ):
                    raise Exception(
                        "O período de Recesso deve estar entre as datas: 20/12 - 06/01!"
                    )
            else:
                if (
                    self.start_date.date()
                    < datetime(self.start_date.year, 12, 20).date()
                    and self.start_date.date()
                    > datetime(self.start_date.year, 1, 6).date()
                ):
                    raise Exception(
                        "A data de Recesso deve estar dentro do período: 20/12 - 06/01!"
                    )

    def validar_duplicidade_recesso(self):
        if not self.end_date:
            query = NonWorkingDay.objects.filter(kind=4).filter(  # Recesso
                Q(Q(start_date=self.start_date) & Q(end_date__isnull=True))
                | Q(
                    Q(start_date__lte=self.start_date)
                    & Q(end_date__gte=self.start_date)
                )
            )
        else:
            query = NonWorkingDay.objects.filter(kind=4).filter(  # Recesso
                Q(
                    Q(start_date__gte=self.start_date)
                    & Q(start_date__lte=self.end_date)
                    & Q(end_date__isnull=True)
                )
                | Q(Q(start_date__lte=self.end_date) & Q(end_date__gte=self.start_date))
            )

        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            raise Exception("Já existe um Recesso cadastrado nesta data/período!")

    def validate_before_save(self):
        self.validate_dates()
        self.validar_datas_recesso()
        self.validar_duplicidade_recesso()

    def execute_before_save(self):
        self.clean_places_and_delete_current_parsenonworkingday()

    def execute_after_save(self):
        self.insert_in_parsenonworkingday()

    def atribui_abrangencia(self):
        if self.kind == 4:  # Recesso
            self.abrangency = 2  # Estadual

    def save(self, *args, **kwargs):
        self.atribui_abrangencia()
        self.validate_before_save()
        with transaction.atomic():
            self.execute_before_save()
            super(NonWorkingDay, self).save(*args, **kwargs)
            self.execute_after_save()

    def delete(self, *args, **kwargs):
        if self.parsenonworkingdays.filter(processed=True).exists():
            raise Exception("Este registro já foi processado e não pode ser removido")

        super(NonWorkingDay, self).delete(*args, **kwargs)


@receiver(m2m_changed, sender=NonWorkingDay.places.through)
def edit_and_remove_nonworkingday_places(sender, instance, action, **kwargs):

    def create_objects_parsenonworkingday_with_places():
        objs.append(
            ParseNonWorkingDay(
                nonworkingday=instance,
                parse_date=_start_date,
                place_id=_pk,
                created_by=get_current_user(),
                modified_by=get_current_user(),
            )
        )

    if instance.parsenonworkingdays.filter(processed=True):
        raise Exception(
            "Não foi possível alterar esse registro. Registro já processado."
        )

    if action == "post_add":
        objs = []
        _start_date = instance.start_date.date()
        _end_date = instance.end_date.date() if instance.end_date else None

        if _end_date:
            while _start_date <= _end_date:
                for _pk in kwargs.get("pk_set"):
                    create_objects_parsenonworkingday_with_places()
                _start_date = _start_date + timedelta(days=1)
        else:
            for _pk in kwargs.get("pk_set"):
                create_objects_parsenonworkingday_with_places()

        ParseNonWorkingDay.objects.bulk_create(objs)

    if action == "post_remove":
        instance.parsenonworkingdays.filter(place__in=kwargs.get("pk_set")).delete()

    if action == "post_clear":
        instance.parsenonworkingdays.all().delete()


class ParseNonWorkingDay(AuditTimestampModel):
    nonworkingday = models.ForeignKey(
        NonWorkingDay,
        on_delete=models.CASCADE,
        verbose_name="Dia não útil",
        related_name="%(class)ss",
    )
    parse_date = models.DateTimeField("Data")
    place = models.ForeignKey(
        Localidade,
        on_delete=models.CASCADE,
        verbose_name="Cidade",
        related_name="%(class)ss",
        blank=True,
        null=True,
    )
    processed = models.BooleanField(default=False, verbose_name="Registro processado?")
    is_partial = models.BooleanField(default=False)

    class Meta:
        unique_together = ("nonworkingday", "parse_date", "place")

    def __str__(self):
        return "%s" % self.nonworkingday.description

    @classmethod
    def occurrences_on_the_date(cls, date):

        return cls.objects.filter(
            parse_date__year=date.year,
            parse_date__month=date.month,
            parse_date__day=date.day,
        )

    @classmethod
    def occurrences_not_processed_on_the_date(cls, date):
        return cls.occurrences_on_the_date(date=date).filter(processed=False)

    @classmethod
    def process_occurrences(cls, occurrences=[]):
        cls.objects.filter(pk__in=occurrences).update(processed=True)

    @classmethod
    def national_holidays(
        cls, date_range=None, exclude_weekend=True, abrangency=1, is_partial=False
    ):
        """
        Este método retorna a quantidade de feriados nacionais de dia inteiro dentro de um NewDateRange.
        O fim de semana pode ser excluído informando excluir_weekend=False.
        Valor padrão para tipo: 1 - (NACIONAL).
        Valor padrão para parte_dia: 4 - (dia inteiro).
        """
        if date_range is None:
            raise Exception("NewDateRange não informado.")

        holidays = []
        holidays_found = cls.objects.filter(
            nonworkingday__abrangency=abrangency,
            is_partial=is_partial,
            parse_date__gte=datetime(
                date_range.start_date.year,
                date_range.start_date.month,
                date_range.start_date.day,
            ),
            parse_date__lte=datetime(
                date_range.end_date.year,
                date_range.end_date.month,
                date_range.end_date.day,
            ),
        )

        for h in holidays_found:
            if not (exclude_weekend and NewDateRange.day_weekend(h.parse_date)):
                holidays.append([h.pk, h.parse_date])

        return holidays

    @classmethod
    def holidays_days(
        cls, date_range=None, exclude_weekend=True, abrangency=[], is_partial=False
    ):

        if date_range is None:
            raise Exception("NewDateRange não informado.")

        holidays = []
        holidays_found = cls.objects.filter(
            nonworkingday__abrangency__in=abrangency,
            is_partial=is_partial,
            parse_date__gte=datetime(
                date_range.start_date.year,
                date_range.start_date.month,
                date_range.start_date.day,
            ),
            parse_date__lte=datetime(
                date_range.end_date.year,
                date_range.end_date.month,
                date_range.end_date.day,
            ),
        )

        for h in holidays_found:
            if not (exclude_weekend and NewDateRange.day_weekend(h.parse_date)):
                holidays.append([h.pk, h.parse_date])

        return holidays


auditlog.register(NonWorkingDay)
