# -*- coding: utf-8 -*-

from django.db import models

from datetime import datetime

from contrib.decorator import to_search
from contrib.utils import getLogger
from rh.gfp.models import ContraCheque, ContraChequePensionista
from standard.models import AuditTimestampModel, Choice

log = getLogger(__name__)


class PensaoQueryset(models.QuerySet):

    def actives_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                models.Q(data_inicio__gt=range_.last)
                | (~models.Q(data_fim=None) & models.Q(data_fim__lt=range_.first))
            )
        else:
            return self.exclude(
                models.Q(data_inicio__gt=data)
                | (~models.Q(data_fim=None) & models.Q(data_fim__lt=data))
            )


class Pensao(AuditTimestampModel):

    class Meta:
        ordering = [
            "servidor__pessoa_fisica__nome",
            "pensionista__nome",
            "-data_inicio",
        ]

    objects = PensaoQueryset.as_manager()

    servidor = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="pensao_pagador",
        on_delete=models.PROTECT,
    )  # Parametro "on_delete" adicionado. (Django 2)
    pensionista = models.ForeignKey(
        "rh.PessoaFisica",
        related_name="pensao_pensionista",
        verbose_name="Pensionista",
        on_delete=models.PROTECT,
    )  # Parametro "on_delete" adicionado. (Django 2)
    representante_legal = models.ForeignKey(
        "rh.PessoaFisica",
        null=True,
        blank=True,
        related_name="pensao_representante_legal",
        on_delete=models.SET_NULL,
    )  # Parametro "on_delete" adicionado. (Django 2)
    publicacao = models.ForeignKey(
        "rh.Publicacao",
        null=True,
        blank=True,
        related_name="pensao_publicacao",
        verbose_name="Publicação",
        on_delete=models.SET_NULL,
    )  # Parametro "on_delete" adicionado. (Django 2)
    data_inicio = models.DateField(verbose_name="Data do início", null=True, blank=True)
    data_fim = models.DateField(verbose_name="Data do fim", null=True, blank=True)
    tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("pensao", "TYPE_OF_CALC"),
        verbose_name="Tipo do Valor",
        default=1,
    )
    valor = models.DecimalField(
        max_digits=16, decimal_places=6, verbose_name="Valor", blank=True, default=0
    )
    type_of_pension = models.SmallIntegerField(
        choices=Choice.get_choices_for("pensao", "TYPE_OF_PENSION"),
        verbose_name="Tipo",
        default=1,
    )
    events = models.ManyToManyField(
        "gfp.Evento", related_name="pension_events", blank=True, verbose_name="Eventos"
    )
    event_employee = models.ForeignKey(
        "gfp.Evento",
        related_name="pensions_as_event_employee",
        verbose_name="Evento no servidor",
        on_delete=models.PROTECT,
    )
    event_employee_13 = models.ForeignKey(
        "gfp.Evento",
        related_name="pensions_as_event_employee_13",
        null=True,
        blank=True,
        verbose_name="Evento no servidor",
        on_delete=models.SET_NULL,
    )
    event_pensioner = models.ForeignKey(
        "gfp.Evento",
        related_name="pensions_as_event_pensioner",
        verbose_name="Evento no pensionista",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return "%s" % self.pensionista

    def save(self, *args, **kargs):
        if not self.representante_legal:
            self.representante_legal = self.pensionista
        super(Pensao, self).save(*args, **kargs)


@to_search(
    [
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "pensionista__nome", "type": "text"},
        {"name": "publicacao__numero", "type": "text"},
    ]
)
class PensaoAlimenticia(Pensao):
    evento = models.ManyToManyField(
        "gfp.Evento",
        through="PensaoAlimenticiaEvento",
        related_name="pensaoalimenticia_eventos",
        blank=True,
    )
    evento_pensao = models.ForeignKey(
        "gfp.Evento",
        related_name="eventos_origem_pensao",
        verbose_name="Evento",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s-%s" % (self.servidor, self.pensionista)

    def save(self, *args, **kargs):
        log.debug(">>>>>> SAVING PensaoAlimenticia")
        super(PensaoAlimenticia, self).save()

        for pae in self.eventos.all():
            log.debug("SAVING %s" % pae.__class__.__name__)
            pae.save()


class PensaoEvento(models.Model):
    evento = models.ForeignKey(
        "gfp.Evento",
        related_name="pensaoalimenticiaevento_evento",
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    tipo = models.SmallIntegerField(
        choices=((1, "VALOR FIXO"), (2, "PERCENTUAL"), (3, "SALÁRIO MÍNIMO")),
        verbose_name="Tipo do Valor",
        blank=True,
        default=1,
    )
    valor = models.DecimalField(
        max_digits=16, decimal_places=6, verbose_name="Valor", blank=True, default=0
    )
    tipo_folhas = models.ManyToManyField("gfp.FolhaTipo", related_name="eventos_pensao")
    calculo_oculto = models.BooleanField(default=False, verbose_name="Calculo oculto")
    evento_principal = models.BooleanField(verbose_name="Principal", default=False)

    def apply_to_value(self, value):
        value = float(value or 0.00)

        if self.tipo == 1 and float(self.valor or 0.00) > value:
            raise Exception("O valor configurado é maior que o valor recebido.")

        return (
            float(self.valor)
            if self.tipo == 1
            else value * (float(self.valor or 0.00) / 100.0)
        )

    def save(self, *args, **kargs):
        if self.tipo == 2 and float(self.valor) > 100.00:
            raise Exception("O tipo de valor percetual não pode ser maior que 100%")

        models.Model.save(self, *args, **kargs)


class PensaoAlimenticiaEvento(PensaoEvento):
    pensao_alimenticia = models.ForeignKey(
        "PensaoAlimenticia", related_name="eventos", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s" % self.evento

    def save(self, *args, **kargs):
        self.valor = self.pensao_alimenticia.valor
        self.tipo = self.pensao_alimenticia.tipo
        super(PensaoAlimenticiaEvento, self).save(*args, **kargs)


@to_search(
    [
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "pensionista__nome", "type": "text"},
        {"name": "publicacao__numero", "type": "text"},
    ]
)
class PensaoMorte(Pensao):
    evento = models.ManyToManyField(
        "gfp.Evento",
        through="PensaoMorteEvento",
        related_name="pensaomorte_eventos",
        blank=True,
    )

    def __str__(self):
        return "%s" % self.pensionista


class PensaoMorteEvento(PensaoEvento):
    pensao_morte = models.ForeignKey(
        "PensaoMorte", related_name="eventos", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def save(self, *args, **kargs):
        self.valor = self.pensao_morte.valor
        self.tipo = self.pensao_morte.tipo
        super(PensaoMorteEvento, self).save(*args, **kargs)

    def __str__(self):
        return "%s" % self.evento


class PensaoFolhaEvento(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    # contracheque_servidor = models.ForeignKey(
    #   'ContraCheque', related_name='lancamentos_pensionistas', null=True, blank=True, on_delete=models.CASCADE)
    contracheque = models.ForeignKey(
        "gfp.ContraChequePensionista",
        related_name="lancamentos_pensionitas",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    folha_evento = models.ForeignKey(
        "gfp.FolhaEvento",
        related_name="origem_pensao",
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    pensao = models.ForeignKey(
        Pensao, related_name="lancamentos", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    folha = models.ForeignKey(
        "gfp.Folha", related_name="pensoes", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    evento = models.ForeignKey(
        "gfp.Evento", related_name="em_pensoes", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    valor = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_base = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    pct = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    # Parametro "on_delete" adicionado. (Django 2)
    # evento_pagador = models.ForeignKey(
    #   'gfp.FolhaEvento', related_name='eventos_pensoes', null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("pensao", "folha", "evento")

    def save(self, *args, **kargs):
        """ """
        log.debug("SAVING PFE...")
        if self.valor != 0:
            if self.folha_evento is None and (
                self.folha is None or self.evento is None
            ):
                raise Exception(
                    "O preenchimento do evento da pensão foi feito de forma incorreta."
                )
            elif self.folha_evento is not None:
                self.folha = self.folha_evento.folha
                self.evento = self.folha_evento.evento
                self.valor_base = self.folha_evento.valor
            cc_servidor, created_s = ContraCheque.objects.get_or_create(
                folha=self.folha, servidor=self.pensao.servidor
            )
            cc_pensionista, created = ContraChequePensionista.objects.get_or_create(
                pensionista=self.pensao.pensionista, contracheque_servidor=cc_servidor
            )
            log.debug(
                "%s(%s):%s(%s):%s"
                % (cc_servidor, created_s, cc_pensionista, created, self.evento)
            )
            self.contracheque = cc_pensionista

            super(PensaoFolhaEvento, self).save(*args, **kargs)
