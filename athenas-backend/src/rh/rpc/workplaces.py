import re
from django.db.models import Q

from contrib.controller import DefaultController
from contrib.utils import getLogger
from rh.models import Lotacao
from contrib.decorator import is_public


log = getLogger(__file__)


class ElectoralExercisesRPC(DefaultController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.response_format == "json":
            self.response["content-type"] = "text/javascript; charset=utf-8"

    @is_public()
    def list(self, args=[]):

        page = int(self.request.GET.get("page") or 1)
        length = int(self.request.GET.get("length") or 10)
        keyword = self.request.GET.get("keyword")

        query = Lotacao.objects.select_related("responsavel").filter(
            Q(electoral_zone=True)
            & Q(ativo=True)
            & Q(responsavel__ativo=True)
            & Q(responsavel__tipo="M")
        )

        if keyword:
            query = query.filter(
                Q(responsavel__pessoa_fisica__nome__icontains=keyword)
                | Q(nome__icontains=keyword)
                | Q(electoral_zone_coverage__icontains=keyword)
            )

        total = query.count() or "0"
        end = page * length
        start = end - length

        electoral_zone_list = [
            {
                "electoral_zone_promoter": (
                    electoral_zone.responsavel.pessoa_fisica.nome
                    if electoral_zone.responsavel
                    else ""
                ),
                "electoral_zone_name": electoral_zone.nome,
                "electoral_zone_number": electoral_zone.nome.split()[0],
                "electoral_zone_coverage": electoral_zone.electoral_zone_coverage.replace(
                    "'", "$(apostrophe)"
                ),
            }
            for electoral_zone in query
        ]

        # TODO: Ordenar e efetuar o slice ao executar a query
        electoral_zone_list_ordered = sorted(
            electoral_zone_list,
            key=lambda x: int(re.search(r"\d+", x["electoral_zone_number"]).group()),
            reverse=False,
        )

        self.render(
            {"total": total, "list": list(electoral_zone_list_ordered[start:end])}
        )
