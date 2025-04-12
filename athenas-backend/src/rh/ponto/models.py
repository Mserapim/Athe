# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.db import models
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import DateUtils, getLogger
from contrib.middleware import set_current_user

from rh.const import TURNO
from rh.gfp.gcpp_utils import remove_gcpp_gcf

from rh.models import (
    AnotacaoFalta,
    Localidade,
    Publicacao,
    RHObject,
    CargaHoraria,
    Servidor,
)
from rh.pvf.models import SendingTimeSheet, PointJustification, JustificationItem
from rh.ponto.envio_notificacao_falta import enviar_notificacao_falta
from standard.models import Choice, AuditTimestampModel
from ged.models import Arquivo as File
from rh.gfp.models import Evento, ContraCheque
from common.usefulday.models import NonWorkingDay

# from contrib.utils import getLogger

log = getLogger(__name__)

DIAS_SEMANA = (
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
)


# @decorator.to_search([
#     {'name': 'titulo', 'type': 'text'},
#     {'name': 'data', 'type': 'date'},
#     {'name': 'ano', 'type': 'number'},
#     {'name': 'parte_dia', 'type': 'choices'},
#     {'name': 'tipo', 'type': 'choices'},
#     {'name': 'localidades__nome', 'type': 'text'},
# ])

# class Feriado(models.Model):
#     titulo = models.CharField(max_length=40)
#     data = models.DateField()
#     ano = models.IntegerField(blank=True)
#     parte_dia = models.IntegerField(choices=TURNO)
#     tipo = models.IntegerField(
#         choices=(
#             (1, 'NACIONAL'),
#             (2, 'ESTADUAL'),
#             (3, 'MUNICIPAL'),
#             (4, 'PONTO FACULTATIVO'),
#             (5, 'LUTO'),
#         )
#     )
#     localidades = models.ManyToManyField(Localidade, related_name='feriados')

#     class Meta:
#         unique_together = ('data', 'parte_dia')

#     def __str__(self):
#         return '%s: %s - %s' % (self.titulo, DateUtils.date_to_str(self.data), self.get_tipo_display())

#     @classmethod
#     def feriados_nacionais(cls, date_range=None, excluir_weekend=True, tipo=1, parte_dia=4):
#         """
#             Este método retorna a quantidade de feriados nacionais de dia inteiro dentro de um NewDateRange.
#             O fim de semana pode ser excluído informando excluir_weekend=False.
#             Valor padrão para tipo: 1 - (NACIONAL).
#             Valor padrão para parte_dia: 4 - (dia inteiro).
#         """
#         if date_range is None:
#             raise Exception('NewDateRange não informado.')
#         feriados = []
#         feriados_encontrados = Feriado.objects.filter(
#             tipo=tipo,
#             parte_dia=parte_dia,
#             data__gte=datetime(date_range.start_date.year, date_range.start_date.month, date_range.start_date.day),
#             data__lte=datetime(date_range.end_date.year, date_range.end_date.month, date_range.end_date.day)
#         )
#         for f in feriados_encontrados:
#             if not (excluir_weekend and NewDateRange.day_weekend(f.data)):
#                 feriados.append([f.pk, f.data])
#         return feriados

#     def save(self, **kargs):
#         self.ano = self.data.year
#         models.Model.save(self, **kargs)


class Falta(RHObject):
    data = models.DateField(null=False)
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    data_processado = models.DateField(
        null=True, blank=True, verbose_name="Data Processado"
    )
    justificada = models.DecimalField(default=0, max_digits=11, decimal_places=2)
    injustificada = models.DecimalField(default=0, max_digits=11, decimal_places=2)
    horas_positivas = models.DecimalField(default=0, max_digits=11, decimal_places=2)
    horas_negativas = models.DecimalField(default=0, max_digits=11, decimal_places=2)
    excedente = models.DecimalField(default=0, max_digits=11, decimal_places=2)
    observacao = models.TextField(blank=True, null=True)
    carga_horaria = models.ForeignKey(
        "rh.CargaHoraria",
        on_delete=models.SET_NULL,
        related_name="faltas",
        null=True,
        blank=True,
    )
    payroll = models.BooleanField(
        verbose_name="Folha", default=False, blank=True, null=True
    )
    vertical_progression = models.BooleanField(
        verbose_name="Progressão Vertical", default=False, blank=True, null=True
    )
    premium_license = models.BooleanField(
        verbose_name="Licença Prêmio", default=False, blank=True, null=True
    )
    request_sts = models.ForeignKey(
        SendingTimeSheet,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="falta",
    )
    origem = models.SmallIntegerField(
        choices=Choice.get_choices_for("ponto", "ORIGIN_CHOICES"), blank=True, null=True
    )
    situacao = models.SmallIntegerField(
        default=1,
        choices=Choice.get_choices_for("ponto", "SITUATION_CHOICES"),
        blank=True,
        null=True,
    )
    anexo = models.ForeignKey(
        File, null=True, blank=True, on_delete=models.PROTECT, related_name="falta"
    )
    justificado = models.BooleanField(
        verbose_name="Está Justificada", default=False, blank=True, null=True
    )
    saldo = models.IntegerField(verbose_name="Saldo", blank=True, null=True)
    competencia_desconto = models.CharField(
        verbose_name="Competência de Desconto", max_length=7, null=True, blank=True
    )
    dias_uteis = models.IntegerField(verbose_name="Dias úteis", blank=True, null=True)

    class Meta:
        ordering = ("-data",)

    def __str__(self):
        return "Falta: %s - Data: %s - %s" % (
            self.servidor,
            DateUtils.date_to_str(self.data),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "---",
        )

    def anotacao_falta(self):
        tipo = Publicacao.get_tipo(99)
        if self.anotacao_geral is None:
            anotacao_geral = AnotacaoFalta.manage_instance(
                servidor=self.servidor,
                tipo_documento=tipo,
                data_inicio=self.data,
                data_fim=self.data_fim,
                texto=self.get_texto(),
                resumo="FALTA",
            )
            AnotacaoFalta.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
            self.anotacao_geral = anotacao_geral
        else:
            anotacao_geral = AnotacaoFalta.objects.get(pk=self.anotacao_geral.pk)
            anotacao_geral.servidor = self.servidor
            anotacao_geral.tipo_documento = tipo
            anotacao_geral.texto = self.get_texto()
            anotacao_geral.data_inicio = self.data
            anotacao_geral.data_fim = self.data_fim
            anotacao_geral.save()
            AnotacaoFalta.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
        return True

    def get_state_icons(self):
        status = []
        if (
            int(self.justificada) == 0
            and int(self.injustificada) == 0
            and int(self.excedente) == 0
            and int(self.horas_positivas)
            and int(self.horas_negativas)
        ):
            status.append(
                {
                    "iconCls": "icon-gep-warning",
                    "title": "Todos os valores estão zerados para este lançamento. Exclua o registro ou verifique possíveis inconsistências.",
                }
            )

        return status

    def get_hours_str(self, args=[]):
        import datetime as dtime

        total = (
            float(self.injustificada) - float(self.excedente)
            if float(self.excedente) > 0
            else float(self.injustificada)
        )
        horas = dtime.timedelta(minutes=float(total)) if total > 0 else "0:00:00"
        horas = str(horas)
        hora, minuto, segundo = horas.split(":")
        return "%sh:%sm" % (hora, minuto)

    def get_hours_float(self, args=[]):
        import datetime as dtime

        horas = (
            dtime.timedelta(minutes=float(self.injustificada))
            if int(self.injustificada) > 0
            else "0:00:00"
        )
        horas = str(horas)
        hora, minuto, segundo = horas.split(":")
        hora = float(hora)
        return hora

    def get_text_by_fault_type(self):
        injustificada = ""
        justificada = ""
        if self.justificado:
            justificada = self.get_texto_justificada()
        else:
            injustificada = self.get_texto_injustificada()

        return injustificada, justificada

    def get_texto(self):
        texto = ""
        injustificada, justificada = self.get_text_by_fault_type()
        impacto = (
            " sem impacto Financeiro"
            if self.payroll == False
            else " com impacto Financeiro"
        )

        try:
            servidor = self.servidor.texto_servidor()
            nome = self.servidor.pessoa_fisica.nome
            dia = DateUtils.date_to_str(self.data)
            dia_semana = DIAS_SEMANA[self.data.weekday()]
            tipo_anotacao = f"faltou {injustificada} ao serviço"
            data_fim = (
                DateUtils.date_to_str(self.data_fim)
                if self.data_fim and self.data_fim != self.data
                else ""
            )
            dia_semana_data_fim = (
                DIAS_SEMANA[self.data_fim.weekday()]
                if self.data_fim and self.data_fim != self.data
                else ""
            )
            msg_data_fim = f"a {data_fim} ({dia_semana_data_fim})" if data_fim else ""
            texto = f"""{servidor} {nome} {tipo_anotacao} no(s) dia(s) {dia} ({dia_semana}) {msg_data_fim} {justificada}{impacto}."""
        except Exception as err:
            log.exception(err)
        return texto

    def get_texto_justificada(self):
        justificativa = JustificationItem.objects.get(
            value=self.point_justification.last().reason_type
        ).name
        return f", sob a justificativa {justificativa}"

    def get_texto_injustificada(self):
        return "INJUSTIFICADAMENTE"

    def delete(self, *args, **kargs):
        if self.anotacao_geral is not None:
            self.anotacao_geral.delete()
        super(Falta, self).delete(*args, **kargs)

    @property
    def get_anotacao_falta(self):
        return self.get_texto()

    @property
    def days(self):
        return float(self.justificada) / (self.carga_horaria.day * 60.0), float(
            self.injustificada
        ) / (self.carga_horaria.day * 60.0)

    @property
    def get_days(self):
        if self.data_fim:
            return NewDateRange(self.data, self.data_fim).days
        else:
            return 0

    @classmethod
    def fill_workload(cls, employee=[]):
        faults = Falta.objects.filter(carga_horaria=None)
        if employee:
            faults = faults.filter(servidor__pk__in=employee)
        log.info("Preenchendo carga horária de faltas %s." % faults.count())
        for fault in faults:
            fault.save()

    @classmethod
    def update_missing(cls, workload):
        log.info("Atualizando faltas de acordo com a carga horária %s" % workload)
        ft = Falta.objects.filter(servidor=workload.servidor).exclude(
            carga_horaria=workload
        )
        if not workload.data_fim:
            ft = ft.filter(data__gte=workload.data_inicio)
        else:
            ft = ft.filter(
                Q(data__gte=workload.data_inicio) & Q(data__lte=workload.data_fim)
            )
        for f in ft:
            f.carga_horaria = workload
            try:
                f.save()
                log.info("Atualizada %s com a carga horária %s" % (f, workload))
            except Exception as err:
                log.info("ERRO - atualizando %s" % f)
                log.exception(err)

    def save(self, *args, **kargs):
        self.validate()
        if not self.pk:
            self.situacao = 1  # Aguardando Processar
        if not self.origem and not self.pk:
            self.origem = 2  # Manual
        self.set_justificado()
        self.calcular_dias_uteis()

        super(Falta, self).save(*args, **kargs)

    def calcular_dias_uteis(self):
        query = NonWorkingDay.objects.filter(
            Q(start_date__range=(self.data, self.data_fim))
            | Q(end_date__range=(self.data, self.data_fim))
        ).exclude(
            abrangency=3
        )  # Municipal
        range_falta = NewDateRange(self.data, self.data_fim)
        dias_nao_uteis = 0

        if query.exists():
            for periodo in query:
                dias_fim_de_semana = sum(
                    1
                    for day in self.iterdates(
                        periodo.start_date.date(),
                        (
                            periodo.end_date.date()
                            if periodo.end_date
                            else periodo.start_date.date()
                        ),
                    )
                    if day.weekday() in (5, 6)
                )
                range_periodo = NewDateRange(
                    periodo.start_date.date(),
                    (
                        periodo.end_date.date()
                        if periodo.end_date
                        else periodo.start_date.date()
                    ),
                )
                qtd_dias = (
                    range_falta.intersect(range_periodo).days - dias_fim_de_semana
                )
                dias_nao_uteis += qtd_dias if qtd_dias > 0 else 0

        dias_de_semana = sum(
            1
            for day in self.iterdates(self.data, self.data_fim)
            if day.weekday() not in (5, 6)
        )

        self.dias_uteis = dias_de_semana - dias_nao_uteis

    def iterdates(self, date1, date2):
        one_day = timedelta(days=1)
        current = date1
        while current <= date2:
            yield current
            current += one_day

    def validate(self):
        # self.validate_workload()
        self.validate_data_inicio()
        self.validate_data_fim()
        self.validate_datas()

    def validate_workload(self):
        self.carga_horaria = self.current_workload
        if not self.carga_horaria:
            log.info(
                "%s não possui carga horária vigente no período %s."
                % (self, DateUtils.date_to_str(self.data))
            )

    def set_justificado(self):
        if self.pk:
            self.justificado = True if self.point_justification.exists() else False
        else:
            self.justificado = False

    def validate_data_inicio(self):
        if not self.data:
            raise Exception("Favor preencher o campo Data Início")

    def validate_data_fim(self):
        if not self.data_fim:
            raise Exception("Favor preencher o campo Total Dias")

    def validate_datas(self):
        query = Falta.objects.filter(
            Q(servidor=self.servidor)
            & Q(
                Q(data__isnull=False, data_fim__isnull=False)
                & Q(
                    Q(data__lte=self.data, data_fim__gte=self.data)
                    | Q(data__gte=self.data, data__lte=self.data_fim)
                )
            )
            | Q(
                Q(data__isnull=False, data_fim__isnull=True)
                & Q(Q(data__lte=self.data, data_fim__gte=self.data))
            )
        ).exclude(situacao=3)

        if (query.count() == 1 and query.first().pk == self.pk) or query.count() == 0:
            pass
        else:
            raise Exception(
                "Já existe uma Falta cadastrada para a data/período informado!"
            )

    def workloads(self, start_date=None, end_date=None):
        dt_current = self.data
        if start_date is None:
            start_date = dt_current
        if end_date is None:
            end_date = start_date

        ch = (
            CargaHoraria.objects.filter(servidor=self.servidor)
            .exclude(
                Q(data_inicio__gt=end_date)
                | (~Q(data_fim=None) & Q(data_fim__lt=start_date))
            )
            .order_by("data_inicio")
        )
        return ch

    @property
    def current_workload(self):
        return self.workloads().last()

    def validar_falta_unica_ativa(self):
        q_falta = Falta.objects.filter(
            Q(servidor=self.servidor)
            & Q(
                Q(data__lte=self.data, data_fim__gte=self.data)
                | Q(data__gte=self.data, data__lte=self.data_fim)
            )
        ).exclude(situacao=3)

        if self.pk:
            q_falta = q_falta.exclude(pk=self.pk)

        if q_falta.exists():
            raise Exception("Não é possivel criar duas faltas no mesmo dia.")

    def validate_unique(self, exclude=None):
        self.validar_falta_unica_ativa()


class RemocaoFalta(RHObject):
    falta = models.ForeignKey(
        Falta,
        related_name="remocao_falta",
        verbose_name="Falta",
        on_delete=models.CASCADE,
    )
    data_remocao = models.DateField(blank=True, null=True, verbose_name="Data Remoção")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    anexo = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="remocao_falta",
    )

    class Meta:
        ordering = ("-data_remocao",)

    def __str__(self):
        return f"Remoção da Falta: {self.servidor} - Data: {DateUtils.date_to_str(self.falta.data)} - {DateUtils.date_to_str(self.falta.data_fim if self.falta.data_fim else self.falta.data)}"

    def save(self, *args, **kargs):
        self.validate()

        self.data_remocao = datetime.now().date()

        if self.falta.situacao == 2:
            self.inativa_anotacao()
            enviar_notificacao_falta(self.falta, tipo_notificacao="REMOCAO")

        query = self.falta.point_justification
        if (
            query.exists() and query.filter(cancelado=False).first().origem != 1
        ):  # Quando origem não for Vida Funcional
            query.update(cancelado=True)
        self.falta.situacao = 3  # Removido
        self.falta.save()
        remove_gcpp_gcf(self.falta)

        super(RemocaoFalta, self).save(*args, **kargs)

    def validate(self):
        self.validate_observacao()
        self.valida_falta_paga()

    def validate_observacao(self):
        if not self.observacao:
            raise Exception("Favor preencher o campo Observação!")

    def valida_falta_paga(self):
        if self.falta.pag_pessoal_faltas.filter(status="pago").exists():
            raise Exception(
                "Não é permitido remover Faltas que foram implantadas em Folha!"
            )

    def inativa_anotacao(self):
        anotacao = AnotacaoFalta.objects.filter(
            servidor=self.falta.servidor,
            data_inicio=self.falta.data,
            data_fim=self.falta.data_fim,
            data_documento=self.falta.data_processado,
        ).first()
        anotacao.ativa = False
        anotacao.save()
