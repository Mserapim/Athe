import base64
from datetime import datetime

from django.db.models import Value, CharField, F, Prefetch
from django.db.models.functions import Concat

from rh.models import Lotacao, Servidor


def get_data_report(params):

    servidores_prefetch = Prefetch(
        "servidor_set",
        queryset=Servidor.objects.filter(ativo=True, servidor_lotacao__ativo=True)
        .annotate(
            servidor_concatenado=Concat(
                "matricula",
                Value(" - "),
                "pessoa_fisica__nome",
                output_field=CharField(),
            )
        )
        .distinct(),
        to_attr="servidores_ativos",
    )

    lotacao = (
        Lotacao.objects.filter(organograma=True, responsavel__isnull=False)
        .prefetch_related(servidores_prefetch)
        .annotate(
            serv_resp=F("responsavel__pessoa_fisica__nome"),
            serv_resp_matricula=F("responsavel__matricula"),
        )
        .order_by("serv_resp", "nome")
    )

    resultado = []
    for item in lotacao:
        servidores = [
            servidor.servidor_concatenado
            for servidor in item.servidores_ativos
            if servidor != item.responsavel
        ]
        resultado.append(
            {
                "nome": item.nome,
                "servidores": servidores,
                "serv_resp": item.serv_resp,
                "serv_resp_matricula": item.serv_resp_matricula,
            }
        )

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return {
        "title": "Servidores por Lotação",
        "lotacoes": resultado,
        "logo_mpmt": encoded_string.decode("utf-8"),
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
    }
