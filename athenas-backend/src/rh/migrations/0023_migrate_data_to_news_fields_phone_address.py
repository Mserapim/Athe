# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from rh.models import OrgaoGeral, Pessoa, Endereco, Telefone


def factory_phone(phone, person=None, general_organ=None):
    return Telefone(
        tipo_telefone=phone.tipo_telefone,
        numero=phone.numero,
        publico=phone.publico,
        data_alteracao=phone.data_alteracao,
        person=person,
        general_organ=general_organ,
        created_by=phone.created_by,
        created_at=phone.created_at,
        modified_by=phone.modified_by,
        modified_at=phone.modified_at,
    )


def factory_address(address, person=None, general_organ=None):
    return Endereco(
        tipo_endereco=address.tipo_endereco,
        tipo_logradouro=address.tipo_logradouro,
        municipio=address.municipio,
        cep=address.cep,
        logradouro=address.logradouro,
        numero=address.numero,
        bairro=address.bairro,
        complemento=address.complemento,
        data_alteracao=address.data_alteracao,
        person=person,
        general_organ=general_organ,
        created_by=address.created_by,
        created_at=address.created_at,
        modified_by=address.modified_by,
        modified_at=address.modified_at,
    )


def migratedata_phone_person(apps, schema_editor):

    for person in Pessoa.objects.exclude(telefone__isnull=True):
        Telefone.objects.bulk_create(
            [factory_phone(phone, person=person) for phone in person.telefone.filter()]
        )


def migratedata_phone_general_organ(apps, schema_editor):

    for organ in OrgaoGeral.objects.exclude(telefone__isnull=True):
        Telefone.objects.bulk_create(
            [
                factory_phone(phone, general_organ=organ)
                for phone in organ.telefone.filter()
            ]
        )


def migratedata_address_general_organ(apps, schema_editor):

    for organ in OrgaoGeral.objects.exclude(endereco__isnull=True):
        Endereco.objects.bulk_create(
            [
                factory_address(address, general_organ=organ)
                for address in organ.endereco.filter()
            ]
        )


def migratedata_address_to_person(apps, schema_editor):

    for person in Pessoa.objects.exclude(endereco__isnull=True):
        Endereco.objects.bulk_create(
            [
                factory_address(address, person=person)
                for address in person.endereco.filter()
            ]
        )


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0022_create_new_fields_phone_address"),
    ]

    operations = [
        migrations.RunPython(migratedata_phone_general_organ, reverse_func),
        migrations.RunPython(migratedata_address_general_organ, reverse_func),
        migrations.RunPython(migratedata_phone_person, reverse_func),
        migrations.RunPython(migratedata_address_to_person, reverse_func),
    ]
