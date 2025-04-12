# -.- coding: utf-8 -.-


from contrib.utils import getLogger
from esocial.extractors.base import Extractor
from esocial.models import WorkHourInterval

log = getLogger(__name__)


class WorkHourIntervalExtractor(Extractor):

    EXTRACTED_CLASS = WorkHourInterval
    INTERNAL = True

    def validate_validity_fields(self):
        pass

    def horario_intervalo_tp_interv(self):
        return self._instance_outside.type_interval

    def horario_intervalo_dur_interv(self):
        return self._instance_outside.duration

    def horario_intervalo_ini_interv(self):
        return self._instance_outside.time_start

    def horario_intervalo_term_interv(self):
        return self._instance_outside.time_end
