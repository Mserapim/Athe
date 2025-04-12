from django.db import transaction
from django.dispatch import receiver

# from adm.diarias.models import Solicitacao as Daily
# from adm.diarias.signals.custom import access_control_signal
# from common.document_access.models import ControlType, DailyControl
from contrib.middleware import get_current_user
from contrib.utils import getLogger, person_from_user


log = getLogger()
log_prefix = "[document_access]"


# def _classify_daily(daily, control_type, legal_prerogative, justification):
#     log.info(f'{log_prefix} Classifying Daily: {daily.codigo}')#

#     control, created = DailyControl.classify(
#         document=daily,
#         control_type=control_type,
#         legal_prerogative=legal_prerogative,
#         justification=justification
#     )#

# def _reclassify_daily(daily, control_type, legal_prerogative, justification):
#     log.info(f'{log_prefix} Reclassifying Daily: {daily.codigo}')#

#     control = daily.control#

#     # Somente reclassifica se o nível de acesso fornecido for diferente do atual.
#     if control.control_type != control_type:
#         with transaction.atomic():
#             control.reclassify(
#                 control_type=control_type,
#                 legal_prerogative=legal_prerogative,
#                 justification=justification
#             )#
#

# @receiver(access_control_signal, sender=Daily)
# def daily_access_control(sender, daily, control_type, legal_prerogative, justification, **kwargs):
#     # Se já tem controle de acesso, reclassifica. Senão, classifica.
#     if daily.control:
#         _reclassify_daily(
#             daily=daily,
#             control_type=control_type,
#             legal_prerogative=legal_prerogative,
#             justification=justification
#         )
#     else:
#         _classify_daily(
#             daily=daily,
#             control_type=control_type,
#             legal_prerogative=legal_prerogative,
#             justification=justification
#         )
