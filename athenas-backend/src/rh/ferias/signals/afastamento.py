# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.utils import DateUtils, getLogger
from rh.afastamento.models import FeriasAfastamento
from rh.const import CANCELADO, INTERRUPCAO, SUSPENSAO
from rh.ferias.models import (
    PASU_ALTERADO,
    PASU_FRUIDO,
    PASU_FRUINDO,
    PASU_HOMOLOGADO,
    PASU_INTERROMPIDO,
    PASU_NAOAUTORIZADO,
    PASU_SUSPENSO,
    PeriodoAquisitivoServidorUsufruto,
)
from rh.models import Servidor
from rh.utils import send_mail_and_notify

log = getLogger("Ferias:Sinais")


class GerenciaAfastamentoFeriasPasu(object):

    def __init__(self, *args, **kargs):
        """
        pasu = pasu
        4   PASU_HOMOLOGADO: "Homologado", #CRIAR AFASTAMENTO
        16  PASU_ALTERADO: "Alterado",#APAGAR AFASTAMENTO
        32  PASU_INTERROMPIDO: "Interrompido",#ALTERAR AFASTAMENTO
        64  PASU_SUSPENSO: "Suspenso",#APAGAR AFASTAMENTO
        128 PASU_FRUINDO: "Em fruição", #CRIAR AFASTAMENTO
        """
        try:
            self.pasu = kargs.get("pasu")
            log.info("{} - {}".format(self.pasu, self.pasu.get_estado_display()))
            if (
                self.pasu.estado in (PASU_HOMOLOGADO, PASU_FRUINDO, PASU_FRUIDO)
                and kargs.get("apagar", False) is False
            ):
                self.criar()
            elif (
                self.pasu.estado == PASU_INTERROMPIDO
                and kargs.get("apagar", False) is False
            ):
                self.alterar()
            elif (
                self.pasu.estado in (PASU_SUSPENSO, PASU_ALTERADO, PASU_NAOAUTORIZADO)
                or kargs.get("apagar", False) is True
            ):
                self.apagar()
        except Exception as err:
            log.exception(err)
            self.notify(err=err, mensagem="__init__")

    def criar(self):
        try:
            with transaction.atomic():
                ferias = FeriasAfastamento.objects.filter(
                    servidor=self.pasu.periodo_aquisitivo_servidor.servidor,
                    data_inicio=self.pasu.data_inicio,
                    data_prevista=self.pasu.data_prevista_fim,
                ).exclude(estado=CANCELADO)
                if ferias.exists():
                    ferias = ferias.latest("pk")
                else:
                    ferias = FeriasAfastamento(
                        servidor=self.pasu.periodo_aquisitivo_servidor.servidor,
                        data_inicio=self.pasu.data_inicio,
                        data_prevista=self.pasu.data_prevista_fim,
                        publicacao_movimentacao=None,
                    )
                ferias.save()
        except Exception as err:
            log.exception(err)
            self.notify(err=err, mensagem="%s criar" % self.__class__.__name__)

    def alterar(self):
        try:
            with transaction.atomic():
                log.info("Alterando afastamento do PASU...")
                ferias = FeriasAfastamento.objects.filter(
                    servidor=self.pasu.periodo_aquisitivo_servidor.servidor,
                    data_inicio=self.pasu.data_inicio,
                    data_prevista=self.pasu.data_prevista_fim,
                ).exclude(estado=CANCELADO)
                log.debug(" PASU %s" % self.pasu)
                log.debug(" INÍCIO %s" % DateUtils.date_to_str(self.pasu.data_inicio))
                log.debug(
                    " FIM(DO MOMENTO DA MARCAÇÃO) %s"
                    % DateUtils.date_to_str(self.pasu.data_prevista_fim)
                )
                log.debug(
                    " NOVO FIM(APÓS INTERRUPÇÃO) %s"
                    % DateUtils.date_to_str(self.pasu.data_fim)
                )
                log.debug(" PASU ESTADO %s " % self.pasu.get_estado_display())
                log.debug(" AFASTAMENTO ENCONTRADO %s" % ferias.count())
                if ferias.exists():
                    ferias = ferias.latest("pk")
                    log.debug(
                        " AFASTAMENTO ESTADO %s ALTERAÇÃO %s"
                        % (ferias.get_estado_display(), ferias.get_alteracao_display())
                    )
                    if self.pasu.estado == PASU_INTERROMPIDO:
                        ferias.data_fim = self.pasu.data_fim
                        ferias.alteracao = INTERRUPCAO
                    ferias.save()
                    log.info(
                        "Novo fim do afastamento %s e alteração para %s"
                        % (
                            DateUtils.date_to_str(self.pasu.data_fim),
                            ferias.get_alteracao_display(),
                        )
                    )
                    log.info("...sucesso!")
                else:
                    log.info("afastamento não encontrado")
        except Exception as err:
            log.exception(err)
            self.notify(err=err, mensagem="%s - alterar" % self.__class__.__name__)

    def apagar(self):
        try:
            with transaction.atomic():
                log.info("Cancelando afastamento do PASU...")
                ferias = FeriasAfastamento.objects.filter(
                    servidor=self.pasu.periodo_aquisitivo_servidor.servidor,
                    data_inicio=self.pasu.data_inicio,
                    data_prevista=self.pasu.data_prevista_fim,
                ).exclude(estado=CANCELADO)
                log.debug(" PASU %s" % self.pasu)
                log.debug(
                    " FIM(DO MOMENTO DA MARCAÇÃO) %s" % self.pasu.data_prevista_fim
                )
                log.debug(
                    " NOVO FIM(APÓS INTERRUPÇÃO/SUSPENSÃO/NÃO AUTORIZADO) %s"
                    % self.pasu.data_fim
                )
                log.debug(" PASU ESTADO %s " % self.pasu.get_estado_display())
                log.debug(" AFASTAMENTO ENCONTRADO %s" % ferias.count())
                if ferias.exists():
                    ferias = ferias.latest("pk")
                    log.debug(
                        " AFASTAMENTO ESTADO %s ALTERAÇÃO %s"
                        % (ferias.get_estado_display(), ferias.get_alteracao_display())
                    )
                    ferias.alteracao = CANCELADO
                    ferias.alteracao = (
                        SUSPENSAO if self.pasu.estado == PASU_SUSPENSO else CANCELADO
                    )
                    ferias.save()
                    log.info(
                        "Novo fim do afastamento %s e alteração para %s"
                        % (
                            DateUtils.date_to_str(self.pasu.data_fim),
                            ferias.get_alteracao_display(),
                        )
                    )
                    log.info("...sucesso!")
        except Exception as err:
            log.exception(err)
            self.notify(err=err, mensagem="%s apagar" % self.__class__.__name__)

    def notify(self, err=None, mensagem=None):
        employees = []
        if self.pasu.pas.servidor.membro:
            employees = Servidor.objects.filter(
                user__groups__name__icontains="expediente-afastamento"
            )
        else:
            employees = Servidor.objects.filter(
                user__groups__name__icontains="rh-afastamento"
            )
        send_mail_and_notify(
            source="ERRO EM %s" % self.__class__.__name__,
            message="Afastamento Férias (%s) NÃO FOI CRIADO -> %s"
            % (self.pasu.pas.servidor, err),
            err=err,
            employee=employees,
        )


@receiver(post_save, sender=PeriodoAquisitivoServidorUsufruto)
def afastamento_pasu(sender, instance, **kargs):
    GerenciaAfastamentoFeriasPasu(pasu=instance)


@receiver(post_delete, sender=PeriodoAquisitivoServidorUsufruto)
def afastamento_pasu_apagar(sender, instance, **kargs):
    GerenciaAfastamentoFeriasPasu(pasu=instance, apagar=True)
