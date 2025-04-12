from rh.api.workplace import RHWorkplaceRestful
from contrib.middleware import get_current_user
from contrib.utils import getLogger

log = getLogger(__name__)


class SACIWorkplaceRestful(RHWorkplaceRestful):

    def get_query(self):
        query = super(SACIWorkplaceRestful, self).get_query()
        user = get_current_user()

        if not user.has_perm("saci.can_generate_reports_all_location"):
            if user.servidor.tipo == "M":
                query = query.filter(
                    pk__in=user.servidor._raw_locations().values_list(
                        "lotacao", flat=True
                    )
                )
            else:
                query = query.filter(pk__in=user.servidor.work_locations.all())

        return query
