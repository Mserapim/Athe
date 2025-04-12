# -*- coding: utf-8 -*-
import json

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from esocial.models import Configuration
from esocial.security import extract_certificate
from ged.models import Arquivo

log = getLogger(__name__)


class ESOCIALConfiguration(RestfulDRY):

    _model = Configuration

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("esocial.configuration.ConfigurationManage")')

    def update_certificate(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            _certificate = Arquivo.objects.get(id=self.request.POST.get("certificate"))
        except Exception:
            _certificate = None

        try:
            _certificate_ca = Arquivo.objects.get(
                id=self.request.POST.get("certificate_ca")
            )
        except Exception:
            _certificate_ca = None

        _certificate_passwd = self.request.POST.get("certificate_passwd")

        if _certificate and _certificate_ca and _certificate_passwd:
            try:
                extract_certificate(
                    certificate_path=_certificate,
                    certificate_ca_path=_certificate_ca,
                    passwd=_certificate_passwd,
                )
            except Exception as e:
                log.exception(e)
                rst.update(message="{}".format(e))
            else:
                rst.update(success=True, message="Certificado atualizado com sucesso!")
        else:
            rst.update(message="Informe os dados do certificado antes de continuar.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(rst))
