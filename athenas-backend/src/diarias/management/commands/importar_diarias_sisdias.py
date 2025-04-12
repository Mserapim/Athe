from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from diarias.utils.importacao_sisdias import importar_dados
from diarias.utils.importacao_sisdias_api import importar_dados_sisdias


log = getLogger(__name__)


class Command(BaseCommand):
    help = """Esse Comando irá disparar emails para os benficiarios que possuem prestaçãop de contas para serem enviadas
      utilizando o modelo de emails.
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("athenas_diarias")
        self.importar_diarias()

    def importar_diarias(self):
        importar_dados_sisdias()
