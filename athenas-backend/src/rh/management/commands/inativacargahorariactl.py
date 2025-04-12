from datetime import date, timedelta, datetime

from contrib.middleware import set_current_user
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from contrib.utils import getLogger

from rh.models import CargaHoraria, MovimentacaoPosse


log = getLogger(__name__)


class Command(BaseCommand):
    help = """Esse Comando irá inativar a Carga Horário dos Servidores que tiveram a Movimentação
    de Posse desligada, se o Servidor possuir mais de uma Posse ativa a carga Horária não será inativada.
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
        self.set_user_to_job("job_inativa_carga_horaria")
        self.inativa_carga_horaria()

    def busca_servidores_desligados(self):
        """Busca Servidores que tiveram a Movimentação Posse desligada."""
        dia_anterior = date.today() - timedelta(1)

        if dia_anterior < date(2024, 2, 29):
            query = (
                MovimentacaoPosse.objects.filter(data_desligamento__isnull=False)
                .distinct("servidor")
                .values_list("servidor__pk", flat=True)
            )
        else:
            query = (
                MovimentacaoPosse.objects.filter(data_desligamento=dia_anterior)
                .distinct("servidor")
                .values_list("servidor__pk", flat=True)
            )
        for servidor in query:
            if (
                MovimentacaoPosse.objects.filter(
                    servidor__pk=servidor, ativo=True
                ).count()
                >= 1
            ):
                """Se o Servidor possuir mais Posse(s) ativa(s) a carga Horária não será inativada."""
                query = query.exclude(servidor=servidor)

        return query

    def inativa_carga_horaria(self):
        log.info(f"Iniciando inativação de Carga Horária | {datetime.now()}")
        print(f"Iniciando inativação de Carga Horária | {datetime.now()}")
        servidores = self.busca_servidores_desligados()
        for serv in servidores:
            query = CargaHoraria.objects.filter(servidor=serv, active=True)
            if query.exists():
                """Inativa sem passar pelo save() e validate()"""
                mov_posse = (
                    MovimentacaoPosse.objects.filter(
                        servidor=serv, data_desligamento__isnull=False
                    )
                    .order_by("data_desligamento")
                    .last()
                )
                log.info(f">>> Carga(s) Horária(s) inativada(s): {query} <<<")
                query.update(active=False, data_fim=mov_posse.data_desligamento)
        log.info(f"Finalizando inativação de Carga Horária | {datetime.now()}")
        print(f"Finalizando inativação de Carga Horária | {datetime.now()}")
