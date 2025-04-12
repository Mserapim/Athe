from apiv2.baseserializers import BaseSerializer
from apiv2.const import MSG_SUCCESS_METHOD
from diarias.utils.fluxo_movimentacao import benef_mover_etapa
from diarias.utils.historico import clonar_ultimo_historico
from ged.models import Arquivo
from rest_framework import status
from django.db import transaction

from diarias.models import (
    Beneficiario,
    HistoricoAnexo,
    HistoricoFluxoViagemBeneficiario,
    Viagem,
)

from contrib.utils import getLogger

log = getLogger(__name__)


class AnaliseCeafSerializer(BaseSerializer):
    """
    Serializer para lidar com a criação de entradas de HistoricoFluxoViagemBeneficiario.
    """

    class Meta:
        model = HistoricoFluxoViagemBeneficiario
        fields = ["viagem", "beneficiario", "obs"]

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            with transaction.atomic():
                self.is_valid(raise_exception=True)

                request = self.context.get("request")
                anexos = request.data.get("anexos", None)

                beneficiario_id = request.data.get("beneficiario", None)
                obs = request.data.get("obs", None)

                beneficiario = Beneficiario.objects.get(id=beneficiario_id)

                historico = clonar_ultimo_historico(beneficiario)
                historico.obs = obs
                historico.decisao = "deferido"
                historico.save()

                if anexos:
                    for anexo_id in anexos:
                        arquivo = Arquivo.objects.get(pk=anexo_id)
                        anexo, _ = HistoricoAnexo.objects.get_or_create(
                            historico=historico, arquivo=arquivo
                        )

                benef_mover_etapa(beneficiario)

                rst.update(
                    {
                        "success": True,
                        "message": MSG_SUCCESS_METHOD["post"],
                        "data": self.data,
                    }
                )

        except Viagem.DoesNotExist:
            rst.update(
                {
                    "message": "Viagem não encontrada",
                    "code": status.HTTP_400_BAD_REQUEST,
                }
            )
        except Beneficiario.DoesNotExist:
            rst.update(
                {
                    "message": "Beneficiario não encontrado",
                    "code": status.HTTP_400_BAD_REQUEST,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})

        return rst
