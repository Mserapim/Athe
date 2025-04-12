# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import (
    Capacidade,
    Cbo,
    Circunscricao,
    Entrancia,
    Especialidade,
    GrupoComarca,
    InCapacidade,
    Instancia,
    MesoRegiao,
    Molestia,
    Pais,
    Patrocinador,
    Penalidade,
    TempoServicoFinalidade,
)
from contrib.utils import getLogger

log = getLogger(__name__)


class RHCapacidadeRestful(RestfulDRY):

    _model = Capacidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.CapacidadeManage")')


class RHInCapacidadeRestful(RestfulDRY):

    _model = InCapacidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.InCapacidadeManage")')


class RHCboRestful(RestfulDRY):

    full_text_index = (
        "codigo__icontains",
        "descricao__icontains",
    )

    _model = Cbo

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.CboManage")')


class RHInstanciaRestful(RestfulDRY):

    _model = Instancia

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.InstanciaManage")')


class RHEntranciaRestful(RestfulDRY):

    _model = Entrancia

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.EntranciaManage")')


class RHEspecialidadeRestful(RestfulDRY):

    _model = Especialidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.EspecialidadeManage")')


class RHPaisRestful(RestfulDRY):

    full_text_index = (
        "nome__icontains",
        "descricao__icontains",
        "ddi__icontains",
        "nome_completo__icontains",
        "nacionalidade__icontains",
    )

    _model = Pais

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.PaisManage")')


class RHGrupoComarcaRestful(RestfulDRY):

    full_text_index = ("comarca__nome__icontains",)

    _model = GrupoComarca

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.GrupoComarcaManage")')


class RHMesoRegiaoRestful(RestfulDRY):

    _model = MesoRegiao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.MesoRegiaoManage")')


class RHCircunscricaoRestful(RestfulDRY):

    _model = Circunscricao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.CircunscricaoManage")')


class RHPatrocinadorRestful(RestfulDRY):

    _model = Patrocinador

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.PatrocinadorManage")')


class RHTempoServicoFinalidadeRestful(RestfulDRY):

    _model = TempoServicoFinalidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.TempoServicoFinalidadeManage")')


class RHDisease(RestfulDRY):

    _model = Molestia

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.disease.Manage")')

    def model_to_dict(self, instance):
        params = super(RHDisease, self).model_to_dict(instance)
        molestia = Molestia.objects.get(pk=instance.pk)

        try:
            nome = molestia.servidor.pessoa_fisica.nome
            matricula = molestia.servidor.matricula
        except:
            nome = ""
            matricula = ""

        params.update(
            {
                "nome": nome,
                "matricula": matricula,
            }
        )
        return params


class RHPunishment(RestfulDRY):

    _model = Penalidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.parameters.PunishmentManage")')
