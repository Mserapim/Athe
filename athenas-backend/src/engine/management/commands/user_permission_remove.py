# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db.models import Q
from engine.models import ControllerPermission
from contrib.utils import getLogger
from contrib.middleware import set_current_user

log = getLogger("db")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--remove",
            dest="remove",
            help="Remove as permissões do usuário do servidor inativo. Permanece apenas com o Básico.",
            action="store_true",
        )

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, mark_read=False, older=None, **kwargs):
        self.set_user_to_job("job_user_permission_remove_handle")
        for user in (
            User.objects.filter(
                Q(servidor__ativo=False)
                & Q(
                    Q(user_permissions__isnull=False)
                    | Q(groups__isnull=False)
                    | Q(controllerpermission__isnull=False)
                )
            )
            .distinct()
            .order_by("username")
        ):
            groups = user.groups.filter()
            permissions = user.user_permissions.filter()
            controller_permission = user.controllerpermission_set.filter()
            print("=> Usuário: {}".format(user))
            for g in groups.filter():
                print("Removendo grupo: {}".format(g))
                user.groups.remove(g)
            for p in permissions.filter():
                user.user_permissions.remove(p)
            for cp in controller_permission.filter():
                print("Removendo funcionalidade: {}".format(cp))
                user.controllerpermission_set.remove(cp)
