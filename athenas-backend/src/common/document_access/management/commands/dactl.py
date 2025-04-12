from django.core.management import BaseCommand
from argparse import ArgumentParser


class SubCommand(BaseCommand):

    def handle(self, *args, **kwargs):
        raise NotImplementedError(
            "subclasses of SubCommand must provide a handle() method"
        )


class Command(BaseCommand):

    subcommands = {}

    @classmethod
    def register(cls, name):
        def wrapper(subcommand):
            cls.subcommands.update({name: subcommand()})
            return subcommand

        return wrapper

    def add_arguments(self, parser):
        subparser = parser.add_subparsers(help="Sub commands", dest="command")

        for name, sub_command in self.subcommands.items():
            p = subparser.add_parser(name, help=sub_command.help)
            sub_command.add_arguments(p)

        return parser

    def handle(self, command, *args, **kwargs):
        if command:
            self.subcommands.get(command, _CommandNotFound()).handle(*args, **kwargs)


class _CommandNotFound(SubCommand):

    def handle(self, *args, **kwargs):
        print("Sub command not found in system")
