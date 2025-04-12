# -*- coding: utf-8 -*-
import datetime
import hashlib
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db import models, transaction


from contrib.daterange import NewDateRange
from contrib.utils import DateUtils, getLogger
from engine.models import ControllerPermission, Group
from engine.notification.models import Notification
from rh.afastamento.models import (
    AfastamentoPrisao,
    AfastamentoSuspensao,
    BaseLicencaAfastamento,
    LicencaAfastamentoConjuge,
    LicencaInteresseParticular,
)
from rh.const import CANCELED, SCHEDULED
from rh.estagio.models import EstagioProbatorioServidor
from rh.models import AnotacaoCarreira, AnotacaoGeral, Publicacao, Servidor
from standard.models import AuditTimestampModel
from standard.questionario.models import (
    Alternativa,
    Elemento,
    Questao,
    Questionario,
    QuestionarioResposta,
    Resposta,
)

log = getLogger(__name__)

TYPE_PARTICIPANT = {
    "1": "PRESIDENTE",
    "2": "SECRETÁRIO",
    "3": "INTEGRANTE",
    "4": "SUPLENTE",
}

STATUS_PERIODICEVALUATION = {
    "1": "ATIVA",
    "2": "INATIVA ",
}

STATUS_EVALUATION = {
    "1": "NOVO",
    "2": "AVALIADO",
    "3": "MANIFESTADO",
    "4": "FINALIZADO",
}

STATUS_RESOURCE = {
    "1": "AGUARDANDO",
    "2": "CONCLUÍDO",
}

DECISION_RESOURCE = {
    "1": "PROVIDO RECURSO",
    "2": "NÃO PROVIDO RECURSO",
}

DECISION_COMISSION = {
    "1": "DAR PROVIDO RECURSO",
    "2": "NÃO DAR PROVIDO RECURSO",
}

STATUS_HOMOLOGATION = {
    "1": "AGUARDANDO HOMOLOGAÇÃO",
    "2": "HOMOLOGADO",
}


class Configuration(AuditTimestampModel):
    """Classe Configuração."""

    class Meta:
        """Class Meta."""

    previus_configuration = models.ForeignKey(
        "Configuration",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Configuração Anterior",
    )
    questionnaire_boss = models.ForeignKey(
        Questionario,
        related_name="boss_apd",
        verbose_name="Questionário Avalidor",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    questionnaire_subordinate = models.ForeignKey(
        Questionario,
        on_delete=models.CASCADE,
        related_name="subordinate_apd",
        null=True,
        blank=True,
        verbose_name="Questionário Avaliado",
    )
    publication = models.ForeignKey(
        "rh.Publicacao",
        related_name="publication_apd",
        verbose_name="Publicação",
        on_delete=models.CASCADE,
    )
    start_date = models.DateField(blank=True, verbose_name="Data Início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    porcentage_approval = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Porcentagem de Aprovação"
    )
    deadline_begin = models.SmallIntegerField(
        default=40, verbose_name="Dias para Início", blank=True
    )
    deadline_blocking = models.SmallIntegerField(
        default=15, verbose_name="Dias para bloqueio", blank=True
    )
    deadline_appeal = models.SmallIntegerField(
        default=0, verbose_name="Dias para Interpor Recurso"
    )
    deadline_judge_resource = models.SmallIntegerField(
        default=0, verbose_name="Dias para comissão julgar recurso"
    )
    deadline_reconsideration = models.SmallIntegerField(
        default=0, verbose_name="Dias para Solicitar a Reconsideração de Avaliação"
    )
    deadline_rectify_evaluation = models.SmallIntegerField(
        default=0, verbose_name="Dias para o chefe retificar Avaliação"
    )
    deadline_rectification_commission = models.SmallIntegerField(
        default=0, verbose_name="Dias para Comissão realizar retificação da nota"
    )
    deadline_science_resul_evaluation = models.SmallIntegerField(
        default=0,
        verbose_name="Dias para avaliado dar ciente do resultado da avaliação",
    )
    interval_periodic_evaluation = models.SmallIntegerField(
        default=0, verbose_name="Intervalo de Avaliações em Meses"
    )
    instructions = models.TextField(default="", verbose_name="Instruções da APD")

    def __str__(self):
        return "%s - %s à %s " % (
            self.publication,
            DateUtils.date_to_str(self.start_date),
            DateUtils.date_to_str(self.end_date) if self.end_date else "",
        )


class Commission(AuditTimestampModel):
    """Classe Comissão."""

    class Meta:
        """Class Meta."""

    previus_commission = models.ForeignKey(
        "Commission",
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Comissão Anterior",
        on_delete=models.CASCADE,
    )
    publication = models.ForeignKey(
        "rh.Publicacao",
        related_name="+",
        verbose_name="Publicação",
        on_delete=models.CASCADE,
    )
    start_date = models.DateField(blank=True, verbose_name="Data Início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    def __str__(self):
        """Unicode."""
        return "Comissão: %s à %s - %s " % (
            DateUtils.date_to_str(self.start_date),
            DateUtils.date_to_str(self.end_date) if self.end_date else "",
            self.publication,
        )

    def save(self, *args, **kwargs):
        """Method save."""
        if self.previus_commission:
            Commission.objects.filter(pk=self.previus_commission.pk).update(
                end_date=self.start_date - timedelta(1)
            )
        super(Commission, self).save(*args, **kwargs)


class MemberCommission(AuditTimestampModel):
    """Classe Membro da Comissão."""

    class Meta:
        """Class Meta."""

        ordering = ("order",)
        permissions = (("apd_commission", "Comissão de APD"),)

    commission = models.ForeignKey(
        "Commission", verbose_name="Comissão", on_delete=models.CASCADE
    )
    member = models.ForeignKey(
        Servidor, verbose_name="Membro", on_delete=models.CASCADE
    )
    type_participant = models.CharField(
        max_length=1,
        choices=list(TYPE_PARTICIPANT.items()),
        default=4,
        verbose_name="Tipo de Membro",
    )
    order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Ordem"
    )
    impediment = models.BooleanField(default=False, verbose_name="Impedimento")

    def next_position(self):
        """Retorna a proxima posição na lista da comissão."""
        return (
            int(
                MemberCommission.objects.filter(commission=self.commission)
                .aggregate(last_position=models.Max("order"))
                .get("last_position")
                or 0
            )
            + 1
        )

    def get_display(self):
        """Retorna display do campo type_participant."""
        if int(self.type_participant) == 1:
            return "PRESIDENTE"
        elif int(self.type_participant) == 2:
            return "SECRETÁRIO"
        elif int(self.type_participant) == 3:
            return "INTEGRANTE"
        elif int(self.type_participant) == 4:
            return "SUPLENTE"

    def move_up(self):
        """Movimenta para posição inferior."""
        if self.order == 1:
            return False
        else:
            try:
                mc = MemberCommission.objects.get(
                    commission=self.commission, order=(self.order - 1)
                )
            except Exception as e:
                log.exception(e)
                mc = None
            finally:
                if mc is not None:
                    mc.order = self.order
                    mc.save()
                self.order -= 1
                self.save()
                return True

    def move_down(self):
        """Movimenta para posição superior."""
        try:
            mc = MemberCommission.objects.get(
                commission=self.commission, order=(self.order + 1)
            )
        except Exception as e:
            mc = None
            log.exception(e)
        finally:
            if mc is not None:
                mc.order = self.order
                mc.save()
                self.order += 1
                self.save()
                return True
            else:
                return False

    def reorder(self):
        """Reordena as posições da comissão."""
        position = 1
        for mc in MemberCommission.objects.filter(commission=self.commission).order_by(
            "order"
        ):
            if mc.order != position:
                mc.order = position
                mc.save()
            position += 1

    def save(self, *args, **kwargs):
        """Method save."""
        log.info(self.type_participant)
        comissao_permission, created = ControllerPermission.objects.get_or_create(
            name="apd-commission"
        )
        comissao_permission.users.add(self.member.user)
        group, created = Group.objects.get_or_create(name="apd-commission")
        self.member.user.groups.add(group)

        if not self.pk:
            self.order = self.next_position()

        super(MemberCommission, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Method delete."""
        comissao_permission = ControllerPermission.objects.get(name="apd-commission")
        comissao_permission.users.remove(self.member.user)
        group = Group.objects.get(name="apd-commission")
        self.member.user.groups.remove(group)

        super(MemberCommission, self).delete(*args, **kwargs)
        self.reorder()


class PeriodicEvaluationPerformance(AuditTimestampModel):
    """Classe Avaliação Periódica de Desempenho."""

    class Meta:
        """Class Meta."""

        ordering = ("end_date",)

        permissions = (
            ("apd_admin", "Administrador de APD"),
            ("apd_boss", "Avaliador de APD"),
            ("apd_subordinate", "Avaliado APD"),
        )

    configuration = models.ForeignKey(
        Configuration, verbose_name="Configuração", on_delete=models.CASCADE
    )
    commission = models.ForeignKey(
        Commission,
        verbose_name="Comissão de Avaliação",
        on_delete=models.CASCADE,
        blank=True,
    )
    previous_apd = models.ForeignKey(
        "PeriodicEvaluationPerformance",
        related_name="+",
        null=True,
        blank=True,
        verbose_name="APD Anterior",
        on_delete=models.CASCADE,
    )
    employee = models.ForeignKey(
        "rh.MovimentacaoPosse", related_name="apd", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=1,
        default=1,
        choices=list(STATUS_PERIODICEVALUATION.items()),
        verbose_name="Status da APD",
    )
    start_date = models.DateField(blank=True, verbose_name="Data Início")
    end_date = models.DateField(blank=True, verbose_name="Data Fim")
    days_suspended = models.IntegerField(null=True, default=0)
    state_evaluation = models.CharField(
        max_length=1, choices=list(STATUS_EVALUATION.items()), default=1, blank=True
    )
    date_science_evaluation = models.DateTimeField(
        blank=True, null=True, verbose_name="Data Ciência do resultado da avaliação"
    )
    date_automatica_science = models.DateTimeField(
        blank=True, null=True, verbose_name="Data da Ciência e Manifestação Automática"
    )
    final_score = models.DecimalField(
        null=True,
        blank=True,
        default=0,
        max_digits=11,
        decimal_places=2,
        verbose_name="Média final",
    )
    top_score = models.DecimalField(
        null=True,
        blank=True,
        default=0,
        max_digits=11,
        decimal_places=2,
        verbose_name="Média máxima",
    )
    copied_from_stage = models.BooleanField(
        default=False, verbose_name="Copiado do estágio?"
    )
    lock_in = models.SmallIntegerField(default=30, verbose_name="Dias até o bloqueio")

    LICENCA_DOENCA = 120
    LICENCA_DOENCA_PESSOA_FAMILIA = 90
    LICENCA_MATERNIDADE = 180
    LICENCA_ATIVIDADE_POLITICA = 90

    def __str__(self):
        return "%s - %s à %s " % (
            self.employee.servidor,
            DateUtils.date_to_str(self.start_date),
            DateUtils.date_to_str(self.end_date) if self.end_date else "",
        )

    def validate(self, qr, qtype):
        evaluation = False
        manifestation = False
        if self.evaluation_apd.exists():
            evaluation = (
                self.evaluation_apd.first().questionnaire_response
                and qr == self.evaluation_apd.first().questionnaire_response
            )
        if self.manifestation_apd.exists():
            manifestation = (
                self.manifestation_apd.first().questionnaire_response
                and qr == self.manifestation_apd.first().questionnaire_response
            )
        if qtype == "manifestation":
            log.debug(f"RETORNEI mani: {manifestation}")
            return manifestation
        if qtype == "evaluation":
            log.debug(f"RETORNEI evalu: {evaluation}")
            return evaluation

        return evaluation or manifestation

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.lock_in = self.configuration.deadline_blocking
        super().save()

    class BlockEvaluation(Exception):
        """Classe que retorna mensagem de exceção."""

        def __init__(self):
            """."""
            Exception.__init__(self, "Esta avaliação não pode mais ser alterada.")

    class BlockManifestation(Exception):
        """Classe que retorna mensagem de exceção."""

        def __init__(self):
            """."""
            Exception.__init__(self, "Não é possivel alterar esta manifestação.")

    @classmethod
    def postpone_lock(cls, pks=[], days=None):
        if days:
            cls.objects.filter(pk__in=pks).update(lock_in=models.F("lock_in") + days)

    @property
    def deadline_begin(self):
        """RETORNA A QUANTOS DIAS PROXIMO DO FINAL DA APD DEVE SER AVISADO QUE O PERIODO ESTÁ ENCERRANDO."""
        return self.configuration.deadline_begin

    @property
    def deadline(self):
        """Retorna a deadline para fazer marcação visual em cores no grid gestor de APD.

        RETORNA 0: PARA BACKGROUND EM BRANCO
        RETORNA 1: PARA BACKGROUND VERDE
        RETORNA 2: PARA BACKGROUND VERMELHO.
        RETORNA 3 e 4: PARA BACKGROUND LARANJA.
        """
        rs = 0
        if self.end_date:
            if self.copied_from_stage:
                rs = 4
            elif self.evaluation_apd.exists() and not self.manifestation_apd.exists():
                rs = 3
            elif self.evaluation_apd.exists() and self.manifestation_apd.exists():
                rs = 4
            elif self.is_bloke and not self.is_about_begin:
                rs = 2
            elif self.is_allowed_begin:
                rs = 1
        return rs

    @property
    def icon_status_evaluation(self):
        """RETORNA O STATUS DA APD

        RETORNA 0: AGUARDANDO AVALIACAO
        RETORNA 1: LIBERADA PARA AVALIACAO
        RETORNA 2: AVALIACAO ATRASADA
        """
        if self.deadline == 0:
            days = self.days_to_begin + 1 - self.deadline_begin
            if days > 0:
                return {
                    "iconCls": "icon-apd icon-apd-status-offline",
                    "title": f"Falta(m) {days} dia(s) para liberação.",
                }
            return {
                "iconCls": "icon-apd icon-apd-status-offline",
                "title": "Aguardando liberação.",
            }
        elif self.deadline == 1:
            return {
                "iconCls": "icon-apd icon-apd-status-active",
                "title": "Avaliação liberada.",
            }
        elif self.deadline == 2 and not self.copied_from_stage:
            days = self.days_to_begin + 1 - self.deadline_begin
            if days > 0:
                return {
                    "iconCls": "icon-apd icon-apd-status-offline",
                    "title": f"Falta(m) {days} dia(s) para liberação.",
                }
            return {
                "iconCls": "icon-apd icon-apd-status-inactive",
                "title": "Avaliação ou Manifestação atrasada.",
            }
        elif self.deadline == 3:
            return {
                "iconCls": "icon-apd icon-apd-status-away",
                "title": "Aguardando Manifestação.",
            }
        elif self.deadline == 4:
            return {
                "iconCls": "icon-apd icon-apd-status-away",
                "title": "Aguardando finalização da etapa.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    def _released(self):
        """Retorna true liberando a avaliação do chefe, caso esteja a 15 dias ou menos da data final da avaliação."""
        return self.end_date and datetime.date.today() <= (
            self.end_date - relativedelta(days=self.deadline_begin)
        )

    def action_state_evaluation(self, action=None):
        """Verifica se é possivel realizar uma ação de alteração de Avaliação ou Manifestacao.

        Verifica ainda se é possível a finalização de etapa, bloqueando caso o estado da avaliacao não permita
        @ACAO = O que esta querendo realizar (1 = AlterarAvaliacao/Avaliar, 2 = AlterarManifestacao/Manifestar,3 = Finalizar)
        @ESTADO = Estado da avalicao (1 = NOVO, 2 = AVALIADO, 3 = MANIFESTADO, 4 = FINALIZADO).

        """
        if action is None:
            return False
        elif action == 1:
            return True if int(self.state_evaluation) != 4 else False
        elif action == 2:
            return (
                True
                if int(self.state_evaluation) == 2 or int(self.state_evaluation) == 3
                else False
            )
        elif action == 3:
            return True if int(self.state_evaluation) == 3 else False

    def gera_chave(self):
        """Gera uma chave para ser usada ao responder um questionário."""
        chave = hashlib.sha224(bytes(self.employee.servidor.matricula)).hexdigest()
        return chave

    def get_evaluation_period(self):
        """RETORNA UNICODE DO PERÍODO DA AVALIAÇÃO DA APD."""
        return "%s - %s " % (
            DateUtils.date_to_str(self.start_date),
            DateUtils.date_to_str(self.end_date) if self.end_date else "",
        )

    @property
    def icon_evaluation(self):
        """Retorna ícone de avaliação realizada."""
        if self.evaluation_apd.exists():
            return {
                "iconCls": "icon-apd icon-apd-boss",
                "title": "Avaliação realizada.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_manifestation(self):
        """Retorna ícone de manifestação realizada."""
        if self.manifestation_apd.exists():
            return {
                "iconCls": "icon-apd icon-apd-subordinate",
                "title": "Manifestação da avaliação realizada.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_resource(self):
        """Retorna ícone de solicitação de recursos realizada."""
        if self.exists_resource():
            if self.get_evaluation().resource_apd.exists():
                if self.get_evaluation().resource_apd.latest("id").decision:
                    return {
                        "iconCls": "icon-apd icon-apd-decision-resource",
                        "title": "O recurso da avaliação foi julgado pela comissão.",
                    }
                else:
                    return {
                        "iconCls": "icon-apd icon-apd-blue-document-arrow",
                        "title": "Servidor solicitou recurso. Aguardando julgamento do recurso pela comissão.",
                    }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_reconsideration(self):
        """Retorna ícone de reconsideração de avaliação realizada."""
        if self.exists_reconsideration():
            if self.get_evaluation().date_opinion_request_reconsideration:
                return {
                    "iconCls": "icon-apd icon-apd-page-go",
                    "title": "Chefe imediato respondeu o pedido de reconsideração da avaliação.",
                }
            else:
                return {
                    "iconCls": "icon-apd icon-apd-reconsideration",
                    "title": "Servidor solicitou reconsideração da avaliação. \
                <br> Data da Solicitação: %s \
                <br>Prazo para reconsiderar o pedido se esgota em: %s dia(s) \
                "
                    % (
                        DateUtils.date_to_str(
                            self.get_evaluation().date_reconsideration
                        ),
                        self.get_evaluation().get_days_to_reconsideration(),
                    ),
                }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_science_resource_decision(self):
        """Retorna ícone de ciência do recurso realizada."""
        if self.exists_science_resource_decision():
            return {
                "iconCls": "icon-apd icon-apd-eye",
                "title": "Servidor já deu ciência da decisão do recurso.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_science_evaluation(self):
        """Retorna ícone de ciência do resultado da avaliação."""
        if self.evaluation_apd.exists() and self.date_automatica_science:
            return {
                "iconCls": "icon-apd icon-apd-exclamation",
                "title": "Ciência ou manifestação automática.",
            }
        elif self.date_science_evaluation:
            return {
                "iconCls": "icon-apd icon-apd-eye",
                "title": "Servidor já deu ciência do resultado da avaliação.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_homologation(self):
        """Retorna ícone de homologação de apd publicada."""
        if self.homologation_apd.exists():
            return {
                "iconCls": "icon-apd icon-apd-publication-sent",
                "title": "Publicação da Homologação realizada.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_license_active(self):
        """Retorna ícone de homologação de apd publicada."""
        if self.exists_license():
            return {
                "iconCls": "icon-apd icon-apd-sofa-exclamation",
                "title": "Servidor possui uma licença/afastamento ativo.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icon_status(self):
        """Retorna ícone de status."""
        if int(self.status) == 1:
            return {
                "iconCls": "icon-apd icon-apd-status-active",
                "title": "Período Ativo.",
            }
        elif int(self.status) == 2:
            return {
                "iconCls": "icon-apd icon-apd-status-inactive",
                "title": "Período Inativo.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icons(self):
        """Retorna ícones."""
        lista = []
        lista.append(self.icon_status_evaluation)
        lista.append(self.icon_license_active)
        lista.append(self.icon_homologation)
        lista.append(self.icon_evaluation)
        lista.append(self.icon_manifestation)
        lista.append(self.icon_reconsideration)
        lista.append(self.icon_resource)
        lista.append(self.icon_science_evaluation)
        lista.append(self.icon_science_resource_decision)
        return lista

    # uiliton borges
    def days_off_while_apd(self):
        """CONTA QUANTOS DIAS DE AFASTAMENTO DURANTE O PERÍODO DO APD ATUAL."""
        days_off_set = BaseLicencaAfastamento.objects.filter(
            tipo__in=(10, 12, 11, 9, 13, 16),
            servidor_id=self.employee.servidor.id,
            data_inicio__gte=self.start_date,
            data_fim__lte=self.end_date,
            estado__in=(2, 3),
        )
        days_off = 0
        try:
            for d in days_off_set:
                dr = NewDateRange(d.data_inicio, d.data_fim)
                days_off = days_off + dr.days
        except Exception as inst:
            print(inst)
            days_off = -1
        return days_off

    def automatic_manifestation_science(self):
        """SE ESTIVER FORA DO PRAZO DE SE MANIFESTAR OU DAR CIÊNCIA, ESTAS SERÃO AUTOMÁTICAS"""
        today = datetime.datetime.now()
        rules = [bool(self.exists_manifestation()), bool(self.exists_science())]
        if (
            not all(rules)
            and not self.date_automatica_science
            and self.is_this_month()
            and today.day > 15
        ):
            self.date_automatica_science = today
            self.save()

    def is_this_month(self):
        today = datetime.datetime.now()
        if today.year == self.end_date.year and today.month == self.end_date.month:
            return True
        else:
            return False

    @property
    def days_to_begin(self):
        today = datetime.date.today()
        date_month = datetime.datetime(
            self.end_date.year, self.end_date.month, self.end_date.day
        ).date()
        days_to_begin = 0
        if today < date_month:
            days_to_begin = (date_month - today).days
        return days_to_begin

    @property
    def is_about_begin(self):
        return self.days_to_begin > self.deadline_begin

    @property
    def is_allowed_begin(self):
        return self.days_to_begin <= self.deadline_begin

    @property
    def days_to_bloke(self, today=datetime.date.today()):

        if self.days_suspended > 0:
            end_date = self.end_date
        else:
            next_year = (self.start_date + relativedelta(years=1)).year
            # date_month = datetime.datetime(next_year, self.end_date.month, 1).date()
            """ modificado para caso onde o servidor finalizou 31/05 e a data início 01/06 e a regra anterior"""
            end_date = datetime.datetime(next_year, self.end_date.month, 1).date()
        days = 0
        if today > end_date:
            days = NewDateRange(end_date, today).days
        return days

    @property
    def is_bloke(self):
        return self.days_to_bloke > self.lock_in

    def evaluation_after_date(self):
        pass

    def evaluation_outofdate(self):
        """VERIFICA SE A AVALIAÇÃO ESTÁ FORA OU DENTRO DO PRAZO."""
        answer = False
        if (
            not self.exists_evaluation()
            or not self.exists_manifestation()
            or not self.exists_science()
        ):
            if self.configuration.deadline_blocking != 0 and self.is_bloke:
                answer = True
            elif self.configuration.deadline_begin != 0 and self.is_about_begin:
                answer = True
            elif self.days_off_while_apd() > 275:
                answer = True
        return answer

    def can_boss_evaluate(self):
        # self.automatic_manifestation_science()
        return not self.evaluation_outofdate()

    def exists_science(self):
        """Verifica se há registro de ciência."""
        return True if self.date_science_evaluation else False

    def exists_automatic_science(self):
        """Verifica se há registro de ciência automática."""
        return True if self.date_automatica_science else False

    def exists_license(self):
        """VERIFICA SE EXISTE UMA LICENÇA ATIVA PARA UM SERVIDOR."""
        data = datetime.date.today()
        return (
            self.employee.servidor.get_afastamentos(data)
            .filter(baselicencaafastamento__remunerado=False)
            .exclude(baselicencaafastamento__estado__in=[SCHEDULED, CANCELED])
            .exists()
        )

    def get_evaluation(self):
        """Retorna objeto avaliação."""
        if self.exists_evaluation():
            return self.evaluation_apd.latest("id")
        else:
            return None

    def get_manifestation(self):
        """Retorna objeto manifestação."""
        if self.exists_manifestation():
            return self.manifestation_apd.latest("id")
        else:
            return None

    def exists_evaluation(self):
        """Verifica se existe uma avaliação."""
        return True if self.evaluation_apd.exists() else False

    def exists_resource(self):
        """Verifica se existe um recurso."""
        if self.evaluation_apd.exists():
            evaluation = self.get_evaluation()
            return True if evaluation.exists_resource() else False
        else:
            return False

    def exists_science_resource_decision(self):
        """Verifica se existe ciência do recurso da avaliação."""
        if self.exists_resource():
            evaluation = self.get_evaluation()
            return True if evaluation.science_decision_resource() else False
        else:
            return False

    def exists_reconsideration(self):
        """Verifica se existe um pedido de reconsideração."""
        if self.evaluation_apd.exists():
            evaluation = self.get_evaluation()
            return True if evaluation.reconsideration_flag else False
        else:
            return False

    def exists_manifestation(self):
        """Verifica se existe uma manifestação."""
        return True if self.manifestation_apd.exists() else False

    def get_immediate_boss(self):
        """RETORNA O CHEFE IMEDIATO."""
        return (
            self.employee.servidor.chefe_imediato
            if self.employee.servidor.chefe_imediato
            else None
        )

    def finish(self):
        """Finaliza uma etapa da APD."""
        self.status = 2
        self.state_evaluation = 2
        self.save()

    def homologation(self):
        """Homologa a finalização de uma apd."""
        self.validate_modified()

        if not self.copied_from_stage:
            if not self.exists_evaluation():
                raise Exception(
                    "Não é possível finalizar essa etapa. Avaliação pendente!"
                )

            if not self.exists_manifestation() and not self.date_automatica_science:
                raise Exception(
                    "Não é possível finalizar essa etapa. Ciência ou Manifestação pendente!"
                )

        self.finish()
        self.create_next()

    def create_next(self):
        configuration = Configuration.objects.get(end_date__isnull=True)
        commission = Commission.objects.get(end_date__isnull=True)

        employee = self.employee.servidor

        start_date = self.end_date + relativedelta(days=1)

        if not employee.data_desligamento or employee.data_desligamento <= start_date:

            new_apd = PeriodicEvaluationPerformance(
                previous_apd=self,
                configuration=configuration,
                commission=commission,
                employee=self.employee,
                start_date=start_date,
                end_date=self.end_date
                + relativedelta(months=configuration.interval_periodic_evaluation),
            )
            new_apd.save()
            Notification.notify(
                "apd-newperiod",
                new_apd.employee.servidor,
                types=("SYS",),
                **{
                    "start": DateUtils.date_to_str(new_apd.start_date),
                    "end": DateUtils.date_to_str(new_apd.end_date),
                },
            )

    def validate_modified(self):
        """Valida se uma etapa pode ser modificada."""
        if int(self.status) == 2 or int(self.state_evaluation) == 4:
            raise Exception("Essa etapa já foi finalizada!")

    def get_add_scores(self):
        """Rotina que executa o preenchimento do modelo ScoreEvaluation com a avaliação de uma APD."""
        # log.info('Salvando Scores..........')
        q = self.configuration.questionnaire_boss_id
        total_max_pontos = 0
        evaluation = self.get_evaluation()
        for elemento_pai in Elemento.objects.filter(
            questionario=q, elemento_pai__isnull=True
        ):
            if elemento_pai.elemento.tipo == "Ref. Textual":
                # print 'QUESITO -> *Ref. Textual %s ' % elemento_pai
                top_score_question = 0
                total_score_evaluation = 0
                for el in Elemento.objects.filter(elemento_pai=elemento_pai):
                    questao = Questao.objects.get(pk=el.elemento.id)

                    response_evaluation = Resposta.objects.get(
                        questao=questao,
                        questionario_resposta=evaluation.questionnaire_response,
                    )
                    total_score_evaluation += response_evaluation.peso
                    top_score_question += int(
                        Alternativa.objects.filter(questao=questao)
                        .aggregate(models.Max("valor"))
                        .get("valor__max")
                    )
                    total_max_pontos += int(
                        Alternativa.objects.filter(questao=questao)
                        .aggregate(models.Max("valor"))
                        .get("valor__max")
                    )
                # print '==>>>> Total de pontos do QUESITO: %s ' % top_score_question
                # print '==>>>> Total de pontos da AVALIACAO QUESITO: %s ' % total_score_evaluation

                score_evaluation, created = ScoreEvaluation.objects.update_or_create(
                    evaluation=evaluation,
                    element=elemento_pai,
                    defaults={
                        "score_obtained": total_score_evaluation,
                        "top_score": top_score_question,
                        "final_score": total_score_evaluation,
                    },
                )
        # print total_max_pontos
        log.info("Salvando Scores de uma Avaliação de APD..........")

    def _get_scores(self):
        total = 0
        obtained = 0
        if self.copied_from_stage:
            total = self.top_score
            obtained = self.final_score
        elif self.evaluation_apd.exists():
            ev = self.get_evaluation()
            for se in ev.score_evaluation.all():
                total += se.top_score
                obtained += se.score_obtained
        return total, obtained

    def get_scores_obtained(self):
        total, obtained = self._get_scores()
        result = round((obtained / total) * 100, 1) if total != 0 else 0
        return "%s%%" % result

    def notify_membercommission(self):
        """Notifica membros da comissão."""
        Notification.notify_all(
            "apd-resource",
            [
                user.member
                for user in self.commission.membercommission_set.all()
                if self.commission.membercommission_set.filter().count()
            ],
            types=("SYS",),
            **{
                "from": self.employee.servidor,
                "start": DateUtils.date_to_str(self.start_date),
                "end": DateUtils.date_to_str(self.end_date),
                "deadline": self.configuration.deadline_judge_resource,
            },
        )

    def notify_boss_resource(self):
        """Notifica o chefe que o servidor solicitou recurso de uma avaliação."""
        Notification.notify(
            "apd-boss-resource",
            self.get_immediate_boss(),
            types=("SYS",),
            **{
                "from": self.employee.servidor,
                "start": DateUtils.date_to_str(self.start_date),
                "end": DateUtils.date_to_str(self.end_date),
            },
        )

    def notify_science(self):
        """Notifica gestores da APD da ciencia do servidor de uma avaliacao."""
        gestor_permission = ControllerPermission.objects.get(name="apd-admin")
        Notification.notify_all(
            "apd-science",
            [
                user.servidor.all()[0]
                for user in gestor_permission.users.all()
                if user.servidor.count()
            ],
            types=("SYS",),
            **{
                "from": self.employee.servidor,
                "start": DateUtils.date_to_str(self.start_date),
                "end": DateUtils.date_to_str(self.end_date),
            },
        )

    def notify_released_evaluation(self, boss=None):
        """
        Notifica o chefe de um servidor que a avaliação de uma etapa da APD foi liberada para avaliação.
        """
        if boss:
            Notification.notify(
                "apd-released",
                boss,
                types=("SYS",),
                **{
                    "from": self.employee.servidor,
                    "start": DateUtils.date_to_str(self.start_date),
                    "end": DateUtils.date_to_str(self.end_date),
                },
            )

    def notify_delayed_evaluation(self, boss=None):
        """
        Notifica o chefe de um servidor que a avaliação de uma etapa da APD foi liberada para avaliação.
        """
        if boss:
            Notification.notify(
                "apd-delayed",
                boss,
                types=("SYS",),
                **{
                    "from": self.employee.servidor,
                    "start": DateUtils.date_to_str(self.start_date),
                    "end": DateUtils.date_to_str(self.end_date),
                },
            )

    def update_end_date(self, days=0):
        """Atualiza a data final de uma APD conforme licenças que impedem sua realização."""
        """
            days=(days - 1), utilizou-se -1 pois subtrai-se -1 do intervalo total
        """
        self.end_date = self.start_date + relativedelta(
            months=self.configuration.interval_periodic_evaluation, days=(days - 1)
        )
        self.days_suspended = days
        self.save()

    def days_suspended_cron(self):
        """Calcula os dias de suspensao em uma etapa."""
        base = NewDateRange(self.start_date, self.end_date)
        range_licenca_total = NewDateRange()
        ESTADOS = [
            1,
            4,
        ]

        # ================================LicencaAfastamentoConjuge==========================================================
        afastamento_conjuge = (
            LicencaAfastamentoConjuge.objects.filter(
                servidor__matricula=self.employee.servidor.matricula, remunerado=False
            )
            .exclude(
                models.Q(data_inicio__gt=base.last)
                | models.Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )

        for licenca in afastamento_conjuge:
            range_conjuge = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_conjuge

        # ================================LicencaInteresseParticular==========================================================
        licensa_particular = (
            LicencaInteresseParticular.objects.filter(
                servidor__matricula=self.employee.servidor.matricula
            )
            .exclude(
                models.Q(data_inicio__gt=base.last)
                | models.Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )

        for licenca in licensa_particular:
            range_particular = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_particular

        # ================================AfastamentoSuspensao==========================================================
        afastamento_suspensao = (
            AfastamentoSuspensao.objects.filter(
                servidor__matricula=self.employee.servidor.matricula
            )
            .exclude(
                models.Q(data_inicio__gt=base.last)
                | models.Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )

        for licenca in afastamento_suspensao:
            range_suspensao = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_suspensao

        # ==================================AfastamentoPrisao================================================
        afastamento_prisao = (
            AfastamentoPrisao.objects.filter(
                servidor__matricula=self.employee.servidor.matricula
            )
            .exclude(
                models.Q(data_inicio__gt=base.last)
                | models.Q(data_fim__isnull=False, data_fim__lt=base.first)
            )
            .exclude(estado__in=ESTADOS)
        )
        for licenca in afastamento_prisao:
            range_prisao = NewDateRange(licenca.data_inicio, licenca.data_fim)
            range_licenca_total += range_prisao

        log.info(
            "Atualizando APD de: %s acrescentado: %d dias."
            % (self, range_licenca_total.days)
        )
        if range_licenca_total.days > 0:
            self.update_end_date(range_licenca_total.days)
            log.info(
                "Atualizando APD de: %s acrescentado: %d dias."
                % (self, range_licenca_total.days)
            )

    def _repeat_last_evaluation_from_apd(self, justification=""):
        old_evaluation = self.previous_apd.get_evaluation()
        old_manifestation = self.previous_apd.get_manifestation()

        # ====== ROTINA DE CÓPIA DE AVALIAÇÃO ======

        # Avaliação = criar novo QuestionarioResposta da avaliação com base no ultimo
        new_questionnaire_response = QuestionarioResposta(
            chave=old_evaluation.questionnaire_response.chave,
            questionario=old_evaluation.questionnaire_response.questionario,
        )
        new_questionnaire_response.save()

        # Criar as responstas do novo QuestionarioResposta copiando as do Questionario resposta da ultima avaliação
        for old_response in Resposta.objects.filter(
            questionario_resposta=old_evaluation.questionnaire_response
        ):
            Resposta(
                questao=old_response.questao,
                questionario_resposta=new_questionnaire_response,
                alternativa=old_response.alternativa,
                texto=old_response.texto,
                peso=old_response.peso,
            ).save()

        # Criar nova avaliação com base na ultima
        new_evaluation = Evaluation(
            questionnaire_response=new_questionnaire_response,
            subordinate=self,
            boss=old_evaluation.boss,
            start_period_evaluation=self.start_date,
            end_period_evaluation=self.end_date,
            days_suspended_evaluation=self.days_suspended,
            reconsideration_flag=old_evaluation.reconsideration_flag,
            text_reconsideration=old_evaluation.text_reconsideration,
            date_reconsideration=old_evaluation.date_reconsideration,
            repetition_flag=True,
            text_justification_repetition=justification,
        )
        new_evaluation.save()

        #  === Rotina que executa o preenchimento do modelo ScoreEvaluation com a avaliação de uma APD.
        self.get_add_scores()

        # ====== ROTINA DE CÓPIA DE MANIFESTAÇÃO ======

        # criar QuestionarioResposta da manifestação
        if old_manifestation:
            new_questionnaire_response_manif = QuestionarioResposta(
                chave=old_manifestation.questionnaire_response.chave,
                questionario=old_manifestation.questionnaire_response.questionario,
            )
            new_questionnaire_response_manif.save()

            # Criar as responstas do antigo questionario resposta da Manifestação para a nova manifestação
            for old_response_manif in Resposta.objects.filter(
                questionario_resposta=old_manifestation.questionnaire_response
            ):
                Resposta(
                    questao=old_response_manif.questao,
                    questionario_resposta=new_questionnaire_response_manif,
                    alternativa=old_response_manif.alternativa,
                    texto=old_response_manif.texto,
                    peso=old_response_manif.peso,
                ).save()

            # Cria uma nova Manifestation
            new_manifestation = Manifestation(
                evaluation=new_evaluation,
                subordinate=self,
                questionnaire_response=new_questionnaire_response_manif,
            )
            new_manifestation.save()

    def _repeat_last_evaluation_from_stage(self, justification=""):
        stage = EstagioProbatorioServidor.objects.filter(
            posse_servidor__servidor=self.employee.servidor
        ).first()
        if not stage:
            raise Exception(
                "Não foi encontrada nenhum estágio probatório para o servidor %s!"
                % self.employee.servidor
            )

        self.copied_from_stage = True
        self.final_score = stage._media_conceito_final[0]
        self.top_score = stage._media_conceito_max
        self.save()

    def repeat_last_evaluation(self, justification=""):
        with transaction.atomic():
            old_apd = self.previous_apd
            self.validate_modified()
            if not old_apd:
                self._repeat_last_evaluation_from_stage(justification=justification)
            else:
                self._repeat_last_evaluation_from_apd(justification=justification)


class Evaluation(AuditTimestampModel):
    """Classe Avaliação."""

    questionnaire_response = models.ForeignKey(
        QuestionarioResposta,
        related_name="evaluation_apd",
        verbose_name="Questionário Resposta",
        on_delete=models.CASCADE,
    )
    subordinate = models.ForeignKey(
        PeriodicEvaluationPerformance,
        related_name="evaluation_apd",
        on_delete=models.PROTECT,
        verbose_name="Avaliado",
    )
    boss = models.ForeignKey(
        "rh.Servidor",
        related_name="evaluation_apd",
        verbose_name="Avaliador",
        on_delete=models.CASCADE,
    )
    start_period_evaluation = models.DateField(
        blank=True, verbose_name="Data Início Período"
    )
    end_period_evaluation = models.DateField(
        blank=True, verbose_name="Data Fim Período"
    )
    days_suspended_evaluation = models.DecimalField(
        null=True, default=0, max_digits=11, decimal_places=2
    )
    reconsideration_flag = models.BooleanField(default=False)
    repetition_flag = models.BooleanField(
        default=False, verbose_name="Nota repetida de outra avaliação"
    )
    text_reconsideration = models.TextField(
        default="", verbose_name="Texto do pedido de reconsideração"
    )
    date_reconsideration = models.DateField(
        null=True, blank=True, verbose_name="Data solicitada a reconsideração"
    )
    opinion_request_reconsideration = models.TextField(
        default="",
        verbose_name="Parecer do avaliador quanto ao pedido de reconsideração do avaliado",
    )
    date_opinion_request_reconsideration = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do parecer do avaliador quanto ao pedido de reconsideração",
    )
    text_justification_repetition = models.TextField(
        default="", verbose_name="Texto do motivo da repetição de avaliação"
    )
    external_evaluator = models.TextField(
        null=True, blank=True, verbose_name="Avaliador de Órgão Externo"
    )
    external_registration = models.TextField(
        null=True, blank=True, verbose_name="Matricula do Avaliador de Órgão Externo"
    )
    external_jobposition = models.TextField(
        null=True, blank=True, verbose_name="Cargo do Avaliador de Órgão Externo"
    )
    external_workplace = models.TextField(
        null=True, blank=True, verbose_name="Lotação do Avaliador de Órgão Externo"
    )
    date_external_evaluation = models.DateField(
        null=True, blank=True, verbose_name="Data da Avaliação Externa"
    )

    def __str__(self):
        return "%s - %s à %s " % (
            self.subordinate.employee,
            DateUtils.date_to_str(self.start_period_evaluation),
            DateUtils.date_to_str(self.end_period_evaluation),
        )

    def exists_resource(self):
        """Verifica de existe recurso."""
        return True if self.resource_apd.exists() else False

    def decision_resource(self):
        """Verifica de existe a decisão de um recurso."""
        if self.exists_resource():
            resource = self.resource_apd.latest("id")
            return True if resource.decision_resource.exists() else False
        else:
            return False

    def science_decision_resource(self):
        """Verifica de existe a ciência da decisão de um recurso."""
        if self.exists_resource():
            resource = self.resource_apd.latest("id")
            return True if resource.date_science_decision else False
        else:
            return False

    @property
    def deadline_reconsideration(self):
        """RETORNA A QUANTIDADE DE DIAS PARA SOLICITAR A RECONSIDERAÇÃO."""
        return self.subordinate.configuration.deadline_reconsideration

    @property
    def deadline_opinion_reconsideration(self):
        """RETORNA A QUANTIDADE DE DIAS PARA DAR O PARECER QUANTO AO PEDIDO DE RECONSIDERAÇÃO."""
        return self.subordinate.configuration.deadline_rectify_evaluation

    def validate_order_reconsideration(self):
        """VERIFICA SE AINDA ESTÁ DENTRO DO PRAZO PARA SOLICITAR PEDIDO DE RECONSIDERAÇÃO DA AVALIAÇÃO."""
        return (
            True
            if NewDateRange.next_day_weekend(
                self.created_at + relativedelta(days=self.deadline_reconsideration)
            )
            > datetime.datetime.now()
            else False
        )

    def validate_order_opinion_reconsideration(self):
        """VERIFICA SE AINDA ESTÁ DENTRO DO PRAZO PARA REALIZAR O PARECER QUANTO AO PEDIDO DE RECONSIDERAÇÃO DA AVALIAÇÃO."""
        return (
            True
            if NewDateRange.next_day_weekend(
                self.date_reconsideration
                + relativedelta(days=self.deadline_opinion_reconsideration)
            )
            > datetime.date.today()
            else False
        )

    def get_days_to_reconsideration(self):
        """RETORNA A QUANTIDADE DE DIAS RESTANTES PARA REALIZAR A RECONSIDERAÇÃO DA AVALIAÇÃO."""
        if self.date_reconsideration:
            max_date = NewDateRange.next_day_weekend(
                self.date_reconsideration
                + relativedelta(days=self.deadline_opinion_reconsideration)
            )
            if datetime.datetime.now().date() > max_date:
                remaining_days = 0
            else:
                remaining_days = NewDateRange(datetime.datetime.now(), max_date).days
            return remaining_days if remaining_days > 0 else 0
        else:
            return 0

    @property
    def deadline_resource(self):
        """RETORNA A QUANTIDADE DE DIAS PARA SOLICITAR O RECURSO."""
        return self.subordinate.configuration.deadline_appeal

    def validate_order_resource(self):
        """VERIFICA SE AINDA ESTÁ DENTRO DO PRAZO SOLICITAR O PEDIDO DE RECURSO DA AVALIAÇÃO."""
        return (
            True
            if NewDateRange.next_day_weekend(
                self.created_at + relativedelta(days=self.deadline_resource)
            )
            > datetime.datetime.now()
            else False
        )

    @property
    def deadline_judge(self):
        """RETORNA A QUANTIDADE DE DIAS PARA A COMISSAO JULGAR O RECURSO."""
        return self.subordinate.configuration.deadline_judge_resource - 1

    def validate_order_judge_resource(self):
        """VERIFICA SE AINDA ESTÁ DENTRO DO PRAZO PARA JULGAR O RECURSO."""
        if self.resource_apd.exists():
            resource = self.resource_apd.latest("id")
            days = resource.get_days_to_judge()
            return True if days > 0 else False
        else:
            return False

    def save(self, *args, **kwargs):
        """Method save."""
        self.subordinate.state_evaluation = 2
        self.subordinate.save()

        self.days_suspended_evaluation = self.subordinate.days_suspended

        super(Evaluation, self).save(*args, **kwargs)
        self.subordinate.get_add_scores()


class ScoreEvaluation(AuditTimestampModel):
    """Classe Pontuação da Avaliação."""

    class Meta:
        """Class meta."""

        pass

    AUDITABLE = {
        "fields": ["score_obtained"],
    }

    evaluation = models.ForeignKey(
        Evaluation,
        related_name="score_evaluation",
        verbose_name="Avaliação de APD",
        on_delete=models.CASCADE,
    )
    element = models.ForeignKey(
        Elemento, related_name="element_score", on_delete=models.CASCADE
    )
    score_obtained = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    top_score = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    final_score = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    date_modified = models.DateField(
        null=True, blank=True, verbose_name="Data modificação da pontuação"
    )
    user_modified = models.ForeignKey(
        "rh.Servidor", related_name="+", null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return (
            "Avaliação %s - Pontos obtidos no fator: %s= %s - Máximo possível de pontos=%s "
            % (
                self.evaluation.subordinate,
                self.element,
                self.score_obtained,
                self.top_score,
            )
        )

    def save(self, *args, **kwargs):
        """Method save."""
        from decimal import Decimal

        if (
            self.date_modified
            and self.user_modified
            and "score_obtained" in self.old_fields
        ):
            raise Exception("Não é permitido alterar essa pontuação!")
        if Decimal(self.final_score) > Decimal(self.top_score):
            raise Exception(
                "A pontuação final não pode ser superior aos pontos possíveis!"
            )

        super(ScoreEvaluation, self).save(*args, **kwargs)


class Manifestation(AuditTimestampModel):
    """Classe Manifestação de avaliação."""

    class Meta:
        """Class meta."""

        pass

    evaluation = models.ForeignKey(
        Evaluation,
        related_name="manifestation_apd",
        verbose_name="Avaliação de APD",
        on_delete=models.CASCADE,
    )
    subordinate = models.ForeignKey(
        PeriodicEvaluationPerformance,
        related_name="manifestation_apd",
        on_delete=models.PROTECT,
        verbose_name="Avaliado",
    )
    questionnaire_response = models.ForeignKey(
        QuestionarioResposta,
        related_name="manifestation_apd",
        verbose_name="Questionário Resposta",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Manifestação: %s" % self.evaluation

    def save(self, *args, **kwargs):
        """Method save."""
        self.subordinate.state_evaluation = 3
        self.subordinate.save()
        # CRIAR FUNCAO PARA PEGAR A QUANTIDADE DE DIAS SUSPENSOS E GRAVAR NO CAMPO CORRESPONDENTE
        super(Manifestation, self).save(*args, **kwargs)


class Resource(AuditTimestampModel):
    """Classe Recurso de Avaliação."""

    class Meta:
        """Class meta."""

        ordering = ("-created_at",)

        permissions = (("apd_resource", "Comissão de Recursos"),)

    evaluation = models.ForeignKey(
        Evaluation,
        related_name="resource_apd",
        verbose_name="Avaliação de APD",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        default=1,
        max_length=1,
        choices=list(STATUS_RESOURCE.items()),
        verbose_name="Status do Recurso",
    )
    decision = models.CharField(
        max_length=1,
        choices=list(DECISION_RESOURCE.items()),
        verbose_name="Decisão do Recurso",
    )
    date_science_decision = models.DateTimeField(
        blank=True, null=True, verbose_name="Data Ciência do Recurso"
    )
    text = models.TextField(default="", verbose_name="Texto do Recurso")

    def __str__(self):
        return "%s" % (self.evaluation,)

    @property
    def icons_decision(self):
        """Retorna o icone com resultado da avaliação do recurso."""
        if self.decision and int(self.decision) == 1:
            return {
                "iconCls": "icon-apd icon-apd-positive",
                "title": "Recurso provido.",
            }
        elif self.decision and int(self.decision) == 2:
            return {"iconCls": "icon-apd icon-apd-negative", "title": "Recurso negado."}
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icons_science(self):
        """Retorna o icone caso haja pendência em ciência do servidor."""
        if self.decision in (1, 2) and not self.date_science_decision:
            return {
                "iconCls": "icon-apd icon-apd-exclamation",
                "title": "Aguardando ciência do servidor.",
            }
        elif self.date_science_decision:
            return {
                "iconCls": "icon-apd icon-apd-eye",
                "title": "Servidor deu ciência da decisão do recurso.",
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def icons_days_judge(self):
        """Retorna o icone com a quantidade de dias restantes para julgamento."""
        if not self.decision and self.get_days_to_judge() > 0:
            return {
                "iconCls": "icon-apd icon-apd-calendar-day",
                "title": "Aguardando julgamento do recurso. \
            <br> Prazo se esgota em: %s dia(s)"
                % self.get_days_to_judge(),
            }
        else:
            return {"iconCls": "icon-apd icon-apd-blank", "title": ""}

    @property
    def deadline(self):
        """Retorna a deadline para fazer marcação visual em cores no grid das solicitações de recurso.

        0 = FUNDO BRANCO
        1 = FUNDO AMARELO
        2 = FUNDO VERMELHO
        """
        days_to_judge = self.evaluation.deadline_judge
        days = self.get_days_to_judge()

        percent_50 = days_to_judge * 50 / 100
        percent_30 = days_to_judge * 30 / 100

        if days >= percent_30 and days <= percent_50:
            return 1
        elif days < percent_30:
            return 2
        else:
            return 0

    @property
    def icons(self):
        """Retorna icones."""
        lista = []
        lista.append(self.icons_days_judge)
        lista.append(self.icons_decision)
        lista.append(self.icons_science)
        return lista

    def get_days_to_judge(self):
        """Retorna a quantidade de dias entre a data máxima para realizar o julgamento e a data do dia atual."""
        d = NewDateRange(
            datetime.datetime.now(),
            NewDateRange.next_day_weekend(
                self.created_at + relativedelta(days=self.evaluation.deadline_judge)
            ),
        )
        return d.days

    @property
    def days_to_judge(self):
        """Retorna a quantidade de dias restantes para julgamento."""
        if self.evaluation.validate_order_judge_resource():
            days = self.get_days_to_judge()
            return "%s dia(s)" % days if days >= 0 else "0 dia(s)"
        else:
            return "0 dia(s)"

    def save(self, *args, **kwargs):
        """Method save."""
        super(Resource, self).save(*args, **kwargs)


class DecisionCommission(AuditTimestampModel):
    """Classe Decisão da Comissão sobre recurso de avaliação."""

    class Meta:
        """Class meta."""

    resource_evaluation = models.ForeignKey(
        Resource,
        related_name="decision_resource",
        verbose_name="Recurso de Avaliação",
        on_delete=models.CASCADE,
    )
    member_commission = models.ForeignKey(
        MemberCommission, related_name="+", on_delete=models.CASCADE
    )
    decision = models.CharField(
        max_length=1,
        choices=list(DECISION_COMISSION.items()),
        verbose_name="Decisão do Recurso",
    )
    text = models.TextField(default="", verbose_name="Observações")

    def __str__(self):
        return "%s -> %s" % (
            self.resource_evaluation,
            self.decision,
        )

    def validate(self):
        """Verifica se já existe uma decisão para um recurso de avaliação de apd."""
        return DecisionCommission.objects.filter(
            resource_evaluation=self.resource_evaluation
        ).exists()

    @property
    def deadline_judge(self):
        """RETORNA A QUANTIDADE DE DIAS PARA JULGAR O RECURSO."""
        return (
            self.resource_evaluation.evaluation.subordinate.configuration.deadline_judge_resource
            - 1
        )

    def validate_order_judge_resource(self):
        """VERIFICA SE AINDA ESTÁ DENTRO DO PRAZO PARA JULGAR O RECURSO."""
        return (
            True
            if NewDateRange.next_day_weekend(
                self.resource_evaluation.created_at
                + relativedelta(days=self.deadline_judge)
            )
            > datetime.datetime.now()
            else False
        )

    def get_decision(self):
        """RETORNA O DISPLAY DA DECISÃO DO RECURSO."""
        if self.decision:
            if int(self.decision) == 1:
                return "DAR PROVIMENTO AO RECURSO SOLICITADO"
            elif int(self.decision) == 2:
                return "NÃO DAR PROVIMENTO AO RECURSO SOLICITADO"
            else:
                return ""
        else:
            return ""

    def save(self, *args, **kwargs):
        """Method save."""
        if self.validate():
            raise Exception("Já existe uma decisão para esse Recurso!")
        if not self.validate_order_judge_resource():
            raise Exception("O prazo para julgamento desse recurso está expirado!")
        if not self.decision:
            raise Exception("O campo decisão do recurso deve ser preenchido!")

        self.resource_evaluation.decision = self.decision
        self.resource_evaluation.status = 2
        self.resource_evaluation.save()

        # NOTIFICA O SERVIDOR QUE SOLICITOU O RECURSO, DA DECISAO DA COMISSAO
        Notification.notify(
            "apd-decision-resource",
            self.resource_evaluation.evaluation.subordinate.employee.servidor,
            types=("SYS",),
            **{
                "decision": self.get_decision(),
            },
        )

        # NOTIFICA ADMINISTRADORES DA APD DA DECISAO DA COMISSAO
        manager_permission = ControllerPermission.objects.get(name="apd-admin")
        Notification.notify_all(
            "apd-decision-resource-msg",
            [user.servidor for user in manager_permission.users.all() if user.servidor],
            types=("SYS",),
            **{
                "employee": self.resource_evaluation.evaluation.subordinate.employee.servidor,
                "period": self.resource_evaluation.evaluation.subordinate.employee,
            },
        )

        super(DecisionCommission, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Method delete."""
        raise Exception("Essa decisão não pode ser removida!")
        log.info("Removendo decisão de recurso %s " % self.resource_evaluation)
        self.resource_evaluation.status = 1
        self.resource_evaluation.decision = ""
        self.resource_evaluation.date_science_decision = None
        self.resource_evaluation.save()
        super(DecisionCommission, self).delete(*args, **kwargs)


class Homologation(AuditTimestampModel):
    """Classe Homologação de APD."""

    class Meta:
        """Class meta."""

    publication = models.ForeignKey(
        "rh.Publicacao",
        related_name="+",
        verbose_name="Publicação",
        on_delete=models.CASCADE,
    )
    periodic_evaluation = models.ForeignKey(
        PeriodicEvaluationPerformance,
        on_delete=models.CASCADE,
        related_name="homologation_apd",
        verbose_name="Avaliação Periódica de Desempenho",
    )
    status = models.CharField(
        max_length=1,
        choices=list(STATUS_HOMOLOGATION.items()),
        verbose_name="Status da Homologacao",
        default=1,
    )
    text = models.TextField(
        default="", verbose_name="Observações", null=True, blank=True
    )
    anotacao_geral = models.ForeignKey(
        AnotacaoGeral,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Anotação Geral",
    )

    def __str__(self):
        return "%s -> %s" % (
            self.publication,
            self.periodic_evaluation,
        )

    def validate(self):
        """Valida se já existe homologação para aquela etapa de APD."""
        return Homologation.objects.filter(
            periodic_evaluation=self.periodic_evaluation
        ).exists()

    def anotacao(self, *args, **kargs):
        tipo = Publicacao.get_tipo(99)
        if self.anotacao_geral is None:
            anotacao_geral = AnotacaoCarreira.manage_instance(
                servidor=self.periodic_evaluation.employee.servidor,
                tipo_documento=tipo,
                texto=self.get_texto(),
                resumo="APD",
            )
            AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
            self.anotacao_geral = anotacao_geral
        else:
            anotacao_geral = AnotacaoCarreira.objects.get(pk=self.anotacao_geral.pk)
            anotacao_geral.texto = self.get_texto()
            anotacao_geral.servidor = self.periodic_evaluation.employee.servidor
            anotacao_geral.tipo_documento = tipo
            anotacao_geral.indireto = False
            anotacao_geral.save()
            AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
        return True

    def get_texto(self):
        texto = ""
        try:
            texto = """O servidor(a) %s concluiu a Avaliação Periódica de Desempenho relativo ao período: %s.Publicação: %s.
                Observação: %s""" % (
                self.periodic_evaluation.employee.servidor.pessoa_fisica.nome,
                self.periodic_evaluation.get_evaluation_period(),
                self.publication,
                self.text,
            )
        except Exception as err:
            log.exception(err)
        return texto

    def save(self, *args, **kwargs):
        self.periodic_evaluation.validate_modified()
        if self.validate():
            raise Exception("Já existe uma Homolgação para essa APD!")

        if int(self.periodic_evaluation.state_evaluation) != 3 and (
            not self.periodic_evaluation.exists_automatic_science()
            and self.periodic_evaluation.date_science_evaluation is None
        ):
            raise Exception(
                "Essa etapa esta pendente de Manifestação ou Ciência. %s" % (self)
            )

        self.status = 2
        log.info("periodic evaluation homologation")
        self.periodic_evaluation.homologation()

        self.anotacao()
        super(Homologation, self).save(*args, **kwargs)
