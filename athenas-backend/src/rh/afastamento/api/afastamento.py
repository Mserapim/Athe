# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.afastamento.api.baselicencaafastamento import AFABaseLicencaAfastamentoRestful
from rh.afastamento.models import (
    Afastamento,
    AfastamentoComparecimentoJuizo,
    AfastamentoCandidatura,
    AfastamentoCompeticao,
    AfastamentoCursoConcurso,
    AfastamentoDeslocamento,
    AfastamentoDisponibilidade,
    AfastamentoEleitoral,
    AfastamentoEstudar,
    AfastamentoMandatoEletivo,
    AfastamentoMissao,
    AfastamentoOutroOrgao,
    AfastamentoPrisao,
    AfastamentoServirJuri,
    AfastamentoSuspensao,
    AfastamentoTreinamento,
    AfastamentoSindicanciaAdm,
    BaseLicencaAfastamento,
)

log = getLogger(__name__)


class AFAAfastamentoRestful(AFABaseLicencaAfastamentoRestful):

    full_text_index = () + AFABaseLicencaAfastamentoRestful.full_text_index

    exclude_fields = [] + AFABaseLicencaAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFABaseLicencaAfastamentoRestful.force_persist_boolean_fields
    )

    _model = Afastamento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.afastamento.Manage")')


class AFAAfastamentoComparecimentoJuizoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoComparecimentoJuizo

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentocomparecimentojuizo.Manage")'
        )


class AFAAfastamentoCandidaturaRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoCandidatura

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentocandidatura.Manage")'
        )


class AFAAfastamentoCompeticaoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoCompeticao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentocompeticao.Manage")'
        )


class AFAAfastamentoCursoConcursoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoCursoConcurso

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentocursoconcurso.Manage")'
        )


class AFAAfastamentoDeslocamentoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoDeslocamento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentodeslocamento.Manage")'
        )


class AFAAfastamentoEleitoralRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoEleitoral

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.afastamentoeleitoral.Manage")')


class AFAAfastamentoEstudarRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoEstudar

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.afastamentoestudar.Manage")')


class AFAAfastamentoParcialEstudarRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoEstudar

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentoparcialestudar.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(AFAAfastamentoParcialEstudarRestful, self).model_to_dict(
            instance
        )

        _dict_.update(
            {
                "parcial": True,
            }
        )
        return _dict_


class AFAAfastamentoMandatoEletivoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoMandatoEletivo

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentomandatoeletivo.Manage")'
        )


class AFAAfastamentoMissaoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoMissao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.afastamentomissao.Manage")')


class AFAAfastamentoOutroOrgaoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = [
        "transito_pela_folha"
    ] + AFAAfastamentoRestful.force_persist_boolean_fields

    _model = AfastamentoOutroOrgao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentooutroorgao.Manage")'
        )


class AFAAfastamentoDisponibilidadeRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = [
        "transito_pela_folha"
    ] + AFAAfastamentoRestful.force_persist_boolean_fields

    _model = AfastamentoDisponibilidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentodisponibilidade.Manage")'
        )


class AFAAfastamentoPrisaoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoPrisao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.afastamentoprisao.Manage")')


class AFAAfastamentoServirJuriRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoServirJuri

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentoservirjuri.Manage")'
        )


class AFAAfastamentoSuspensaoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoSuspensao

    def json(self, args=[]):

        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.afastamentosuspensao.Manage")')


class AFAAfastamentoTreinamentoRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoTreinamento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentotreinamento.Manage")'
        )


class AFAAfastamentoSindicanciaAdmRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = AfastamentoSindicanciaAdm

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentosindicanciaadm.Manage")'
        )


class AFAAfastamentoRecessoForenseRestful(AFAAfastamentoRestful):

    full_text_index = () + AFAAfastamentoRestful.full_text_index

    exclude_fields = [] + AFAAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFAAfastamentoRestful.force_persist_boolean_fields
    )

    _model = BaseLicencaAfastamento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.afastamentorecessoforense.Manage")'
        )

    def do_post(self, *args, **kwargs):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
        }

        params = self.get_params(self.request.POST, check_case=False)
        try:
            obj = self._model.objects.create(
                situation_unicode="Recesso Forense - Membros", tipo=7, **params
            )
            obj.tipo = 7
            obj.save()
            rst.update(
                success=True,
                message="Afastamento criado com sucesso!",
            )
        except Exception as e:
            raise Exception(e)

        return rst
