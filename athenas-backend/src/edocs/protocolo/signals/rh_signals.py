# -.- coding: utf-8 -.-
from rh.models import Lotacao, OrgaoGeral, UnidadeAdministrativa
from edocs.protocolo.task.rh_reference import generalorgan_update_reference
from engine.mq.models import Task
from django.dispatch import receiver
from django.db.models.signals import post_save
from contrib.utils import getLogger

log = getLogger(__name__)
