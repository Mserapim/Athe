# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import SocialSecurityEmployee

log = getLogger(__name__)


@receiver(post_save, sender=SocialSecurityEmployee)
@receiver(post_delete, sender=SocialSecurityEmployee)
def update_employee_social_security(sender, instance, **kargs):
    """
    Este sinal é responsável por atualizar as caches de regime previdenciario
    do servidor ao ter uma alteração de configuração.
    """
    employee = instance.employee
    employee.save()
    log.info(">>>>>>>>>>> SIGNAL social_security employee")
