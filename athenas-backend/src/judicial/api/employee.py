from rh.api.employee import RHEmployeeRestful
from rh.models import Servidor
from contrib.middleware import get_current_user
from contrib.utils import getLogger

log = getLogger(__name__)


class EJudEmployeeRestful(RHEmployeeRestful):

    def get_query(self):
        query = super(EJudEmployeeRestful, self).get_query()
        user = get_current_user()

        if not user.has_perm("judicial.outcourtlawsuitadmin"):
            if user.servidor.tipo == "M":
                query = query.filter(pk=user.servidor.pk)
            else:
                query = query.filter(
                    pk__in=Servidor.objects.filter(
                        tipo="M",
                        servidor_lotacao__designacao=True,
                        servidor_lotacao__lotacao__in=user.servidor.work_locations.all(),
                    )
                )

        return query


class RHSubordinateRestful(RHEmployeeRestful):

    def get_query(self):
        query = super(RHSubordinateRestful, self).get_query()
        user = get_current_user()
        if not user.has_perm("judicial.outcourtlawsuitadmin"):
            if user.servidor:
                query = query.exclude(tipo="M")
                query = query.filter(pk=user.servidor.pk)
                subordinates = user.servidor.subordinados.all()
                if subordinates.exists():
                    query |= subordinates
            else:
                query = []

        return query

    def model_to_dict(self, instance):
        params = super(RHSubordinateRestful, self).model_to_dict(instance)
        unicode = "{} - {}".format(instance.pessoa_fisica.nome, "ATIVO")
        if not instance.ativo:
            unicode = "{} - {}".format(instance.pessoa_fisica.nome, "INATIVO")
        params.update({"pessoa_fisica_unicode": unicode})
        return params
