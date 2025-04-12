# -*- coding: utf-8 -*-
from common.document_access.management.subcommands.dasync import AbstractDASync
from common.document_access.models import ControlType, AttendanceControl

# from django.db.models import Q
from common.saci.models import Attendance


class Driver(AbstractDASync):
    """
    Implementação do driver para Atendimento ao Cidadão.
    """

    def handle(self, options):
        print("Executando sincronização para AttendanceControl ...")
        self.activate_athenas_user()

        control_type = ControlType.objects.get(options.get("control_type"))
        justification = options.get("justification")
        legal_prerogative = options.get("legal_prerogative")

        created_count = 0
        for document in Attendance.objects.filter(confidential=True):
            obj, created = AttendanceControl.classify(
                document=document,
                control_type=control_type,
                justification=justification,
                bypass_validation=True,
                legal_prerogative=legal_prerogative,
            )

            if created:
                created_count += 1

        print(
            "\nForam registrados {0} novos controles de acesso:".format(created_count)
        )
