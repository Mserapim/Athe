from django.core.management.base import BaseCommand, CommandError
from datetime import date
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from planejamento.contrato.models import AgreementAnnotation


class Command(BaseCommand):
    help = (
        "Sistema de Contratos - Enviando um edoc de notificação programados para hoje."
    )

    def handle(self, *args, **options):
        # Filtra as anotações programadas para ser enviadas hoje
        annots = AgreementAnnotation.objects.filter(
            schedule=True, schedule_date=date.today()
        )

        # Anda pelas anotações de hoje uma a uma
        for annot in annots:
            # Captura o usuário interessado (origem). O edoc exige isso
            # por haver a necessidade de um usuário corrente na chamada
            # da função docketing, que cria o edoc.
            user = User.objects.get(username=annot.created_by.username)
            set_current_user(user)

            # Cria e despacha o edoc
            annot.edoc_creating()

        self.stdout.write(f"\nEdocs enviados com sucesso.")
