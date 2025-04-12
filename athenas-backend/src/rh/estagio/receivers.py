# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.afastamento.models import (
    AfastamentoCursoConcurso,
    AfastamentoMandatoEletivo,
    AfastamentoOutroOrgao,
    AfastamentoPrisao,
    LicencaAdocao,
    LicencaAfastamentoConjuge,
    LicencaAtividadePolitica,
    LicencaDoencaPessoaFamilia,
    LicencaMandatoClassista,
    LicencaSaudeJuntaMedica,
    LicencaServicoMilitar,
)
from rh.estagio.models import Configuracao, EstagioAvaliacao, EstagioProbatorioServidor
from rh.models import (
    MovimentacaoAposentadoria,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    Quadro,
)

log = getLogger(__name__)


@receiver(post_save, sender=MovimentacaoPosse)
def signals_estagio_movimentacao_posse(sender, instance=None, **kargs):
    try:
        if instance.servidor.type_by_possession in ["EFE", "ECM", "EFC"]:
            log.debug(
                ">>> GESTOR DE ESTAGIO PROBATORIO >>>>>>>>>>>>> %s:%s:%s"
                % (
                    instance.quadro.cargo.tipo_lei_cargo if instance.quadro else "",
                    instance.ativo,
                    instance.servidor.tipo,
                )
            )
            configs = Configuracao.objects.filter(
                Q(data_inicio__lte=instance.data_exercicio)
                & (Q(data_fim=None) | Q(data_fim__gte=instance.data_exercicio))
            )

            if configs:
                with transaction.atomic():
                    config = configs[0]
                    created = False
                    estagio_probatorio_servidor = None
                    if (
                        instance.quadro.cargo.tipo_lei_cargo == "EF"
                        and instance.ativo is True
                        and instance.servidor.tipo == "S"
                    ):
                        estagio_probatorio_servidor, created = (
                            EstagioProbatorioServidor.objects.get_or_create(
                                posse_servidor=instance, configuracao=config
                            )
                        )
                    # se nao tiver no estagio_probatorio_servidor ainda, então cria
                    if created:
                        estagio_probatorio_servidor.proxima_avaliacao = (
                            estagio_probatorio_servidor.next_evaluation(
                                instance.data_exercicio
                            )
                        )
                        estagio_probatorio_servidor.configuracao = config
                        estagio_probatorio_servidor.fim_estagio = (
                            estagio_probatorio_servidor.get_fim_estagio()
                        )
                        estagio_probatorio_servidor.save()
                        log.info("Criou dados de  %s no gestor de estagio: " % instance)

                    # se já tiver o servidor no estagio_probatorio_servidor entao atualiza os dados
                    elif estagio_probatorio_servidor:
                        if not EstagioAvaliacao.objects.filter(
                            avaliado=estagio_probatorio_servidor
                        ).count():
                            estagio_probatorio_servidor.proxima_avaliacao = (
                                estagio_probatorio_servidor.next_evaluation(
                                    instance.data_exercicio
                                )
                            )
                            estagio_probatorio_servidor.fim_estagio = (
                                estagio_probatorio_servidor.get_fim_estagio()
                            )
                            estagio_probatorio_servidor.configuracao = config
                            estagio_probatorio_servidor.save()
                            log.info("Atualizando servidor %s" % instance)
                        else:
                            num_avaliacoes = EstagioAvaliacao.objects.filter(
                                avaliado=estagio_probatorio_servidor
                            ).count()
                            log.info(
                                "Servidor %s ja foi avaliado %d vez(es), nao é possivel alterar os dados"
                                % (instance, num_avaliacoes)
                            )
                    else:
                        log.info(
                            "Servidor %s não possui estágio probatório." % instance
                        )

            else:
                log.info(
                    "Erro! A data de exercicio é menor que a das configuracoes existentes"
                )

    except Exception as err:
        log.exception(err)


@receiver(post_save, sender=MovimentacaoDesligamento)
@receiver(post_save, sender=MovimentacaoAposentadoria)
def signals_estagio_movimentacao_desligamento(sender, instance=None, **kargs):
    try:
        if not instance.servidor.membro and instance.servidor.type_by_possession in [
            "EFE",
            "ECM",
            "EFC",
        ]:
            with transaction.atomic():
                log.info(
                    ">>> DESLIGAMENTO EM GESTOR DE ESTÁGIO PROBATÓRIO >>>>>>>>>>>>>"
                )
                eps = EstagioProbatorioServidor.objects.get(
                    posse_servidor=instance.movimentacao_posse
                )
                if not eps.is_finalized:
                    log.info(
                        "O servidor: %s foi desligado do cargo. Alterando status no gestor de estágio probatório"
                        % eps
                    )
                    eps.status = 4
                    eps.bloqueada = True
                    eps.proxima_avaliacao = None
                    eps.save()
                else:
                    log.info("Estagio do servidor: %s ja foi finalizado" % eps)
    except EstagioProbatorioServidor.DoesNotExist as err:
        pass
    except Exception as err:
        log.exception(err)


@receiver(post_save, sender=LicencaSaudeJuntaMedica)
@receiver(post_save, sender=LicencaDoencaPessoaFamilia)
@receiver(post_save, sender=LicencaAfastamentoConjuge)
@receiver(post_save, sender=LicencaServicoMilitar)
@receiver(post_save, sender=AfastamentoOutroOrgao)
@receiver(post_save, sender=AfastamentoMandatoEletivo)
@receiver(post_save, sender=AfastamentoCursoConcurso)
@receiver(post_save, sender=AfastamentoPrisao)
@receiver(post_save, sender=LicencaAtividadePolitica)
@receiver(post_save, sender=LicencaMandatoClassista)
@receiver(post_save, sender=LicencaAdocao)
def signal_post_save_afastamento(sender, instance=None, **kargs):
    """
    Comando para atualizar a propriedade ativo de cada servidor.
    Utiliza-se is_ativo, pois ele baseia-se na data de exercício.
    """
    log.info(
        ">>>>>>>>>>>>>>>>> RECALCULANDO SUPENSOES DO ESTAGIO <<<<<<<<<<<<<<<<<<<<<<"
    )
    try:
        if not instance.servidor.membro and instance.servidor.type_by_possession in [
            "EFE",
            "ECM",
            "EFC",
        ]:
            with transaction.atomic():
                posse = instance.servidor.posses_ativas.get(
                    quadro__cargo__tipo_lei_cargo="EF"
                )
                estagio_servidor = EstagioProbatorioServidor.objects.get(
                    posse_servidor=posse, status=1
                )
                estagio_servidor.calcula_suspensao_save_afastamentos()
    except EstagioProbatorioServidor.DoesNotExist:
        log.info(
            "Servidor %s não possui dados em estágio probatório." % instance.servidor
        )
    except Exception as err:
        log.exception(err)
