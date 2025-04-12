from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


from rh.dayoff.models import Usufruct
from rh.afastamento.utils.afastamento_usufruto import criar_afastamento_usufruto

from standard.models import Item

log = getLogger(__name__)


class Command(BaseCommand):
    help = """

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
        self.set_user_to_job("job_athenas_gerar_afastamento_usufruto_ferramenta")
        self.criar_afastamentos()

    def buscar_usufrutos(self):
        item_config = Item.objects.get(key="LISTA_USUFRUTO_AFASTAMENTO")

        lista_ids = item_config.value.split(";") if item_config.value else []

        usufrutos = Usufruct.objects.filter(id__in=lista_ids)

        return usufrutos

    def criar_afastamentos(self):

        log.info(f"iniciando o job/serviço gerar_afastamento_usufruto_ferramenta")

        usufrutos = self.buscar_usufrutos()

        for usufruto in usufrutos:
            try:
                log.info(f"Criando Afastamento pelo usufruto: {usufruto}")
                print(f"Criando Afastamento pelo usufruto: {usufruto}")

                criar_afastamento_usufruto(usufruto)

            except Exception as e:
                print(f"{e}")
                log.error(f"{e}")
