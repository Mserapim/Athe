from rh.api.person import RHNaturalPersonRestful
from django.db.models import Q
from contrib.utils import getLogger

log = getLogger(__name__)


class ClinicalNaturalPerson(RHNaturalPersonRestful):

    def get_query(self, *args, **kwargs):
        return (
            super()
            .get_query(*args, **kwargs)
            .exclude(servidor=None, dependentes_pessoa=None)
        )
