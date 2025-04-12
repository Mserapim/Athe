import reportlab.lib.units
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from contrib.utils import getLogger
from rh.sisdias.models import Sdia01OrdemServico
from diarias.utils.importacao_sisdias_api import importar_diarias_api
from django.db.models import IntegerField
from django.db.models.functions import Cast
from app.settings import SISDIAS_API_URL, SISDIAS_TOKEN

import requests

import threading

log = getLogger(__name__)


class ImportarDiariasView(APIView):
    """
    Retorna se o usuario logado tem permissão para criar uma viagem
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        resposta = {"success": True, "message": "Nada Feito", "code": 200, "data": {}}

        try:
            ano_inicio = request.data.get("ano_inicio")
            ano_fim = request.data.get("ano_fim", ano_inicio)
            servidor = request.data.get("servidor")

            qtd_total = 0

            params = {
                "ano_inicial": ano_inicio,
                "ano_final": ano_fim,
                "chapa_servidor": servidor,
            }

            url = f"{SISDIAS_API_URL}v1/diarias/porAno"
            headers = {"Authorization": f"Bearer {SISDIAS_TOKEN}"}

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                dados = response.json()

                qtd_total = dados["total"]

            if qtd_total > 0:
                thread = threading.Thread(
                    target=importar_diarias_api, args=(params, request.user)
                )
                thread.start()

                resposta["message"] = (
                    f"{qtd_total} diárias foram encontradas e enviadas para importação. Você será notificado assim que o processo de importação for concluído."
                )
            else:
                resposta["message"] = f"Nenhuma diária foi encontrada."

        except Exception as e:
            resposta["message"] = f"Erro ao tentar importar diaria - {e}"
            resposta["code"] = 400

        return Response(resposta, status=resposta["code"])
