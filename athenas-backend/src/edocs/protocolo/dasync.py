from common.document_access.management.subcommands.dasync import AbstractDASync
from common.document_access.models import ControlType, ProtocolControl
from django.db.models import Q
from edocs.protocolo.models import Protocolo as Protocol


class Driver(AbstractDASync):
    """
    Implementação do driver para Protocolo
    """

    def handle(self, options):
        print("Executando sincronização para ProtocolControl ...")
        self.activate_athenas_user()

        criteria = Q(sigiloso=True)

        if options.get("criteria"):
            criteria.add(options.get("criteria"), "AND")

        control_type = ControlType.objects.get(options.get("control_type"))
        justification = options.get("justification")
        legal_prerogative = options.get("legal_prerogative")

        created_count = 0
        for document in Protocol.objects.filter(criteria):
            obj, created = ProtocolControl.classify(
                document=document,
                control_type=control_type,
                justification=justification,
                legal_prerogative=legal_prerogative,
                bypass_validation=True,
            )

            if created:
                created_count += 1
        print(
            "\nForam registrados {0} novos controles de acesso:".format(created_count)
        )
