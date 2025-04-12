# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from common.distribution.models import Distribution


log = getLogger(__name__)


class CDDistribution(RestfulDRY):

    _model = Distribution

    force_upper = False

    full_text_index = "title__icontains"

    def get_query(self, *args, **kwargs):
        query = super(CDDistribution, self).get_query(*args, **kwargs)
        employee = employee_from_user(self.request.user)

        if not employee:
            query = query.none()
        else:
            query = query.filter(origin__in=employee.work_locations_effective_exercise)

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.distribution.Manage")')

    def employee_locations(self, args=[]):
        result = {
            "success": False,
            "message": "Nothing made yet.",
            "count": 0,
            "collection": [],
        }

        try:
            employee = employee_from_user(self.request.user)
            if not employee:
                raise Exception(
                    "Não foi possível obter Origem. Servidor público não encontrado."
                )
        except Exception as e:
            result.update(message=str(e))
        else:
            result.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=employee.work_locations_effective_exercise.count(),
                collection=[
                    {"pk": wl.pk, "description": str(wl)}
                    for wl in employee.work_locations_effective_exercise
                ],
            )

        self.renderer(result)

    def _instances_from_params(self):
        src_distribution = self.get_params()["src_distribution"]
        dst_distribution = self.get_params()["dst_distribution"]

        try:
            source = self.Model.objects.get(pk=src_distribution)
        except self.Model.DoesNotExist:
            raise Exception(
                " ".join(
                    [
                        "Não foi encontrada nenhuma Distribuição de Origem que",
                        "corresponda ao código '{}'.",
                    ]
                ).format(src_distribution)
            )

        try:
            destination = self.Model.objects.get(pk=dst_distribution)
        except self.Model.DoesNotExist:
            raise Exception(
                " ".join(
                    [
                        "Não foi encontrada nenhuma Distribuição de Destino que",
                        "corresponda ao código '{}'.",
                    ]
                ).format(dst_distribution)
            )

        return source, destination

    def copy_players(self, args=[]):
        log.info(
            " ".join(
                [
                    "Gestor de Distribuicao: Tentando copiar Players da",
                    "Distribuição de Origem para a Distribuição de Destino.",
                ]
            )
        )

        response = {
            "success": False,
            "message": "Action not implemented.",
            "msg_type": "error",
        }

        try:
            source, destination = self._instances_from_params()

            text = "Gestor de Distribuicao: Copiando Players de '{}' para '{}'."
            log.info(text.format(source, destination))

            destination.copy_players_from(source=source)

            response.update(
                {
                    "success": True,
                    "message": "Ação realizada com êxito.",
                    "msg_type": "info",
                }
            )
        except KeyError as e:
            if str(e).find("u'") > -1:
                e = str(e)[1:]

            response.update(
                {
                    "message": "Verifique se o parâmetro %s foi passado na requisição."
                    % e
                }
            )
        except self.Model.BaseError as e:
            response.update({"message": str(e), "msg_type": e.msg_type})
        except Exception as e:
            response.update({"message": str(e)})

        return self.renderer(response)
