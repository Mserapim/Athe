from rest_framework.response import Response
import csv
import io
from django.http import HttpResponse
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from reports.tasks import report_csv
from django.utils.module_loading import import_string
from apiv2.utils import get_titulo_campo

log = getLogger(__name__)


class ResponseExportar(Response):
    def __init__(
        self,
        data_queryset,
        formato="csv",
        sincrono=False,
        campos=[],
        dados_lista=False,
        **kwargs,
    ):
        self.dados_lista = dados_lista

        if formato == "csv":
            if sincrono:
                content_type = "text/csv"
                content = self._gerar_csv_sincrono(data_queryset, campos)
                self.response = HttpResponse(content=content, content_type=content_type)
                self.response["Content-Disposition"] = (
                    'attachment; filename="dados.csv"'
                )
            else:
                task = self._gerar_csv_assincrono(data_queryset, campos)
                response_data = {
                    "success": True,
                    "uuid": task.uuid,
                    "message": "Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                }
                super().__init__(data=response_data, **kwargs)
        else:
            msg = "Formato inválido. Use 'csv'."
            log.error(msg)
            raise ValueError(msg)

    def _gerar_csv_sincrono(self, data_queryset, campos):
        if self.dados_lista:
            serializer_data = data_queryset["dados_lista"]
        else:
            serializer_class = import_string(data_queryset["serializer_name"])
            serializer_data = serializer_class(
                data_queryset["queryset"], many=True
            ).data

        if campos:
            serializer_data = [
                {campo: item.get(campo, "") or "" for campo in campos}
                for item in serializer_data
            ]

        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=serializer_data[0].keys(), delimiter=";"
        )
        writer.writeheader()
        writer.writerows(serializer_data)
        return output.getvalue()

    def _gerar_csv_assincrono(self, data_queryset, campos):
        """
        Função que retorna um arquivo csv assincrono
        Args:
            data: dados da consulta
        Returns:
            task
        """
        try:
            if "dados_lista" in data_queryset and data_queryset["dados_lista"]:
                data_model = {"dados_lista": data_queryset["dados_lista"]}
            else:
                data_ids = list(data_queryset["queryset"].values_list("id", flat=True))
                model_name = data_queryset["queryset"].model._meta.label
                data_model = {
                    "ids": data_ids,
                    "model": model_name,
                    "serializer_name": data_queryset["serializer_name"],
                }

            task = Task.start(
                report_csv,
                f"",
                success=f"""<a href="/athenas/api/v2/report/download/?uuid=%(uuid)s">Download</a>""",
                user=get_current_user().pk,
                download=False,
                filename="dados",
                mimetype="text/csv",
                extension="csv",
                identifier="registration",
                notificar=True,
                origem_apiv2=True,
                data_model=data_model,
                campos=campos,
            )
            return task
        except Exception as error:
            log.error(error)
