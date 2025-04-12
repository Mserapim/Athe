from datetime import datetime
from django.db import transaction
from contrib.middleware import set_current_user
from common.document_access.management.commands.dactl import (
    Command as CommandController,
)
from common.document_access.models import Control


@CommandController.register("auto-declassify")
class Command(object):

    help = "Este comando avalia e desclassifica os controles de acesso que tenha sua data de termo final expirada."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            help="Somente simula a desclassificação",
            dest="dry_run",
            action="store_true",
        )

        return parser

    def handle(self, dry_run=False, *args, **kwargs):
        query = Control.objects.filter(final_term__lte=datetime.now())

        print("Desclassificando ...")
        count = 0
        set_current_user("athenas")

        for control in query:
            print(
                " -> Documento \033[1;33m%(number)s\033[0m que perder \033[1;33m%(lost)s\033[0m ... "
                % {
                    "number": control.document_number,
                    "lost": str(control.control_type),
                },
                end="",
            )

            if not dry_run:
                try:
                    with transaction.atomic():
                        control.my_origin.declassify(
                            justification="".join(
                                [
                                    "<p>",
                                    "Desclassificado automáticamente uma vez que o prazo estipulado no termo final, foi ultrapassdo"
                                    "</p>",
                                ]
                            )
                        )
                        count += 1
                        print("{\033[1;32mdone\033[0m}")
                except Exception as e:
                    print("{\033[1;31merror\033[0m}")
                    print(e)
            else:
                print("{\033[1;32mskip\033[0m}")

        print(f"Foram desclassificado {count} documento(s)")
