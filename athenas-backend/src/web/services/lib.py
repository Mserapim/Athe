#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from django.db import transaction
from contrib.utils import getLogger
from edocs.protocolo.models import Protocolo, Movimentacao, TipoDocumento
from rh.models import (
    Pessoa,
    PessoaFisica,
    PessoaJuridica,
    Telefone,
    Localidade,
    Endereco,
    Estado,
    Lotacao,
    MovimentacaoPosse,
    Quadro,
)

"""
Lista de parâmetros necessários para geração de protocolo:

    sigla_lotacao
    tipo_doc
    assunto
    resumo

    cep
    endereco
    bairro
    cidade (id)

    telefone

    Para pessoa física
        cpf
        interessado
        estado_civil
        raca_cor
        naturalidade (id da localidade)
        identidade
        emissor (orgão emissor do documento de identidade)

    Para pessoa jurídica
        cnpj
        interessado
        razao_social
"""


class IProtocolo(object):

    log = getLogger("IProtocolo")

    @classmethod
    def do(self, data, protocolo=None):

        try:
            with transaction.atomic():
                lotacao_origem = Lotacao.objects.get(sigla="PROTGE")
                lotacao_destino = Lotacao.objects.get(sigla=data["sigla_lotacao"])

                if not protocolo:
                    pessoa = None
                    anonimo = False

                    tipo_doc = TipoDocumento.objects.get(nome=data["tipo_doc"])
                    if "cpf" in data or "CPF" in data:
                        cpf = data.get("cpf", None) or data["CPF"]
                        pessoa = self.get_pessoa(cpf) or self.__create_pessoa(
                            nome=data.get("interessado", None) or data["nome"],
                            estado_civil=data["estado_civil"],
                            naturalidade=data["naturalidade"],
                            cpf=cpf,
                            raca=data.get("raca_cor", 0),
                            rg=data.get("rg", None) or data["identidade"],
                            rg_orgao=data["emissor"],
                            email=data.get("email", None),
                        )

                    elif "cnpj" in data or "CNPJ" in data:
                        cnpj = data.get("cnpj", None) or data["CNPJ"]
                        pessoa = self.get_pessoa_juridica(
                            cnpj
                        ) or self.__create_pessoa_juridica(
                            nome=data.get("interessado", None) or data["nome"],
                            razao_social=data["razao_social"],
                            cnpj=cnpj,
                        )

                    elif anonimo:
                        pessoa = self.get_anonimo()

                    if pessoa and pessoa.nome is not "ANONIMO":
                        cep = data.get("cep", None) or data["CEP"]
                        logradouro = data.get("endereco", None) or data["logradouro"]
                        endereco = self.get_endereco(
                            cep, logradouro
                        ) or self.__create_endereco(
                            cep=cep,
                            logradouro=logradouro,
                            bairro=data["bairro"],
                            tipo=data.get("tipo_endereco", 1),
                            cidade=data["cidade"],
                        )

                        telefone = self.get_telefone(
                            data["telefone"]
                        ) or self.__create_telefone(
                            numero=data["telefone"], tipo=data.get("tipo_telefone", 1)
                        )

                        pessoa.endereco.add(endereco)
                        pessoa.telefone.add(telefone)

                        protocolo = Protocolo(
                            interessado=pessoa,
                            orgao_geral_origem=lotacao_origem.orgaogeral_ptr,
                            lotacao_criacao=lotacao_origem.orgaogeral_ptr,
                            servidor_origem=lotacao_origem.responsavel,
                            tipo_documento=tipo_doc,
                        )
                    else:
                        e = Exception(
                            'Para gerar o protocolo é necessário um interessado "modelo pessoa"'
                        )
                        self.log.error(e)
                        return {"error": True, "msg": str(e), "data": None}

                protocolo.assunto = data["assunto"]
                protocolo.resumo = data["resumo"]
                protocolo.save()

                now = datetime.datetime.now()
                Movimentacao(
                    protocolo=protocolo,
                    lotacao_origem=protocolo.orgao_geral_origem,
                    lotacao_destino=lotacao_destino.orgaogeral_ptr,
                    servidor_origem=protocolo.servidor_origem,
                    servidor_destino=lotacao_destino.responsavel,
                    lotacao_criacao=protocolo.lotacao_criacao,
                    data_recebimento=now,
                    data_encaminhamento=now,
                    parecer=protocolo.resumo,
                    passo=protocolo.movimentacoes.all().count(),
                ).save()

                return {"error": False, "msg": None, "data": protocolo}
        except Exception as e:
            self.log.error(e)
            return {"error": True, "msg": str(e), "data": None}

    @classmethod
    def get_anonimo(self):
        return Pessoa.objects.get(nome="ANONIMO")

    @classmethod
    def get_pessoa(self, cpf):
        cpf = cpf.replace(".", "").replace("-", "")
        pessoa = PessoaFisica.objects.filter(cpf=cpf)
        return pessoa[0] if pessoa.exists() else None

    @classmethod
    def get_pessoa_juridica(self, cnpj):
        cnpj = cnpj.replace(".", "").replace("-", "").replace("/", "")
        pessoa = PessoaJuridica.objects.filter(cnpj=cnpj)
        return pessoa[0] if pessoa.exists() else None

    @classmethod
    def get_endereco(self, cep, logradouro):
        cep = cep.replace("-", "").replace(".", "")
        endereco = Endereco.objects.filter(cep=cep, logradouro=logradouro)
        return endereco[0] if endereco.exists() else None

    @classmethod
    def get_telefone(self, numero):
        numero = (
            numero.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        )
        telefone = Telefone.objects.filter(numero=numero)
        return telefone[0] if telefone.exists() else None

    """@transaction.commit_manually
    @classmethod
    def create_pessoa(self, cpf, nome, estado_civil, raca, rg, rg_orgao, naturalidade, email=None):
        try: pessoa = self.__create_pessoa(cpf, nome, estado_civil, raca, rg, rg_orgao, naturalidade, email)
        except Exception, e:
            log.error(e)
            transaction.rollback()
            return None
        else:
            transaction.commit()
            return pessoa

    @transaction.commit_manually
    @classmethod
    def create_pessoa_juridica(self, cnpj, nome, razao_social):
        try: pessoa = self.__create_pessoa_juridica(cnpj, nome, razao_social)
        except Exception, e:
            log.error(e)
            transaction.rollback()
            return None
        else:
            transaction.commit()
            return pessoa """

    @classmethod
    def __create_pessoa(
        self, cpf, nome, estado_civil, raca, rg, rg_orgao, naturalidade, email=None
    ):
        pessoa_fisica = PessoaFisica(
            cpf=cpf.replace(".", "").replace("-", ""),
            email_institucional=email,
            nome=nome,
            estado_civil=estado_civil,
            raca_cor=raca,
            municipio_naturalidade=Localidade.objects.get(id=naturalidade),
            rg=rg,
            rg_orgao=rg_orgao,
        )
        pessoa_fisica.save()
        return pessoa_fisica

    @classmethod
    def __create_pessoa_juridica(self, cnpj, nome, razao_social):
        pessoa_juridica = PessoaJuridica(
            cnpj=cnpj.replace(".", "").replace("-", "").replace("/", ""),
            nome=nome,
            razao_social=razao_social,
        )
        pessoa_juridica.save()
        return pessoa_juridica

    @classmethod
    def __create_endereco(self, logradouro, bairro, cep, cidade, tipo=1):
        endereco = Endereco(
            cep=cep.replace("-", "").replace(".", ""),
            logradouro=logradouro,
            bairro=bairro,
            tipo_endereco=tipo,
            tipo_logradouro=0,
            municipio=Localidade.objects.get(id=cidade),
        )
        endereco.save()
        return endereco

    @classmethod
    def __create_telefone(self, numero, tipo=1):
        telefone = Telefone(
            numero=numero.replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", ""),
            tipo_telefone=tipo,
        )
        telefone.save()
        return telefone


def lista_cidades_por_estado(sigla, nome):
    return _add_estado_a_cidades(
        Localidade.objects.filter(estado__sigla=sigla, nome__icontains=nome).values(
            "id", "nome", "estado"
        )
    )


def lista_cidades_por_nome(nome):
    return _add_estado_a_cidades(
        Localidade.objects.filter(nome__icontains=nome).values("id", "nome", "estado")
    )


def _add_estado_a_cidades(cidades):
    for item in cidades:
        estado = Estado.objects.get(id=item["estado"])
        item["estado"] = {"id": estado.id, "nome": estado.nome, "sigla": estado.sigla}
        item["nome"] += " - %s" % estado.sigla
    return list(cidades)
