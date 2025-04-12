from engine.mq.models import Task
from reports.tasks import pdf_task
from contrib.base_converter import str_to_bool
import os
import ast
import traceback
from reports.utils import criar_pdf

from reports.data.mpmt.diarias.os_consolidada import get_data_report
from contrib.middleware import get_current_user, set_current_user


from contrib.utils import getLogger

log = getLogger(__name__)


class GerarOsConsolidada:

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def get_module(self):
        """
        Metódo que retorna o nome o path do módulo da classe
        """
        return f"{self.__module__}"

    def class_name(self):
        """
        Metódo que retorna o nome da classe
        """
        return f"{self.__class__.__name__}"

    def criar_os(self, beneficiario):
        try:
            template = "portrait/mpmt/diarias/os_consolidada/template.html"

            params = {
                "outfile": template,
                "report_name": "OS-Consolidado",
                "id_beneficiario": beneficiario.id,
                "output_format": "PDF",
            }

            file = criar_pdf(
                html_path=template,
                filename=f"{params['report_name'].lower()}",
                mimetype="application/pdf",
                extension="pdf",
                identifier="queryregistration",
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
            )

            return ("file", (f"{file.file}.pdf", open(file.absolute_path, "rb")))

        except Exception as error:
            log.error(str(error))
            error_message = traceback.format_exc()
            print(error_message)
            log.info(error_message)

        return None
