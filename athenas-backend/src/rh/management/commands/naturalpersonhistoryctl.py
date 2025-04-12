from django.core.management.base import BaseCommand
from django.db.models import Q
from rh.models import NaturalPersonHistory


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
class CreateNaturalPersonHistory(SubCommand):
    name = "create-naturalpersonhistory-dependence"
    help = "Cria NaturalPersonHistory (Histórico da pessoa física) a partir de Dependencia de Dependente."

    def handle(self, clear=False, *args, **kwargs):
        self.create_history_dependence()

    def create_history_dependence(self):
        NaturalPersonHistory.cmd_create_history_dependence()
