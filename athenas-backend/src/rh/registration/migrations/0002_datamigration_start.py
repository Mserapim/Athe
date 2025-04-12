# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from django.db import migrations

from contrib.middleware import StartupLoader, set_current_user
from rh.models import (
    CPF,
    RG,
    RG_ISSUER,
    DocsDadosEspecificos,
    Documento,
    Endereco,
    Servidor,
    Telefone,
)
from rh.registration.models import FormInformation

StartupLoader().doLoad()
set_current_user(User.objects.get(username="athenas"))


def datamigration_address_phone(apps, schema_editor):
    print("""Removendo espaços de CEP de Endereços.""")
    print("""Removendo mensagem incorreta de Complemento de Endereços.""")
    print("""Removendo espaços de Número de Telefone.""")
    employeers = Servidor.objects.filter(ativo=True)
    for employee in employeers:
        for address in employee.pessoa_fisica.address.filter():
            if address.complemento:
                p = re.compile(r"<.*?>")
                complemento = p.sub("", address.complemento)
                Endereco.objects.filter(pk=address.pk).update(complemento=complemento)

            if address.cep:
                cep = "".join(i for i in address.cep if i.isdigit())
                Endereco.objects.filter(pk=address.pk).update(cep=cep)

        for number in employee.pessoa_fisica.phone.exclude(tipo_telefone=6).filter():
            if number.numero:
                numero = "".join(i for i in number.numero if i.isdigit())
                Telefone.objects.filter(pk=number.pk).update(numero=numero)


def datamigration_forminformation(apps, schema_editor):
    print("""Carregamento inicial de informações para recadastramento.""")
    FormInformation.command_load_info_employee()


def datamigration_cpf_rg(apps, schema_editor):
    print("""Migrando CPF e RG para Documento e Documentos Especificos.""")
    verbose = True

    def show(employee, verbose=False):
        if verbose:
            cpf = employee.pessoa_fisica.cpf_document
            rg = employee.pessoa_fisica.rg_document
            date_expedition = ""
            state = ""
            issuer = ""
            if rg:
                date_expedition = rg.data_expedicao
                state = rg.estado_expedicao
                issuer = rg.rg_issuer
            print(
                employee,
                employee.pessoa_fisica.cpf_document,
                employee.pessoa_fisica.rg_document,
            )
            print(
                "CPF: %s | RG: %s - Expedição: %s - Estado: %s - Emissor: %s"
                % (cpf, rg, date_expedition, state, issuer)
            )
            print("--------------------------------------")

    for employee in Servidor.objects.filter():
        cpf = employee.pessoa_fisica.cpf_document
        rg = employee.pessoa_fisica.rg_document
        if not cpf or not rg:
            try:
                document = Documento(
                    numero=employee.pessoa_fisica.cpf, tipo_documento=CPF
                )
                document.save()
                employee.pessoa_fisica.documento.add(document)
            except Exception as err:
                print(err)
                show(employee, verbose=True)
            try:
                document = Documento(
                    numero=employee.pessoa_fisica.rg,
                    tipo_documento=RG,
                    data_expedicao=employee.pessoa_fisica.rg_data_expedicao,
                    estado_expedicao=employee.pessoa_fisica.rg_uf,
                )
                document.save()
                employee.pessoa_fisica.documento.add(document)
                docs = DocsDadosEspecificos(
                    especificidade=RG_ISSUER, valor=employee.pessoa_fisica.rg_orgao
                )
                docs.save()
                document.dados_especificos.add(docs)
            except Exception as err:
                print(err)
                show(employee, verbose=True)
        show(employee, verbose=verbose)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE", reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunPython(datamigration_address_phone, _null_function),
        migrations.RunPython(datamigration_cpf_rg, _null_function),
        migrations.RunPython(datamigration_forminformation, _null_function),
        migrations.RunSQL(
            migrations.RunSQL.noop, reverse_sql="SET CONSTRAINTS ALL IMMEDIATE"
        ),
    ]
