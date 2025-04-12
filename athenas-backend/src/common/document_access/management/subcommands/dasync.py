from datetime import datetime
from importlib import import_module

from common.document_access.management.commands.dactl import (
    Command as CommandController,
)
from common.document_access.models import ControlType
from contrib.middleware import set_current_user
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


class AbstractDASync(object):
    """Classe Abstrata para Sync de Acesso a Documento.
    Essa classe serve de gateway para aqueles que forem implementar a sincronização
    de dados de Acesso a Documento para cada classe que tratar deste tipo de controle.
    """

    def activate_athenas_user(self):
        """Define (se possível) o usuário athenas.
        Define, caso exista, o usuário athenas como o usuário a praticar as ações do comando.
        """

        try:
            user = User.objects.get(username="athenas")
        except User.DoesNotExist as e:
            raise e
        else:
            set_current_user(user)

    def handle(self):
        raise Exception("not implemented")


@CommandController.register("sync")
class Command(object):

    help = """Este comando é responsável por executar rotinas de sincronização do modulo de acesso a documento."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--target",
            dest="target",
            help="Executa a ação de sincronização para UM contexto.",
        )

        parser.add_argument(
            "-a",
            "--all-targets",
            action="store_true",
            dest="all_targets",
            help="Executa a ação de sincronização para TODOS contextos.",
        )

        parser.add_argument(
            "-l",
            "--list-targets",
            action="store_true",
            dest="list_targets",
            help="LISTA todas os contextos de controle de acesso a documento.",
        )

        parser.add_argument(
            "-c",
            "--control-type",
            dest="control_type",
            help="Define o CONTROLE DE TIPO padrão a ser usado na sincronização.",
        )

        parser.add_argument(
            "--list-control-types",
            action="store_true",
            dest="list_control_types",
            help="LISTA todas os tipos de controle que podem ser usados como padrão na sincronização.",
        )

        parser.add_argument(
            "--list-prerogatives",
            action="store_true",
            dest="list_prerogatives",
            help="LISTA todas as prerrogativas para um tipo de controle que podem ser usados como padrão na sincronização.",
        )

        parser.add_argument(
            "--legal-prerogative",
            dest="legal_prerrogative",
            help="Prerrogativa legal a ser utilizada na sincronização.",
        )

        parser.add_argument(
            "-b",
            "--begin",
            dest="begin",
            help="Define o INÍCIO do período. Formato 'aaaammdd'",
        )

        parser.add_argument(
            "-e",
            "--end",
            dest="end",
            help="Define o FIM do período. Formato 'aaaammdd'",
        )

        parser.add_argument(
            "-j",
            "--justification",
            dest="justification",
            help="Justificativa para a classificação do documento",
        )

    def invalid_parameter(self):
        """
        É disparada como mensagem padrão quando nenhum parâmetro válido foi informado ao comando.
        """

        print(
            "Informe um parâmetro válido.\n"
            "Para mais informações sobre este comando, use '-h' ou '--help' como parâmetro.\n"
        )

    def handle_target(self, options):
        """
        Sincroniza dados de controle de acesso a documentos.
        O argumento target recebe o nome da classe de controle no qual será feito a sincronização.
        É possível informar em intervalo aberto ou fechado (begin/end) um período de tempo para ser
        realizada esta ação.
        """

        try:
            module_path = getattr(settings, "DOCUMENT_ACCESS_TARGET_CLASSES").get(
                options.get("target")
            )
            module = import_module(module_path)

            criteria = Q()
            if options.get("begin"):
                criteria.add(
                    Q(
                        data_criacao__gte=datetime.strptime(
                            options.get("begin"), "%Y%m%d"
                        )
                    ),
                    "AND",
                )
            if options.get("end"):
                criteria.add(
                    Q(
                        data_criacao__lte=datetime.strptime(
                            options.get("end"), "%Y%m%d"
                        )
                    ),
                    "AND",
                )
            if criteria:
                options.update({"criteria": criteria})

            if options.get("control_type"):  # Tipo de Controle informado pelo usuário
                options.update({"control_type": Q(pk=options.get("control_type"))})
            else:  # Tipo de Controle padrão
                options.update(
                    {"control_type": Q(is_secret=False, title__icontains="Restrito")}
                )

            module.dasync.Driver().handle(options)
        except Exception as e:
            print(e)

    def list_targets(self):
        """
        Lista os nomes dos modelos (alvos) que podem ser informados como parâmetro,
        bem como uma descrição breve do que se trata cada modelo.
        """

        for name, module_path in getattr(
            settings, "DOCUMENT_ACCESS_TARGET_CLASSES"
        ).items():
            try:
                module = import_module(module_path)
                print("%-20s%s" % (name, module.dasync.Driver.__doc__))
            except Exception as e:
                print(e)
        print("\n")

    def list_control_types(self):
        """
        Lista os tipos de controle que podem ser usados como padrão no ato da sincronização
        """

        for ct in ControlType.objects.all():
            print("{} - {}".format(ct.pk, ct.title))

    def list_legal_prerogatives(self, control_type_id):
        """
        Lista as prerrogativas legais do tipo de controle que podem ser usados como padrão no ato da sincronização
        """
        ct = ControlType.objects.get(pk=control_type_id)
        for prerogative in ct.prerogatives.all():
            print(" - ".join([str(prerogative.pk), str(prerogative)]))

    def handle(self, *args, **options):
        """
        Este gateway de sincronização trata qual rota o comando tomará ao receber
        dos parâmetros o(s) alvo(s) e assim repassar a tarefa para aquele que,
        de fato, lidará com a tarefa.
        """

        if options.get("target"):  # Se for informado um alvo válido
            self.handle_target(options)
        elif options.get(
            "all_targets"
        ):  # Se for informado que todos os alvos serão considerados
            for target in getattr(settings, "DOCUMENT_ACCESS_TARGET_CLASSES").keys():
                copied_options = dict(options)
                copied_options.update({"target": target})
                self.handle_target(copied_options)
        elif options.get(
            "list_targets"
        ):  # Se for solicitada a listagem dos alvos válidos
            self.list_targets()
        elif options.get("list_control_types"):
            self.list_control_types()
        elif options.get("list_prerogatives"):
            control_type = options.get("control_type", None)
            if not control_type:
                print(
                    "Use o -c para indicar o tipo de controle a ser ver as prerrogativas dele."
                )
            else:
                self.list_legal_prerogatives(control_type)
        else:  # Se não ocorrer nenhuma das opções anteriores
            self.invalid_parameter()
