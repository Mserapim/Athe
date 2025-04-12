from time import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from edocs.protocolo.models import Envelop
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger

log = getLogger("db")


def tsprint(*args, **kwargs):
    """Prints with timestamp"""

    print(f"[{timezone.now()}]", *args, **kwargs)


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "--recovery-envelop",
            help="Run this command to retrieve envelopes that could not be sent",
            action="store_true",
            dest="recovery_envelop",
        )

        parser.add_argument(
            "--dry-run",
            help="Only simulate run command",
            action="store_true",
            dest="dry_run",
        )

        return parser

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def _get_query(self):
        return (
            Envelop.objects.prefetch_related("destinations")
            .select_related("movement__protocolo")
            .exclude(destinations=None)
            .filter(
                delivery_state__in=(Envelop.PENDENT, Envelop.IN_DELIVERY),
                destinations__created_movement=None,
            )
        )

    def _handle_recovery_envelop(self, dry_run=False):
        query = self._get_query()

        if not query.exists():
            return

        msg = f"Foram encontrados {query.count()} envelopes não entregues."
        tsprint(msg)
        log.info(msg)

        for envelop in query:
            msg = (
                f"Despachando envelope -> pk: {envelop.pk}, "
                f"protocolo: {envelop.movement.protocolo.codigo}, "
                f"para {envelop.destinations.count()} destino(s)..."
            )
            tsprint(msg, end="")
            log.info(msg)

            s_time = time()
            envelop.dispatch(verbose=True)
            e_time = time()

            print(" %0.3f ms" % (e_time - s_time))

    def handle(self, recovery_envelop=False, dry_run=False, *args, **kwargs):
        if recovery_envelop:
            self.set_user_to_job("job_protocolctl_handle")
            self._handle_recovery_envelop(dry_run)
