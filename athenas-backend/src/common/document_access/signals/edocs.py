# -*- encoding: utf-8 -*-

from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save

from common.document_access.models import ControlType, LegalPrerogative, ProtocolControl
from contrib.utils import getLogger
from edocs.protocolo.models import Protocolo as Protocol, Movimentacao as Movement
from edocs.protocolo.signals.custom import access_control_signal
from rh.models import Pessoa as Person


log = getLogger()
log_prefix = "[document_access]"


def _classify_protocol(
    protocol, control_type, justification, legal_prerogative, is_committed=True
):
    log.info(f"{log_prefix} Classifying EDOC Protocol: {protocol.codigo}")

    control, created = ProtocolControl.classify(
        document=protocol,
        control_type=control_type,
        legal_prerogative=legal_prerogative,
        justification=justification,
        is_committed=is_committed,
    )


def _reclassify_protocol(
    protocol, control_type, justification, legal_prerogative, is_committed=True
):
    log.info(f"{log_prefix} ReClassifying EDOC Protocol: {protocol.codigo}")

    control = protocol.protocol_control

    # Somente reclassifica se o nível de acesso fornecido for diferente do atual.
    if control.control_type != control_type:
        control.reclassify(
            control_type=control_type,
            legal_prerogative=legal_prerogative,
            justification=justification,
            is_committed=is_committed,
        )


@receiver(access_control_signal, sender=Protocol)
def protocol_access_control(
    sender,
    protocol,
    control_type_id,
    justification,
    legal_prerogative_id,
    is_committed=True,
    **kwargs,
):
    try:
        control_type = ControlType.objects.get(id=control_type_id)
    except ControlType.DoesNotExist:
        raise Exception("O Nível de Acesso fornecido não existe.")

    try:
        legal_prerogative = LegalPrerogative.objects.get(id=legal_prerogative_id)
    except LegalPrerogative.DoesNotExist:
        raise Exception("A Hipótese Legal fornecida não existe.")

    # Se já tem controle de acesso, reclassifica. Senão, classifica.
    if hasattr(protocol, "protocol_control"):
        _reclassify_protocol(
            protocol=protocol,
            control_type=control_type,
            legal_prerogative=legal_prerogative,
            justification=justification,
            is_committed=is_committed,
        )
    else:
        _classify_protocol(
            protocol=protocol,
            control_type=control_type,
            legal_prerogative=legal_prerogative,
            justification=justification,
            is_committed=is_committed,
        )


def _grant_destination_access(control, movement):
    if (
        control.control_type and control.control_type.is_secret
    ):  # Allowedlist é para classificações com grau de sigilo.
        if movement.destinatario:
            control.grant_person_access(movement.destinatario)

            log.info(
                "{} Destinatário '{}' adicionado na Allowedlist!".format(
                    log_prefix, movement.destinatario
                )
            )
        elif movement.lotacao_destino and hasattr(movement.lotacao_destino, "lotacao"):
            person = movement.lotacao_destino.lotacao.responsavel.pessoa_fisica
            control.grant_person_access(person)

            log.info(
                "{} Responsável '{}' pela lotação '{}' adicionado na Allowedlist!".format(
                    log_prefix, person, movement.lotacao_destino.sigla
                )
            )


@receiver(post_save, sender=Movement)
def post_movement(sender, **kwargs):
    movement = kwargs.get("instance")

    if movement.passo > 0 and movement.protocolo.my_origin.control:
        control = movement.protocolo.my_origin.control
        control.commit()
        _grant_destination_access(control, movement)
