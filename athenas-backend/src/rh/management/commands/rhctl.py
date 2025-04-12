from contrib.middleware import current_request
from django.core.management.base import BaseCommand
from django.db.models import Q
from rh.models import (
    NaturalPersonHistory,
    PessoaFisica,
    PessoaJuridica,
    Pessoa,
    RepeatPersonIncident,
    ServidorLocalizacao,
    ServidorLotacao,
    DeclaracaoAtividade,
)


class SubCommand(object):
    name = "undefined"
    help = "undefined"

    def add_arguments(self, parser):
        pass


class Command(BaseCommand):
    help = "Gestor de comandos do subsistema de Recursos Humanos"

    __subcommands = {}

    @classmethod
    def register(cls):
        def __wrapper(CommandClass):
            cls.__subcommands.update({CommandClass.name: CommandClass})
            return CommandClass

        return __wrapper

    def add_arguments(self, parser):
        sp = parser.add_subparsers(help="Sub comandos do rhctl", dest="command")

        for name, CommandClass in self.__subcommands.items():
            p = sp.add_parser(name, help=CommandClass.help)
            sc = CommandClass()
            sc.add_arguments(p)

    def handle(self, command, *args, **kwargs):
        if command and command in self.__subcommands:
            sc = self.__subcommands.get(command)()
            sc.handle(*args, **kwargs)
        else:
            print("O comando desejado não é reconhecido.")


@Command.register()
class ScanCommand(SubCommand):
    name = "repeat-scan"
    help = "Busca por pessoas que estejam repetidas na base de dados"

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--clear",
            help="Limpa todos os incidentens que estjam marcados como pendentes",
            dest="clear",
            action="store_true",
        )

        return parser

    def handle(self, clear=False, *args, **kwargs):
        scopes = (
            (PessoaFisica, "Procurado pessoas físicas repetidas ..."),
            (PessoaJuridica, "Procurado pessoas físicas repetidas ..."),
            # (Pessoa, 'Procurado pessoas comum repetidas ...'),
        )

        if clear:
            print("Limpando incidentes pententes")
            RepeatPersonIncident.objects.filter(current_state=1).delete()

        print("Classificando repetições")
        for Person, header in scopes:
            print(header, end="")

            query = Person.objects.order_by("phonetic_name", "-rate_fill")
            total = query.count()
            current = 0
            message = ""

            for person in query:
                print("\b" * len(message), end="")
                current += 1
                message = f" ({current} de {total})"
                print(message, end="")
                person.index_repeated()
            else:
                print("\b" * len(message), end="")
                print(" " * len(message), end="")
                print("\b" * len(message), end="")

                print(" (PRONTO) ")


@Command.register()
class ScanCommand(SubCommand):
    name = "rate-fill"
    help = "Atualiza a taxa de preenchimento das pessoas no banco de dados"

    def handle(self, clear=False, *args, **kwargs):
        scopes = (
            (PessoaFisica, "Atualizando pessoas fisicas ..."),
            (PessoaJuridica, "Atualizando pessoas juridicas ..."),
        )

        print("Atualizando...")
        for Person, header in scopes:
            print(header, end="")

            query = Person.objects.order_by("phonetic_name", "-rate_fill")
            total = query.count()
            current = 0
            message = ""

            for person in query:
                print("\b" * len(message), end="")
                current += 1
                message = f" ({current} de {total})"
                print(message, end="")
                Person.objects.filter(pk=person.pk).update(
                    rate_fill=person._calculate_rate_fill()
                )
            else:
                print("\b" * len(message), end="")
                print(" " * len(message), end="")
                print("\b" * len(message), end="")

                print(" (PRONTO) ")


@Command.register()
class MainScheduleEmployeeWorkplace(SubCommand):
    name = "main-schedule-date"
    help = "Atualiza todas lotação/exercício com main_schedule_date preenchida."

    def handle(self, clear=False, *args, **kwargs):
        ServidorLotacao.cmd_main_schedule_date()


@Command.register()
class MainScheduleActivityStatement(SubCommand):
    name = "main-schedule-date-activity-statement"
    help = "Atualiza todas declaração de atividade com main_schedule_date preenchida."

    def handle(self, clear=False, *args, **kwargs):
        DeclaracaoAtividade.cmd_main_schedule_date()


@Command.register()
class CreateNaturalPersonHistory(SubCommand):
    name = "create-naturalpersonhistory-dependence"
    help = "Cria NaturalPersonHistory (Histórico da pessoa física) a partir de Dependencia de Dependente."

    def handle(self, clear=False, *args, **kwargs):
        self.create_history_dependence()

    def create_history_dependence(self):
        NaturalPersonHistory.cmd_create_history_dependence()
