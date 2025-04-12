# -*- coding:utf-8 -*-

from django.db.models import Model, CharField, OneToOneField, CASCADE
from rh.models import PessoaFisica, PessoaJuridica
from edocs.protocolo.models import Protocolo
from web.ouvidoria.choices import SIM_NAO


def load_personal_data(cpf=None, cnpj=None):
    data = {}
    person = None

    if cpf:
        person = PessoaFisica.objects.filter(cpf=cpf).first()
        if person:
            data.update(
                nome=person.nome, sexo=person.sexo, grau_instrucao=person.grau_instrucao
            )

    elif cnpj:
        person = PessoaJuridica.objects.filter(cnpj=cnpj).first()
        if person:
            data.update(nome=person.nome)

    if person:
        address = person.address.last()
        if address:
            data.update(
                tipo_endereco=address.tipo_endereco,
                tipo_logradouro=address.tipo_logradouro,
                cep=address.cep,
                logradouro=address.logradouro,
                complemento=address.complemento,
                bairro=address.bairro,
                numero=address.numero,
                municipio=address.municipio.pk,
            )

        phone = person.phone.last()
        if phone:
            data.update(telefone=phone.numero)

    return data


class Manifestacao(Model):
    mora_no_municipio_referido = CharField(max_length=1, choices=SIM_NAO)
    protocolo = OneToOneField(
        Protocolo, related_name="manifestacao", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
