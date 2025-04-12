# -*- coding: utf-8 -*-

from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.gfp.models import IRRF, Evento, FolhaEvento
from rh.pensao.models import PensaoFolhaEvento, PensaoMorteEvento

log = getLogger(__name__)


# @receiver(post_save, sender = PensaoAlimenticiaEvento)
@receiver(post_save, sender=PensaoMorteEvento)
def post_pensao_evento_save(sender, instance, **kargs):
    pensao = (
        instance.pensao_morte
        if sender == PensaoMorteEvento
        else instance.pensao_alimenticia
    )
    lancamentos = FolhaEvento.objects.filter(
        evento=instance.evento, servidor=pensao.servidor
    ).exclude(folha__status=3)

    for lancamento in lancamentos:
        try:
            pfe = lancamento.origem_pensao.get(pensao=pensao)
        except Exception as e:
            pfe = PensaoFolhaEvento(pensao=pensao, folha_evento=lancamento)

            log.exception(e)
        finally:
            pfe.valor = "%.2f" % instance.apply_to_value(lancamento.valor)
            pfe.save()


# @receiver(pre_delete, sender = PensaoAlimenticiaEvento)
@receiver(pre_delete, sender=PensaoMorteEvento)
def pre_pensao_evento_delete(sender, instance, **kargs):
    pensao = (
        instance.pensao_morte
        if sender == PensaoMorteEvento
        else instance.pensao_alimenticia
    )
    lancamentos = FolhaEvento.objects.filter(
        evento=instance.evento, servidor=pensao.servidor
    ).exclude(folha__status=3)

    for lancamento in lancamentos:
        try:
            pfe = lancamento.origem_pensao.get(pensao=pensao)
        except Exception:
            pass
        else:
            pfe.delete()


# @receiver(post_save, sender = PensaoFolhaEvento)
# @receiver(post_delete, sender = PensaoFolhaEvento)
def post_save_pensaofolhaevento_irrf(sender, instance, **kargs):
    eventos = {
        "P": Evento.objects.filter(aplica_irrf=True, tipo="P"),
        "D": Evento.objects.filter(aplica_irrf=True, tipo="D"),
    }

    if instance.evento.numero != "9999":

        proventos = float(
            PensaoFolhaEvento.objects.filter(
                pensao=instance.pensao,
                folha=instance.folha,
                evento__in=eventos.get("P", []),
            )
            .aggregate(total=Sum("valor"))
            .get("total")
            or 0.00
        )

        despesas = float(
            PensaoFolhaEvento.objects.filter(
                pensao=instance.pensao,
                folha=instance.folha,
                evento__in=eventos.get("D", []),
            )
            .aggregate(total=Sum("valor"))
            .get("total")
            or 0.00
        )

        try:
            irrf = IRRF.objects.filter(
                data_vigencia__lte=instance.folha.dt_pagamento
            ).order_by("-data_vigencia")[0]
        except Exception as e:
            log.exception(e)
        else:
            valor_base = proventos - despesas
            faixas = irrf.faixas.filter(
                limite_inferior__lte=valor_base, limite_superior__gte=valor_base
            )

            if faixas.exists():
                faixa = faixas.get()

                aliquota = float(faixa.percentual or 0.00)
                deducao = float(faixa.desconto or 0.00)
                dependente = float(irrf.valor_dependente or 0.00)
                numero_depentene = 0
                valor = round(
                    (valor_base - (deducao + round(dependente * numero_depentene, 2)))
                    * (aliquota / 100.0),
                    2,
                )
                try:
                    pfe = PensaoFolhaEvento.objects.get(
                        pensao=instance.pensao,
                        folha=instance.folha,
                        evento__numero="9999",
                    )
                    log.info("Encontrado Pensao Folha Evento")
                except PensaoFolhaEvento.DoesNotExist:
                    pfe = PensaoFolhaEvento(
                        pensao=instance.pensao,
                        folha=instance.folha,
                        evento=Evento.objects.get(numero="9999"),
                    )
                    log.info("Criar Pensao Folha Evento")
                finally:
                    pfe.pct = aliquota
                    pfe.valor_base = valor_base
                    pfe.valor = valor
                    pfe.save()
            else:
                log.info("Isento do imposto")
                try:
                    pfe = PensaoFolhaEvento.objects.get(
                        pensao=instance.pensao,
                        folha=instance.folha,
                        evento__numero="9999",
                    )
                    log.info("Encontrado Pensao Folha Evento")
                except Exception:
                    pass
                else:
                    pfe.delete()
