# -*- coding:utf-8 -*-
import re
import json
from zeep.helpers import serialize_object
from zeep.client import Client
from zeep.transports import Transport
from lxml import etree
from zeep import Plugin


class PatchXml(Plugin):
    def egress(self, envelope, http_headers, operation, binding_options):

        request_message = etree.tostring(envelope, encoding="unicode")

        if "<soap-env:Body>" in request_message:
            request_message = re.sub(
                r"ns[\d]+:pessoaFisica", "pessoaFisica", request_message
            )
            parser = etree.XMLParser()
            new_envelope = etree.XML(request_message, parser=parser)
            # print(etree.tostring(new_envelope, pretty_print=True))
            return new_envelope, http_headers

        else:

            return envelope, http_headers

    def ingress(self, envelope, http_headers, operation):
        # print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers


class WSClient(object):

    def __init__(self, url, user, passwd, logging=False):
        self.client = Client(url, plugins=[PatchXml()])
        self.user = user
        self.passwd = passwd
        self.factory = self.client.type_factory("ns0")

    def get_factory(self):
        return self.factory

    def create_message(self, object):
        return self.client.create_message(
            self.client.service,
            "salvarMembros",
            usuario=self.user,
            senha=self.passwd,
            membros=object,
        )

    def get_type(self, type):
        return self.client.get_type(type)

    def get_cargos(self):
        return self.client.service.obtemCargos(self.user, self.passwd)

    def get_ramos(self):
        return self.client.service.obtemRamos(self.user, self.passwd)

    def get_estados(self):
        return self.client.service.obtemEstados(self.user, self.passwd)

    def get_municipios_por_estado(self, uf_id):
        return self.client.service.obtemMunicipiosPorEstado(
            self.user, self.passwd, uf_id
        )

    def get_motivos_inativacao(self):
        return self.client.service.obtemMotivosInativacao(self.user, self.passwd)

    def get_motivos_inativacao(self):
        return self.client.service.obtemMotivosInativacao(self.user, self.passwd)

    def get_unidades_organicas(self, ramo):
        return self.client.service.obtemUnidadeOrganicas(self.user, self.passwd, ramo)

    def get_areas_cursos(self):
        return self.client.service.obtemAreasCurso(self.user, self.passwd)

    def get_disciplinas(self):
        return self.client.service.obtemDisciplinas(self.user, self.passwd)

    def get_tipos_pos_graduacao(self):
        return self.client.service.obtemTiposPosGraduacao(self.user, self.passwd)

    def get_obtem_tipos_trabalhos_publicados(self):
        return self.client.service.obtemTiposTrabalhosPublicados(self.user, self.passwd)

    def send_data(self, employee):
        response = None
        try:
            response = self.client.service.salvarMembros(
                usuario=self.user, senha=self.passwd, membros=employee
            )
            if response:
                response = json.loads(json.dumps(serialize_object(response, dict)))
        except Exception as e:
            raise e
        finally:
            return response
