# -*- coding: utf-8 -*-
import json

from contrib.newrest import RestfulDRY
from nomeacao.cadastramento.models import ConviteNomeacao, AnexoConvite

from django.db.models import F, CharField, Value
from django.db.models.functions import Replace, Cast

from contrib.utils import getLogger, get_json_engine
from contrib.nil import nil_date

from rh.models import PessoaFisica

from nomeacao.cadastramento.sinc_form_nomeacao_residente import (
    SincFormNomeacaoResidentes,
)

from contrib.utils import decode_base64

from validate_docbr import CPF


log = getLogger(__name__)
json_engine = get_json_engine()


class RHNomeacaoRestful(RestfulDRY):
    _model = ConviteNomeacao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.nomeacao.Manage")')

    def do_filter(self, query, force_filter=None):

        cpf = CPF()

        def fn(f):
            return {f.get("property"): self._filter_eval_value(f.get("value"))}

        try:
            flist = None
            if not force_filter:
                flist = json.loads(self.get_params().get("filter", "[]"))
            else:
                flist = force_filter
        except KeyError as e:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % e
            )
        except Exception as e:
            log.exception(e)
            raise (e)

        pessoa_fisica_pk = flist[0].get("value")

        pessoa_fisica = PessoaFisica.objects.get(pk=pessoa_fisica_pk)

        cpf_mascara = cpf.mask(pessoa_fisica.cpf)

        return ConviteNomeacao.objects.filter(convidado__documentacao__cpf=cpf_mascara)

    def model_to_dict(self, instance):
        params = super(RHNomeacaoRestful, self).model_to_dict(instance)
        params.update(
            {
                "cpf": instance.convidado.documentacao.cpf,
                "tipo_nomeacao": instance.get_tipo_nomeacao_display(),
                # "provimento": instance.provimento,
                "data_convocacao": nil_date(instance.data_convocacao, None),
                "data_resposta": nil_date(instance.data_resposta, None),
            }
        )
        return params


class RHNomeacaoAnexoRestful(RestfulDRY):
    _model = AnexoConvite

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.nomeacao.anexo_nomeacao.Manage")')

    def model_to_dict(self, instance):

        # params = super(AnexoConvite, self).model_to_dict(instance)

        params = RestfulDRY.model_to_dict(self, instance)
        params.update(
            {
                "tipo_documento_display": instance.get_tipo_documento_display(),
                "link_download": instance.api_arquivo_path,
            }
        )
        return params

    def download_anexo(self, *args):
        obj = {
            "success": True,
            "message": "Download do Anexo em Andamento",
        }

        anexo_pk = self.request.POST.get("anexo_pk")

        if not anexo_pk:
            obj["message"] = "Erro ao tentar realizar o Download do anexo"
            obj["success"] = False
        else:
            anexo = AnexoConvite.objects.get(pk=anexo_pk)
            res = SincFormNomeacaoResidentes().req_arquivo_anexo(
                anexo.api_relative_path
            )

            obj["arquivo"] = decode_base64(res.content)

        self.response.write(json_engine.encode(obj))
