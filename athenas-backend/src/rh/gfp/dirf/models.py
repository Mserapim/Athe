# -*- coding: utf-8 -*-

import codecs
import os
from datetime import date, datetime

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify


from contrib.daterange import NewDateRange
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from engine.models import NullTaskSession
from ged.models import Arquivo as FileGED
from rh.gfp.models import IRRF, RRA, Evento, FolhaEvento, Folha, RRAEmployee
from rh.models import Molestia, Pessoa, PessoaFisica, Servidor
from rh.pensao.models import Pensao as Pension
from standard.models import AuditTimestampModel, Choice, Configuration

log = getLogger(__name__)


LIST_IDENTIFIERS_PA = [
    "BPFDEC-RTPA",
    "BPFRRA-RTPA",
]

INFORMATION_TAGS = {
    "BPFDEC-RIAP": "Rendimentos Isento - Outros",
    "BPFDEC-RIO": "Rendimentos Isento - Outros",
    "BPFDEC-RTPA": "Pensão Alimenticia",
    "BPFRRA-RTPA": "Pensão Alimenticia",
}

DEBUG_PERSONS = [
    # 10738,
    # 346,
    # 725,
    # 860, 512, 194, 11977, 349, 370, 1039, 795, 21425,  # GERAIS
    # 730,  # APOSENTADOS
    # 39,  # PENSAO ALIMENTCIA
    # 627,  # 176, 290, 627, 951, 1048  # PENSAO MORTE
    # 21425,  # 10036, 11936, 10501, 11898, 473, 576
    # 676,  # RRA
    # 11950, 51753, 12261, 325, 377, 22230
]

DEBUG_EMPLOYES = [
    # 91108,
    # 86208,  # PA
    # 1322301,
    # 75507,
]


def current_year():
    return datetime.now().year


class DirfResumos(models.Model):
    pessoa = models.ForeignKey(
        Pessoa, related_name="dirf_resumos", on_delete=models.CASCADE
    )
    ano = models.SmallIntegerField()
    mes = models.SmallIntegerField()
    valor = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    tipo = models.CharField(max_length=20, null=False, db_index=True, default="DIARIA")
    identifier = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("dirf", "IDENTIFIERS_DIRF"),
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "dirf_resumos"
        unique_together = (["pessoa", "ano", "mes", "tipo", "identifier"],)
        ordering = ("-ano", "pessoa", "mes", "identifier")


class DirfSummary(AuditTimestampModel):
    DEFAULT_USER = "athenas"

    code = models.ForeignKey(
        "NaturezaRendimento", related_name="summaries", on_delete=models.PROTECT
    )
    identifier = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("dirf", "IDENTIFIERS_DIRF")
    )
    info = models.CharField(
        max_length=50, null=False, db_index=True, default="", blank=True
    )
    person = models.ForeignKey(
        Pessoa, related_name="dirf_summaries", on_delete=models.CASCADE
    )
    calendar_year = models.SmallIntegerField()
    value_01 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_02 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_03 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_04 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_05 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_06 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_07 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_08 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_09 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_10 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_11 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_12 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    value_13 = models.DecimalField(
        max_digits=11, decimal_places=2, default=0, blank=True
    )
    rra = models.ForeignKey(
        RRA,
        verbose_name="RRA",
        related_name="dirf_summaries",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    pensioner = models.ForeignKey(
        PessoaFisica,
        related_name="dirf_summaries_pensioner",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    dirf_created = models.BooleanField(default=False, blank=True)

    class Meta:
        unique_together = (
            ["person", "calendar_year", "info", "identifier", "pensioner", "code"],
        )
        ordering = ("-calendar_year", "code", "person", "identifier", "info")

    @property
    def choice(self):
        return Choice.objects.get(
            app_label="dirf", name="IDENTIFIERS_DIRF", value=self.identifier
        )

    def __str__(self):
        return "%s:%s %s %s" % (
            self.choice.label,
            self.info,
            self.person,
            self.pensioner,
        )

    def save(self, *args, **kwargs):
        if (
            self.choice.label.startswith("BPF")
            and not hasattr(self.person, "pessoafisica")
        ) or (
            self.choice.label.startswith("BPJ")
            and not hasattr(self.person, "pessoajuridica")
        ):
            raise Exception(
                "Identificador Id-DIRF (%s) incompatível com tipo de pessoa (%s)!"
                % (self.choice.label, type(self.person))
            )
        self.value_01 = 0 if self.value_01 is None else self.value_01
        self.value_02 = 0 if self.value_02 is None else self.value_02
        self.value_03 = 0 if self.value_03 is None else self.value_03
        self.value_04 = 0 if self.value_04 is None else self.value_04
        self.value_05 = 0 if self.value_05 is None else self.value_05
        self.value_06 = 0 if self.value_06 is None else self.value_06
        self.value_07 = 0 if self.value_07 is None else self.value_07
        self.value_08 = 0 if self.value_08 is None else self.value_08
        self.value_09 = 0 if self.value_09 is None else self.value_09
        self.value_10 = 0 if self.value_10 is None else self.value_10
        self.value_11 = 0 if self.value_11 is None else self.value_11
        self.value_12 = 0 if self.value_12 is None else self.value_12
        self.value_13 = 0 if self.value_13 is None else self.value_13
        super(DirfSummary, self).save(*args, **kwargs)


class DialectManager(models.Manager):

    def get_by_natural_key(self, nome):
        return self.get(nome=nome)


class Dialect(models.Model):
    """Classe que gerencia as configurações de layout e geração da DIRF.

    Attributes:
        nome (TYPE): Description
        calendar_year (TYPE): Description
        reference_year (TYPE): Description
        identificador_layout (TYPE): Description
        last_dirf_file (TYPE): Description
        last_processed_summary (TYPE): Description
        copy_from (ForeignKey): Auto-relation
    """

    nome = models.CharField(max_length=60, blank=True, null=False, unique=True)
    calendar_year = models.PositiveSmallIntegerField(blank=True, default=current_year)
    reference_year = models.PositiveSmallIntegerField(blank=True, default=current_year)
    identificador_layout = models.CharField(max_length=7, blank=True, null=True)
    last_processed_summary = models.DateTimeField(null=True, blank=True)
    last_dirf_file = models.ForeignKey(
        "ged.Arquivo", null=True, blank=True, on_delete=models.SET_NULL
    )
    last_receipt = models.CharField(max_length=32, blank=True, null=True)
    copy_from = models.ForeignKey(
        "Dialect", blank=True, null=True, on_delete=models.SET_NULL
    )

    objects = DialectManager()

    class Meta:
        """Meta Class de ``Dialect``.

        Attributes:
            ordering (tuple): Parâmetros para ordenação dos objetos do modelo
        """

        ordering = ("-reference_year", "-calendar_year")

    def natural_key(self):
        """Chave natual para ser usada no dumpdata e loaddata.

        Returns:
            tuple: uma tupla contendo apenas o nome do ``Dialect``, que é único
        """
        return (self.nome,)

    def __str__(self):
        """Unicode do modelo.

        Returns:
            unicode string: "DIRF {reference_year}/{calendar_year}"
        """
        return "DIRF %d/%d" % (self.reference_year, self.calendar_year)

    def save(self, *args, **kargs):
        """Save do modelo.

        Args:
            *args (TYPE): Atributos posicionais
            **kargs (TYPE): Atributos nomeados

        Returns:
            TYPE: não há retorno
        """
        if not self.pk:
            if not self.nome:
                self.nome = "ano-calendario-%04d" % self.reference_year
            self.last_dirf_file = None
        log.debug(self.__dict__)
        models.Model.save(self, *args, **kargs)

        if self.copy_from and not self.tokens.exists():
            self.copy()

        if self.last_receipt:
            declaration = Declaracao.objects.filter(ano_base=self.calendar_year).first()
            if not declaration.published:
                declaration.published = True
                declaration.save()

    def copy(self):

        if self.copy_from:
            from_dialect = self.copy_from
            try:
                # from_dialect.save()
                for token in from_dialect.tokens.all():
                    new_token, created = Token.objects.get_or_create(
                        dialect=self,
                        nome=token.nome,
                        slug=slugify(token.nome),
                        id_receita=token.id_receita,
                        tipo=token.tipo,
                        identifier=token.identifier,
                        extra_info=token.extra_info,
                    )
                    log.debug("%s %s" % ("C" if created else "U", new_token.slug))
                    new_token.eventos.add(*[ev for ev in token.eventos.all()])
            except Exception as e:
                log.exception(e)
                raise e

    def get_natur_rend(self, employee, rra_employee):
        codigo_nat_rend = "0561" if not rra_employee else "1889"
        if employee.type_by_possession in ["SAP", "MAP", "MAP2", "APO", "BFP"]:
            codigo_nat_rend = "3533"

        return NaturezaRendimento.objects.get(codigo=codigo_nat_rend)

    def _summarize_totals_default(
        self,
        employee,
        identifier,
        q_entries,
        pensioner=None,
        pensioner_type=0,
        rra_employee=None,
    ):
        if not q_entries.exists():
            return {}

        totals = self._get_values_default(employee, identifier, q_entries)

        person = (
            pensioner if (pensioner and pensioner_type == 2) else employee.pessoa_fisica
        )
        for info in totals:
            info_dec = info if info else str(pensioner or "")

            ds, created = DirfSummary.objects.get_or_create(
                person=person,
                calendar_year=self.calendar_year,
                info=info_dec,
                identifier=identifier["id"],
                rra=rra_employee.rra if rra_employee else None,
                pensioner=(
                    pensioner if not (pensioner and pensioner_type == 2) else None
                ),
                dirf_created=True,
                code=self.get_natur_rend(employee, rra_employee),
            )
            has_value = False
            for x in range(1, 14):
                setattr(ds, "value_%02d" % x, totals[info][x - 1] or 0)
                if getattr(ds, "value_%02d" % x, 0):
                    has_value = True

            if has_value or identifier["label"] == "BPFRRA-QTMESES":
                ds.save()
            else:
                ds.delete()

        return totals

    def _summarize_totals_bpfdec_rtpa(
        self,
        employee,
        identifier,
        q_entries,
        pensioner=None,
        pensioner_type=0,
        rra_employee=None,
    ):
        """Sumariza os lancamentos de q_entries para o identificador BPFDEC-RTPA
        (Pensao alimenticia de quem recebe RRA).
        Args:
            employee (rh.Servidor): Servidor que será sumarizado
            identifier (dict): identificador da DIRF: 'id', 'label'
            q_entries (QuerySet): Queryset com os lancametnos a serem sumarizados
            pensioner (None, optional): Pensionista, caso seja lancamentos de um pensionista
            pensioner_type (int, optional):
                Tipo do pensionista: 0 - Sem penssao | 1 - pensao alimenticia | 2 - pensao por morte/partilha
            rra_employee (None, optional): RRA do servidor

        Returns:
            TYPE: Description
        """

        if identifier["label"].startswith("BPFDEC"):
            q_entries = q_entries.filter(rra_employee=None)
        else:
            q_entries.exclude(rra_employee=None)

        if not q_entries.exists():
            return {}

        q_entries = (
            q_entries.order_by(
                "contracheque__pensioner__cpf",
                "contracheque__pensioner__data_nascimento",
            )
            .values("contracheque__pensioner")
            .distinct()
        )
        for res in q_entries:
            if res["contracheque__pensioner"]:
                pensioner = PessoaFisica.objects.get(pk=res["contracheque__pensioner"])
                q_rtpa_entries = q_entries.filter(
                    contracheque__pensioner=pensioner,
                    contracheque__employee_pays_pension=1,
                )
                totals = self._summarize_totals_default(
                    employee,
                    identifier,
                    q_rtpa_entries,
                    pensioner=pensioner,
                    pensioner_type=1,
                    rra_employee=rra_employee,
                )

        return {}

    def _summarize_totals_bpfrra_rtpa(
        self,
        employee,
        identifier,
        q_entries,
        pensioner=None,
        pensioner_type=0,
        rra_employee=None,
    ):
        """Sumariza os lancamentos de q_entries para o identificador BPFRRA-RTPA
        (Pensao alimenticia de que mrecebe RRA).
        Args:
            employee (rh.Servidor): Servidor que será sumarizado
            identifier (dict): identificador da DIRF: 'id', 'label'
            q_entries (QuerySet): Queryset com os lancametnos a serem sumarizados
            pensioner (None, optional): Pensionista, caso seja lancamentos de um pensionista
            pensioner_type (int, optional):
                Tipo do pensionista: 0 - Sem penssao | 1 - pensao alimenticia | 2 - pensao por morte/partilha
            rra_employee (None, optional): Description

        Returns:
            TYPE: Description
        """
        return self._summarize_totals_bpfdec_rtpa(
            employee,
            identifier,
            q_entries,
            pensioner=pensioner,
            pensioner_type=pensioner_type,
            rra_employee=rra_employee,
        )

    def get_list_identifiers(self):
        identifiers_ids = [token.identifier for token in self.tokens.all()]
        choices = Choice.objects.filter(
            app_label="dirf",
            name="IDENTIFIERS_DIRF",
            value__in=identifiers_ids,
        )

        return [{"id": choice.value, "label": choice.label} for choice in choices]

    def summarize_employee(self, employee):
        d_year = NewDateRange(
            date(self.calendar_year, 1, 1), date(self.calendar_year, 12, 31)
        )
        payrolls = Folha.objects.filter(dt_pagamento__year=self.calendar_year)
        q_entries = (
            FolhaEvento.objects.order_by("servidor_id")
            .filter(
                models.Q(
                    contracheque__servidor__pessoa_fisica=employee.pessoa_fisica,
                    status__in=("CT", "CE", "BS"),
                )
                & (
                    models.Q(contracheque__folha__in=payrolls)
                    | models.Q(reference_month=13, reference_year=self.calendar_year)
                )
            )
            .exclude(
                contracheque__pensioner=None, contracheque__employee_pays_pension=2
            )
            .select_related(
                "contracheque__servidor__pessoa_fisica",
                "contracheque__pensioner",
                "evento",
            )
        )

        if q_entries.exists():
            # comentando query abaixo temparariamente, desconsiderando lógicas relacionadas à RRA

            # q_rras = RRAEmployee.objects.filter(employee__pessoa_fisica=employee.pessoa_fisica)
            # rras = [rra_employee for rra_employee in q_rras if q_entries.filter(rra_employee=rra_employee).exists()]
            # rras.append(None)  # Para lancamentos sem RRA

            # Pensões vigentes no ano do servidor -------
            q_pensions = Pension.objects.filter(
                servidor__pessoa_fisica=employee.pessoa_fisica
            ).exclude(
                models.Q(data_inicio__gt=d_year.last)
                | (~models.Q(data_fim=None) & models.Q(data_fim__lt=d_year.first))
            )
            pensioners_pm = set(
                [pm.pensionista for pm in q_pensions.filter(type_of_pension=2)]
            )
            pensioners_pm.add(None)  # Para lancamentos do proprio servidor

            list_identifiers = self.get_list_identifiers()
            for identifier in list_identifiers:
                tokens = self.tokens.filter(identifier=identifier["id"])

                if identifier["label"] == "BPFRRA-QTMESES":
                    ident_id = next(
                        ident
                        for ident in list_identifiers
                        if ident["label"] == "BPFRRA-RTRT"
                    )["id"]
                    custom_tokens = self.tokens.filter(identifier=ident_id)
                    events = Evento.objects.filter(as_token__in=custom_tokens)
                else:
                    events = Evento.objects.filter(as_token__in=tokens)

                q_id_entries = q_entries.filter(evento__in=events)

                for pensioner in pensioners_pm:
                    pensioner_type = 2 if pensioner else 0
                    if pensioner:
                        q_entries_ident = q_id_entries.filter(
                            contracheque__pensioner=pensioner,
                            contracheque__employee_pays_pension=pensioner_type,
                        )
                    else:
                        q_entries_ident = q_id_entries.exclude(
                            contracheque__employee_pays_pension=2
                        )

                    # definindo qual método de sumarização escolher
                    method_name = f"_summarize_totals_{identifier['label'].lower().replace('-', '_')}"
                    _summarize_totals = getattr(
                        self, method_name, self._summarize_totals_default
                    )

                    totals = _summarize_totals(
                        employee,
                        identifier,
                        q_entries_ident,
                        pensioner=pensioner,
                        pensioner_type=pensioner_type,
                    )

                # comentando lógica abaixo temporariamente, desconsiderando lógicas relacionadas à RRA

                # for rra_employee in rras:
                #     rra_identifier = identifier['label'].find('RRA') >= 0
                #     if (rra_identifier and rra_employee) or (not rra_identifier and not rra_employee):
                #         # Executa apenas se o identificador for compativel com o rra_employee
                #         # ou seja, identificado de RRA com presença de RRA ou o contrário
                #         q_rra_entries = q_id_entries.filter(rra_employee=rra_employee)
                #         for pensioner in pensioners_pm:
                #             pensioner_type = 2 if pensioner else 0
                #             q_pm_rra_entries = q_rra_entries

                #             if pensioner:
                #                 q_pm_rra_entries = q_pm_rra_entries.filter(
                #                     contracheque__pensioner=pensioner, contracheque__employee_pays_pension=pensioner_type)
                #             else:
                #                 q_pm_rra_entries = q_pm_rra_entries.exclude(contracheque__employee_pays_pension=2)

                #             # definindo qual método de sumarização escolher
                #             method_name = f"_summarize_totals_{identifier['label'].lower().replace('-', '_')}"
                #             log.info(f">>> method_name: {method_name}")
                #             _summarize_totals = getattr(self, method_name, self._summarize_totals_default)

                #             log.info(f">>> summarize_employee > _summarize_totals: {_summarize_totals}")
                #             log.info(f">>> summarize_employee > q_pm_rra_entries: {q_pm_rra_entries}")

                #             totals = _summarize_totals(
                #                 employee, identifier, q_pm_rra_entries,
                #                 pensioner=pensioner, pensioner_type=pensioner_type,
                #                 rra_employee=rra_employee)

            log.debug(">>> FINALIZANDO DIRF %s" % employee)

    def summarize_entries(self, clear=False, task=None):
        """Sumariza todos os ``FolhaEvento`` dos contracheques pagas no ano indicado em ``calendar_year``.

        Args:
            clear (bool, optional): True para apagar todo sumario gerado anteiormente
            task (None, optional): task for notification

        Returns:
            TYPE: Description
        """
        task_ = NullTaskSession() if not task else task
        persons = []
        q_employeers = Servidor.objects.filter(
            (
                models.Q(
                    entries__contracheque__folha__dt_pagamento__year=self.calendar_year
                )
                | models.Q(
                    entries__reference_month=13,
                    entries__reference_year=self.calendar_year,
                )
            )
        ).distinct()

        debug_persons_ids = DEBUG_PERSONS + [
            e.pessoa_fisica.id
            for e in Servidor.objects.filter(matricula__in=DEBUG_EMPLOYES)
        ]

        if debug_persons_ids:
            q_employeers = q_employeers.filter(pessoa_fisica__in=debug_persons_ids)

        if clear:
            task_.send_message("Apagando sumários de %04d!" % self.calendar_year)
            q_summaries = DirfSummary.objects.filter(
                calendar_year=self.calendar_year, dirf_created=True
            )
            if debug_persons_ids:
                q_summaries = q_summaries.filter(person__in=debug_persons_ids)
            q_summaries.delete()

        task_["total"] = q_employeers.count()
        task_["pct"] = count = 0

        task_.send_message("Processando contracheques dos servidores!")
        for employee in q_employeers:
            count += 1
            task_["pct"] = count
            if employee.pessoa_fisica not in persons:
                persons.append(employee.pessoa_fisica)
                log.debug("DIRF SUMMARIZE PERSON: %s" % employee)
                self.summarize_employee(employee)

        result = DirfSummary.objects.filter(
            calendar_year=self.calendar_year, dirf_created=True
        ).aggregate(date=models.Max("modified_at"))
        self.last_processed_summary = result["date"]
        self.save()

    def generate_file(self, filename="", receipt_number="", task=None):
        """Cria o aquivo da DIRF e armazena no GED para ser utilizado.

        Args:
            filename (str, optional): nome do arquivo da DIRF a ser gerado
            receipt_number (str, optional): Recibo que está sendo retificado
            task (None, optional): Description

        Returns:
            TYPE: Description

        """
        from rh.gfp.generators.dirf.protocol import File

        filename = (
            "dirf_%s_%s.txt" % (self.calendar_year, self.reference_year)
            if not filename
            else filename
        )
        task_ = NullTaskSession() if not task else task
        user = get_current_user()

        task_.info(msg="Gerando arquivo da DIRF e declarações. AGUARDE ...", type_of=1)

        file_dirf = File(self, receipt_number=receipt_number, persons=DEBUG_PERSONS)

        file_path = os.path.join(settings.UPLOAD_STORE_DIR, filename)

        if not os.path.exists(settings.UPLOAD_STORE_DIR):
            os.makedirs(settings.UPLOAD_STORE_DIR)

        with codecs.open(file_path, "w", "utf-8") as fd:
            fd.write(str(file_dirf))

        gedfile = FileGED.from_filepath(file_path, user, "application/txt", 3)

        task_.add_file(gedfile, msg="Arquivo da DIRF gerado: %s" % gedfile.filename)
        self.last_dirf_file = gedfile
        self.save()

        return gedfile

    def get_if_employee_has_molestia_in_month(self, employee, month):
        employee_has_molestia = False
        if employee.molestia:
            month_start = datetime(
                self.calendar_year, month if month < 13 else 12, 1
            ).date()
            dt_laudo = employee.molestia.data_laudo if employee.molestia else False
            dt_laudo = datetime(
                employee.molestia.data_laudo.year, employee.molestia.data_laudo.month, 1
            ).date()
            employee_has_molestia = month_start >= dt_laudo

        return employee_has_molestia

    def _get_value(self, employee, month, q_entries, token):
        value = q_entries.aggregate(total=models.Sum("value")).get("total") or 0

        return value if (token and token.tipo == 1) or value == 0 else -value

    def _get_value_bpfrra_rtrt(self, employee, month, q_entries, token):
        disease = Molestia.objects.filter(servidor=employee).first()
        dr = NewDateRange.from_month(self.calendar_year, month if month < 13 else 12)

        if disease and disease.data_laudo < dr.last:
            return 0.00

        return self._get_value(employee, month, q_entries, token)

    def _get_value_bpfrra_rimog(self, employee, month, q_entries, token):
        disease = Molestia.objects.filter(servidor=employee).first()
        dr = NewDateRange.from_month(self.calendar_year, month if month < 13 else 12)

        if not disease or disease.data_laudo > dr.last:
            return 0.00

        return self._get_value(employee, month, q_entries, token)

    def _get_value_bpfdec_rtdp(self, employee, month, q_entries, token):
        dr = NewDateRange.from_month(self.calendar_year, month if month < 13 else 12)
        irrf = (
            IRRF.objects.exclude(data_vigencia__gt=dr.last)
            .order_by("data_vigencia")
            .last()
        )
        value_dependent = float(irrf.valor_dependente) if irrf else 0.0

        value = q_entries.aggregate(total=models.Sum("qnt")).get("total") or 0

        return float(value) * value_dependent

    def _get_value_bpfrra_qtmeses(self, employee, month, q_entries, token):
        # Comentando lógica de cálculo,  provisóriamente retornará 0 (zero) e será preenchido manualmente

        # rra = q_entries.first().rra_employee
        # q_value = q_entries.aggregate(max_prazo=models.Max('prazo'), max_instalments_paid=models.Max('installments_paid'))

        # return float(rra.months / q_value['max_prazo'] * q_value['max_instalments_paid'])
        return 0

    def _get_value_bpfdec_rtrt(self, employee, month, q_entries, token):
        employee_has_molestia = self.get_if_employee_has_molestia_in_month(
            employee, month
        )

        return (
            0
            if employee_has_molestia
            else self._get_value(employee, month, q_entries, token)
        )

    def _get_value_bpfdec_rimog(self, employee, month, q_entries, token):
        employee_has_molestia = self.get_if_employee_has_molestia_in_month(
            employee, month
        )

        return (
            self._get_value(employee, month, q_entries, token)
            if employee_has_molestia
            else 0
        )

    def _get_value_bpfdec_rip65(self, employee, month, q_entries, token):
        value = 0

        gte_65_years_old = (
            datetime.today().year - employee.pessoa_fisica.data_nascimento.year
        ) >= 65
        if gte_65_years_old and employee.type_by_possession in [
            "SAP",
            "MAP",
            "MAP2",
            "APO",
            "BFP",
        ]:
            dr = NewDateRange.from_month(
                self.calendar_year, month if month < 13 else 12
            )
            irrf = (
                IRRF.objects.exclude(data_vigencia__gt=dr.first)
                .order_by("data_vigencia")
                .last()
            )
            value = float(
                irrf.faixas.order_by("limite_inferior").first().limite_superior
            )

        return value

    def _get_values_default(self, employee, identifier, q_entries, tokens=[]):
        if not tokens:
            tokens = self.tokens.filter(identifier=identifier["id"])

        fevs = q_entries.exclude(reference_month=13)
        fevs13 = q_entries.filter(reference_month=13, reference_year=self.calendar_year)
        totals = {}
        has_value = False

        method_name = f"_get_value_{identifier['label'].lower().replace('-', '_')}"
        _get_value = getattr(self, method_name, self._get_value)

        for token in tokens:
            if identifier["label"] == "BPFRRA-QTMESES":
                ident_id = next(
                    ident
                    for ident in token.dialect.get_list_identifiers()
                    if ident["label"] == "BPFRRA-RTRT"
                )["id"]
                tks = [
                    ev.pk
                    for ev in token.dialect.tokens.filter(identifier=ident_id)
                    .first()
                    .eventos.all()
                ]
            else:
                tks = [ev.pk for ev in token.eventos.all()]

            fevs_token = fevs.filter(evento__in=tks)
            fevs13_token = fevs13.filter(evento__in=tks)

            if fevs_token.exists() or fevs13_token.exists():
                total_value_month = 0
                for month in range(1, 14):
                    fevs_token_month = fevs_token.filter(
                        contracheque__folha__dt_pagamento__month=month
                    )
                    info = token.extra_info

                    q_entries = fevs_token_month if month < 13 else fevs13_token
                    if not q_entries:
                        continue  # Continuar apenas se existir lançamentos

                    total_value_month = _get_value(employee, month, q_entries, token)
                    if (
                        total_value_month != 0
                        or identifier["label"] == "BPFRRA-QTMESES"
                    ):
                        if info not in totals:
                            totals[info] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        has_value = True
                        totals[info][month - 1] += total_value_month

        return totals if has_value else {}

    def print_values(self, person, identifier="BPFDEC-RTRT", rra_employee=None):
        values = self._get_values_default(person, identifier, rra_employee=rra_employee)
        for x in range(1, 14):
            print("%02d/%04d - %s" % (x, self.calendar_year, values[x - 1]))


class TokenManager(models.Manager):

    def get_by_natural_key(self, slug, dialect):
        return self.get(slug=slug, dialect=dialect)


class Token(models.Model):
    dialect = models.ForeignKey(
        Dialect, related_name="tokens", on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=60)
    slug = models.CharField(max_length=60, blank=True)
    eventos = models.ManyToManyField(Evento, related_name="as_token")
    id_receita = models.CharField(
        max_length=30,
        verbose_name="Identificador do Registro",
        null=True,
        blank=True,
        default="",
    )
    tipo = models.IntegerField(
        choices=Choice.get_choices_for("dirf", "TYPE_DIRF_TOKENS"),
        null=True,
        blank=True,
    )
    identifier = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("dirf", "IDENTIFIERS_DIRF"),
        blank=True,
        default=1,
    )
    extra_info = models.CharField(max_length=30, verbose_name="Info", default="")

    objects = TokenManager()

    class Meta:
        ordering = ["dialect", "slug"]

    def natural_key(self):
        return (self.slug, self.dialect)

    def save(self, *args, **kargs):
        self.slug = slugify(self.nome)
        models.Model.save(self, *args, **kargs)

    def __str__(self):
        return self.slug


class NaturezaRendimento(models.Model):
    codigo = models.CharField(max_length=4, unique=True)
    titulo = models.CharField(max_length=300, null=True)
    descricao = models.TextField()

    @classmethod
    def get_from_codigo(cls, codigo):
        return cls.objects.get(codigo=codigo)

    def __str__(self):
        return "%s: %s" % (self.codigo, self.titulo)


class Declaracao(models.Model):
    nome = models.CharField(max_length=10, null=True)
    ano_base = models.IntegerField(verbose_name="Ano base")
    retificadora = models.IntegerField(blank=True, default=1)
    published = models.BooleanField(default=False, verbose_name="Publicado?")
    rectified_receipt = models.CharField(
        default="", verbose_name="Recibo retificado", max_length=12, blank=True
    )

    class Meta:
        ordering = ("-ano_base", "-retificadora")

    def __str__(self):
        return self.nome

    def save(self, *args, **kargs):
        if self.retificadora is None:
            self.retificadora = (
                Declaracao.objects.filter(ano_base=self.ano_base).count() + 1
            )

        self.nome = "%s.%s" % (self.ano_base, self.retificadora)
        models.Model.save(self, *args, **kargs)


class Demonstrativo(AuditTimestampModel):

    DEFAULT_USER = "athenas"

    AUDITABLE = {
        "fields": [
            "declaracao",
            "servidor",
            "pessoa_fisica",
            "natureza",
            "rra",
            "qnt_meses",
            "rendimento",
            "rendimento_molestia",
            "previdencia_oficial",
            "previdencia_privada",
            "pensao_alimenticia",
            "imposto_retido",
            "parcela_isenta",
            "ajuda_custo",
            "pensao_aposentado",
            "lucro_dividendo",
            "servico_prestado",
            "idenizacao",
            "outros",
            "outros_descricao",
            "decimoterceiro",
            "decimoterceiro_imposto",
            "decimoterceiro_outro",
            "informacao_complementar",
        ],
    }

    declaracao = models.ForeignKey(
        Declaracao, related_name="demonstrativos", on_delete=models.CASCADE
    )
    servidor = models.ForeignKey(
        Servidor, related_name="dirfs", null=True, on_delete=models.CASCADE
    )
    pessoa_fisica = models.ForeignKey(
        PessoaFisica, related_name="dirfs_pessoa_fisica", on_delete=models.CASCADE
    )
    natureza = models.ForeignKey(
        NaturezaRendimento, related_name="demonstrativos", on_delete=models.PROTECT
    )
    tipo_folha = models.ForeignKey(
        "gfp.FolhaTipo",
        related_name="demonstrativos",
        null=True,
        on_delete=models.SET_NULL,
    )
    rra = models.ForeignKey(
        "gfp.RRA", related_name="demonstrativos", null=True, on_delete=models.PROTECT
    )
    qnt_meses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # QTMESES[1-13]
    rendimento = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RTRT[1-12]
    rendimento_molestia = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RIMOG[1-13]
    previdencia_oficial = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RTPO[1-12]
    previdencia_privada = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    pensao_alimenticia = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RTPA[1-12]
    imposto_retido = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RTIRF[1-12]
    parcela_isenta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ajuda_custo = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RIDAC[1-12]
    pensao_aposentado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lucro_dividendo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    servico_prestado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    idenizacao = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outros = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RIO[1-13]
    outros_descricao = models.CharField(max_length=120, null=True)  # RIO (DESC)
    # RTRT[13] - RTPO[13] - RTIRF[13] - RTDP[13]
    decimoterceiro = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    decimoterceiro_imposto = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # RTIRF[13]
    decimoterceiro_outro = models.CharField(max_length=60, default="")
    informacao_complementar = models.CharField(max_length=500, default="")  # INF
    responsavel = models.ForeignKey(
        Servidor, related_name="como_responsavel", on_delete=models.PROTECT
    )
    data_geracao = models.DateTimeField(auto_now_add=True)
    version = models.PositiveSmallIntegerField(default=1, verbose_name="Versão")

    class Meta:
        ordering = ("declaracao", "-version")

    def save(self, *args, **kargs):
        if not self.pessoa_fisica and self.servidor:
            self.pessoa_fisica = self.servidor.pessoa_fisica
        if not self.responsavel:
            cfg = Configuration.get_or_create("gfp")
            self.responsavel_id = int(cfg.get("responsavel_gfp"))
        if self.declaracao.published and self.old_fields:
            log.debug(self.diff)
            for k in self.old_fields:
                f = self.diff.get(k, (None, None))
                log.debug(
                    ">> DIRF DEM OLDS %s: %s(%s)/%s(%s) %s %s"
                    % (
                        k,
                        f[0],
                        type(f[0]),
                        f[1],
                        type(f[1]),
                        f[0] == f[1],
                        self.pessoa_fisica,
                    )
                )
            self.version += 1
            self.data_geracao = datetime.now()

        if len(self.informacao_complementar or "") > 500:
            self.informacao_complementar = self.informacao_complementar[0:500]
        if len(self.outros_descricao or "") > 120:
            self.outros_descricao = self.outros_descricao[0:120]
        if len(self.decimoterceiro_outro or "") > 60:
            self.decimoterceiro_outro = self.decimoterceiro_outro[0:60]

        super(Demonstrativo, self).save(*args, **kargs)

    def clear(self):
        self.qnt_meses = 0
        self.rendimento = 0
        self.rendimento_molestia = 0
        self.previdencia_oficial = 0
        self.previdencia_privada = 0
        self.pensao_alimenticia = 0
        self.imposto_retido = 0
        self.parcela_isenta = 0
        self.ajuda_custo = 0
        self.pensao_aposentado = 0
        self.lucro_dividendo = 0
        self.servico_prestado = 0
        self.idenizacao = 0
        self.outros = 0
        self.decimoterceiro = 0
        self.decimoterceiro_imposto = 0
        self.outros_descricao = ""
        self.decimoterceiro_outro = ""
        self.informacao_complementar = ""

    def __str__(self):
        return f"{self.natureza.codigo} - {self.pessoa_fisica} v{self.version}"
