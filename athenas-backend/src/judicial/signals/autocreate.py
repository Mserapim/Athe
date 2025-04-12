# -*- coding: utf-8 -*-
"""
Estes sinais serão utilizados para criar processos automáticamente
"""
import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from edocs.protocolo.models import Movimentacao
from judicial.models import OutCourtLawsuit, Denunciation, Triage
from contrib.utils import getLogger
from standard.models import Configuration
from datetime import date, timedelta

log = getLogger(__name__)


@receiver(post_save, sender=Movimentacao)
def create_from_field_document(instance, created, **kargs):
    cfg = Configuration.get_or_create("ejud")
    especies = []

    try:
        especies = json.loads(cfg.get("autoCreateFor"))
        if (
            not instance.protocolo.out_court_lawsuits.exists()
            and instance.protocolo.tipo_documento.pk in especies
        ):
            log.info("É necessário cria um processo Extrajudicial.")
            try:
                lawsuit = OutCourtLawsuit(origin=instance.protocolo)
                lawsuit.title = instance.protocolo.assunto
                log.info(
                    "Fazendo cache de localização para %s", instance.lotacao_destino
                )
                lawsuit.location = instance.lotacao_destino.lotacao
                lawsuit.deadline_cache = date.today() + timedelta(
                    days=int(cfg.get("deadlineTriage") or 0)
                )
                lawsuit.save()
                log.info("Adicionado o documento de noticia de fato")
                denunciation = Denunciation(
                    protocol=instance.protocolo,
                    create_location=lawsuit.location,
                    lawsuit=lawsuit,
                )
                denunciation.save()
                log.info("Documento de noticia de fato criado com sucesso!")
                lawsuit.parts.add(Triage(create_location=lawsuit.location))
                log.info("Adicionado o documento inicial de triagem!")
            except Exception as e:
                log.exception(e)
        elif (
            instance.passo == 0
            and not instance.data_encaminhamento
            and instance.protocolo.tipo_documento.pk in especies
        ):
            log.info("Atualizando informações da denuncia.")
            denunciation = instance.protocolo.has_deunciation.get()
            denunciation.cache_rendered = None
            denunciation.save()
        else:
            log.info("Não é necessário criar processo Extrajudicial.")
    except Exception as e:
        log.exception(e)
