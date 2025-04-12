# from dateutil.relativedelta import relativedelta
from django.db.models import Max, Q

from contrib.decorator import cache_return
from contrib.utils import getLogger
from standard.models import Choice, RunCodeManager

from rh.gfp.calcs.mpmt.base import BaseCalculation

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpmt-eventualprovider")
class EventualProvider(BaseCalculation):
    title = "Calculo de valor do Prestador de Serviços (Colaborador Eventual - COE)"

    PARAMS_ = ["info", "oIds", "base_value"]

    def validate_type_by_possession(self):
        if self.employee.type_by_possession not in ["COE"]:
            raise self.CalculationNotApplicable(
                "Essa verba é somente para COE (Colaborador Eventual)!"
            )

    def validate(self):
        self.validate_type_by_possession()

    def value(self):
        return self.base_value()

    def quantity(self):
        return self.maximum_quantity()


@RunCodeManager.register("gfp-mpmt-eventualproviderinss")
class EventualProviderINSS(BaseCalculation):
    title = "Calculo de INSS do Prestador de Serviços (Colaborador Eventual - COE)"

    PARAMS_ = ["info", "oIds", "base_value"]

    def validate_type_by_possession(self):
        if self.employee.type_by_possession not in ["COE"]:
            raise self.CalculationNotApplicable(
                "Essa verba é somente para COE (Colaborador Eventual)!"
            )

    def validate(self):
        self.validate_type_by_possession()
