# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from contrib.utils import getLogger
from edocs.protocolo.models import GroupPerson, GroupGeneralOrgan
from contrib.middleware import get_current_user

log = getLogger(__name__)


@receiver(m2m_changed, sender=GroupPerson.persons.through)
def check_permission_for_group_person(sender, instance, action, **kwargs):
    user = get_current_user()
    instance.level_access = int(instance.level_access or 0)
    if instance.level_access == 1:
        if action in ("pre_add", "pre_remove", "pre_clear") and not user.has_perm(
            "protocolo.group_person_admin_global_distribution"
        ):
            raise Exception("Você não tem permissão para alterar uma lista global.")


@receiver(m2m_changed, sender=GroupGeneralOrgan.general_organ.through)
def check_permission_for_group_general_organ(sender, instance, action, **kwargs):
    user = get_current_user()
    instance.level_access = int(instance.level_access or 0)
    if instance.level_access == 1:
        if action in ("pre_add", "pre_remove", "pre_clear") and not user.has_perm(
            "protocolo.group_general_organ_admin_global_distribution"
        ):
            raise Exception("Você não tem permissão para alterar uma lista global.")
