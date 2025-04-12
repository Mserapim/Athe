# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.db.models import Q, deletion, Sum
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management import call_command

from contrib.middleware import set_current_user, get_current_user

from standard.models import Choice
from rh.models import Servidor

set_current_user("athenas")
user = get_current_user()

fixtures_files = (
    ("fixtures/02-menus.json", "Could not load minutes manager menu options."),
    ("fixtures/03-minute-choices.json", "Could not load minutes manager choices."),
    (
        "fixtures/04-minute-profiles.json",
        "Could not load profiles to the minutes manager.",
    ),
)


def load_choices_fixtures():

    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Loading fixtures...")
    try:
        for fixture, err_message in fixtures_files:
            filepath = os.path.join(BASE_DIR, "planejamento", "contrato", fixture)
            print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
            call_command("loaddata", filepath)
    except Exception:
        print("ERR: %s" % err_message)


def normalize_process_numbers(Contrato):
    for c in Contrato.objects.filter(tipo_contrato=2):
        if c.numero_processo:
            if len(c.numero_processo) == 14 and c.numero_processo[8] == "0":
                c.numero_processo = c.numero_processo[:8] + c.numero_processo[9:]
        if c.numero_processo_mae:
            if len(c.numero_processo_mae) == 14 and c.numero_processo_mae[8] == "0":
                c.numero_processo_mae = (
                    c.numero_processo_mae[:8] + c.numero_processo_mae[9:]
                )
        c.save()

    print("Process numbers corrected.")


def migrate_agreement_srp_to_minute(
    Contrato,
    Minute,
    OrgaoGeral,
    Processo,
    MinuteAction,
    AgreementSupervisor,
    MinuteSupervisor,
    MinuteItem,
    MinuteSolicitation,
    MinuteSolicitationItem,
    MinuteSolicitationCommitmentNote,
    MinuteSolicitationPayment,
):

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++ Starting Contract Migration (SRP) for Minute Manager +++")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("-------------------------------------------------")

    for count, contrato in enumerate(
        Contrato.objects.filter(tipo_contrato=2).order_by("numero")
    ):

        print(
            "Starting the migration of the agreement %s - %s"
            % (count + 1, contrato.numero)
        )

        if len(contrato.numero_processo) == 13:
            _numero_processo = (
                contrato.numero_processo[:4]
                + "."
                + contrato.numero_processo[4:8]
                + "."
                + contrato.numero_processo[8:]
            )
        elif len(contrato.numero_processo) == 21:
            _numero_processo = (
                contrato.numero_processo[:2]
                + "."
                + contrato.numero_processo[2:4]
                + "."
                + contrato.numero_processo[4:8]
                + "."
                + contrato.numero_processo[8:15]
                + "/"
                + contrato.numero_processo[15:19]
                + "-"
                + contrato.numero_processo[19:]
            )
        try:
            _process_number = Processo.objects.get(
                codigo_processo__icontains=_numero_processo
            )
        except:
            raise Exception("Processo %s não encontrado." % (contrato.numero_processo))

        if contrato.numero_processo_mae:
            if len(contrato.numero_processo_mae) == 13:
                _numero_processo_mae = (
                    contrato.numero_processo_mae[:4]
                    + "."
                    + contrato.numero_processo_mae[4:8]
                    + "."
                    + contrato.numero_processo_mae[8:]
                )
            elif len(contrato.numero_processo_mae) == 21:
                _numero_processo_mae = (
                    contrato.numero_processo_mae[:2]
                    + "."
                    + contrato.numero_processo_mae[2:4]
                    + "."
                    + contrato.numero_processo_mae[4:8]
                    + "."
                    + contrato.numero_processo_mae[8:15]
                    + "/"
                    + contrato.numero_processo_mae[15:19]
                    + "-"
                    + contrato.numero_processo_mae[19:]
                )
            try:
                _parent_process = Processo.objects.get(
                    codigo_processo__icontains=_numero_processo_mae
                )
            except:
                pass
        else:
            _parent_process = None

        _minute_object = contrato.objeto_contrato
        if contrato.pessoa.count() > 1:
            _minute_object += " OBS: Contratados da base legada: "
            for p in contrato.pessoa.all():
                _minute_object += p.nome + ","

        _bidding_type = None
        if contrato.tipo_licitacao in [3, 4, 5]:
            _bidding_type = contrato.tipo_licitacao
        else:
            _bidding_type = 4

        _minute_status = None
        if contrato.status == 4:
            _minute_status = 6
        else:
            _minute_status = 1

        minute = Minute.objects.create(
            number=contrato.numero,
            process_number=_process_number,
            parent_process=_parent_process,
            notice_number=contrato.numero_licitacao,
            management_organ=OrgaoGeral.objects.get(id=511),
            minute_object=_minute_object,
            bidding_type=_bidding_type,
            provider=contrato.pessoa.last(),
            adhesions_quantity=100,
            begin_validity=contrato.data_inicio,
            end_validity=contrato.data_vencimento,
            signature_date=contrato.data_inicio,
            publication_date=contrato.data_publicacao,
            official_diary=None,
            total_amount=None,
            object_execution="Ata originada por migração de dados.",
            days_for_notice=contrato.dias_para_aviso,
            status=_minute_status,
            created_by_id=user.id,
            modified_by_id=user.id,
        )

        print("--- Initiating the migration of contract actions.")

        for acao in contrato.acoes.all():
            if acao.tipo in [7, 12, 13, 100]:
                if acao.tipo == 7:
                    _action = 4
                elif acao.tipo == 12:
                    _action = 5
                elif acao.tipo == 13:
                    _action = 6
                else:
                    _action = 100

                minuteaction = MinuteAction.objects.create(
                    minute=minute,
                    user=acao.user,
                    action=_action,
                    observation=acao.observacao,
                )
                minuteaction.date = acao.data_acao
                minuteaction.save()

        print("--- Finalizing the migration of contract actions.")
        print("-------------------------------------------------")
        print("--- Initiating the migration of supervisors.")

        for agreementsupervisor in AgreementSupervisor.objects.filter(
            agreement=contrato.id
        ):
            minutesupervisor = MinuteSupervisor.objects.create(
                minute=minute,
                employee=agreementsupervisor.employee,
                kind=agreementsupervisor.kind,
                publication_document=agreementsupervisor.publication_document,
                publication_document_date=agreementsupervisor.publication_document_date,
                begin=agreementsupervisor.begin,
                observation=agreementsupervisor.observation,
                end=agreementsupervisor.end,
                created_by_id=user.id,
                modified_by_id=user.id,
            )
            minutesupervisor.classifications = agreementsupervisor.classifications.all()

        print("--- Finalizing the migration of supervisors.")
        print("-------------------------------------------------")

        if contrato.ne.count() > 0:
            print("--- Initializing item creation for minute.")
            valor = (
                contrato.ne.filter(reforco_estorno__isnull=True)
                .aggregate(Sum("valor"))
                .get("valor__sum")
                or 0
            )
            valor_reforco = (
                contrato.ne.filter(reforco_estorno=100)
                .aggregate(Sum("valor"))
                .get("valor__sum")
                or 0
            )
            valor_estorno = (
                contrato.ne.filter(reforco_estorno=1)
                .aggregate(Sum("valor"))
                .get("valor__sum")
                or 0
            )
            total_ne = (
                round(valor, 2) + round(valor_reforco, 2) - round(valor_estorno, 2)
            )

            # Adiciona um item com o valor da soma das NEs do contrato correspondente
            minuteitem = MinuteItem.objects.create(
                minute_id=minute.id,
                description="Item criado por migração de dados",
                unit_measure=61,
                quantity=1,
                unitary_value=total_ne,
                total_value=total_ne,
                group=999,
                item_balance=0,
                generate_agreement=False,
                status=1,
                created_by_id=user.id,
                modified_by_id=user.id,
            )
            minute.total_amount = total_ne
            minute.save()
            print("--- Finishing the creation of the item for the minute.")
            print("-------------------------------------------------")
            print("--- Initiating solicitation creation.")

            # Adiciona um Pedido para a Ata
            minutesolicitation = MinuteSolicitation.objects.create(
                minute_id=minute.id,
                number="0000/2018",
                edoc=None,
                justification="Pedido criado por migração de dados.",
                situation=1,
                created_by_id=user.id,
                modified_by_id=user.id,
            )
            print("--- Finalizing solicitation creation.")
            print("-------------------------------------------------")
            print("--- Initializing item creation for solicitation.")
            # Adiciona um item para o Pedido
            minutesolicitationitem = MinuteSolicitationItem.objects.create(
                solicitation_id=minutesolicitation.id,
                item_id=minuteitem.id,
                quantity=1,
                created_by_id=user.id,
                modified_by_id=user.id,
            )
            minutesolicitation.situation = 6
            minutesolicitation.save()

            print("--- Finishing the creation of the item for the solicitation.")
            print("-------------------------------------------------")
            print("--- Initiating the migration of commitment notes.")

            for notaempenho in contrato.ne.filter(ne_anterior_id__isnull=True).order_by(
                "id"
            ):
                commitmentnote = MinuteSolicitationCommitmentNote.objects.create(
                    id=notaempenho.id,
                    solicitation=minutesolicitation,
                    number=notaempenho.numero_ne,
                    value=notaempenho.valor,
                    kind=notaempenho.tipo,
                    classification=notaempenho.classificacao,
                    reinforcement_reversal=notaempenho.reforco_estorno,
                    origin=1,
                    created_by=notaempenho.criado_por,
                    modified_by=notaempenho.modified_by,
                    created_at=notaempenho.created_at,
                    modified_at=notaempenho.modified_at,
                )

            for notaempenho_ref in contrato.ne.filter(
                ne_anterior_id__isnull=False
            ).order_by("id"):
                _parent = MinuteSolicitationCommitmentNote.objects.get(
                    id=notaempenho_ref.ne_anterior_id
                )
                commitmentnote_ref = MinuteSolicitationCommitmentNote.objects.create(
                    id=notaempenho_ref.id,
                    parent=_parent,
                    solicitation=minutesolicitation,
                    number=notaempenho_ref.numero_ne,
                    value=notaempenho_ref.valor,
                    kind=notaempenho_ref.tipo,
                    classification=notaempenho_ref.classificacao,
                    reinforcement_reversal=notaempenho_ref.reforco_estorno,
                    origin=1,
                    created_by=notaempenho_ref.criado_por,
                    modified_by=notaempenho_ref.modified_by,
                    created_at=notaempenho_ref.created_at,
                    modified_at=notaempenho_ref.modified_at,
                )
            print("--- Finalizing the migration of commitment notes.")
            print("-------------------------------------------------")
            print("--- Initiating the migration of payments")
            for medicao in contrato.medicoes.all():
                payment = MinuteSolicitationPayment.objects.create(
                    commitmentnote=MinuteSolicitationCommitmentNote.objects.get(
                        id=medicao.nota_empenho_id
                    ),
                    user=medicao.user,
                    start_reference_period=medicao.inicio_periodo_referencia,
                    end_reference_period=medicao.fim_periodo_referencia,
                    bank_order=medicao.ordem_bancaria,
                    value=medicao.valor,
                    payment_date=medicao.data_pagamento,
                    observation=medicao.observacao,
                    status=medicao.status,
                    invoice=medicao.nota_fiscal,
                    created_by_id=user.id,
                    modified_by_id=user.id,
                )
                payment.created_by = medicao.created_by
                payment.created_at = medicao.created_at
                payment.save()
            print("--- Finalizing the migration of payments ")

        print("Finalizing the migration of the agreement %s." % (contrato.numero))
        print("-------------------------------------------------")

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++ End of Contract Migration (SRP) for Minutes Manager +++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


def add_users_to_new_group_permissions():
    # Adicionando os grupos de permissão da ata para os usuários ativos e que possui permissão no Gestor de Contratos

    srv = None
    try:
        group = None
        basic_group = Group.objects.get(name="hiring-minute-supervisor")
        for srv in Servidor.objects.filter(
            Q(tipo__in=["S", "M"]), Q(ativo=True), ~Q(user=None)
        ):
            print("Adding permission to user: %s" % srv.user.username)
            if srv.user.groups.filter(name="hiring-agreement-financial"):
                group = Group.objects.get(name="hiring-minute-financial")
                srv.user.groups.add(group)
            if srv.user.groups.filter(name="hiring-agreement-manager"):
                group = Group.objects.get(name="hiring-minute-manager")
                srv.user.groups.add(group)
            if srv.user.groups.filter(name="hiring-agreement-view-all"):
                group = Group.objects.get(name="hiring-minute-view-all")
                srv.user.groups.add(group)
            srv.user.groups.add(basic_group)
            print("Added completion for user %s" % srv.user.username)
    except Exception:
        print("Unable to add %s user to group" % (srv))


def forwards_data_migration(apps, schema_editor):
    OrgaoGeral = apps.get_model("rh", "OrgaoGeral")
    Processo = apps.get_model("processo", "Processo")
    Contrato = apps.get_model("contrato", "Contrato")
    AgreementSupervisor = apps.get_model("contrato", "AgreementSupervisor")
    Minute = apps.get_model("contrato", "Minute")
    MinuteAction = apps.get_model("contrato", "MinuteAction")
    MinuteItem = apps.get_model("contrato", "MinuteItem")
    MinuteSolicitation = apps.get_model("contrato", "MinuteSolicitation")
    MinuteSolicitationItem = apps.get_model("contrato", "MinuteSolicitationItem")
    MinuteSolicitationCommitmentNote = apps.get_model(
        "contrato", "MinuteSolicitationCommitmentNote"
    )
    MinuteSolicitationPayment = apps.get_model("contrato", "MinuteSolicitationPayment")
    MinuteSupervisor = apps.get_model("contrato", "MinuteSupervisor")
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++ Initiating data migration... ++++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    load_choices_fixtures()
    normalize_process_numbers(Contrato)
    migrate_agreement_srp_to_minute(
        Contrato,
        Minute,
        OrgaoGeral,
        Processo,
        MinuteAction,
        AgreementSupervisor,
        MinuteSupervisor,
        MinuteItem,
        MinuteSolicitation,
        MinuteSolicitationItem,
        MinuteSolicitationCommitmentNote,
        MinuteSolicitationPayment,
    )
    add_users_to_new_group_permissions()

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++++++++++++++++ Finilizing data migration... +++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


def reverse_load_choices_fixtures():
    Choice.objects.filter(app_label="contrato", name__icontains="MINUTE_").delete()


def reverse_normalize_process_numbers(Contrato):
    for c in Contrato.objects.filter(tipo_contrato=2):
        if c.numero_processo:
            if len(c.numero_processo) == 15:
                c.numero_processo = (
                    c.numero_processo[:10] + "0" + c.numero_processo[10:]
                )
        if c.numero_processo_mae:
            if len(c.numero_processo_mae) == 15:
                c.numero_processo_mae = (
                    c.numero_processo_mae[:10] + c.numero_processo_mae[10:]
                )
        c.save()


def reverse_migrate_agreement_srp_to_minute(
    Minute,
    MinuteAction,
    MinuteSupervisor,
    MinuteItem,
    MinuteSolicitation,
    MinuteSolicitationItem,
    MinuteSolicitationCommitmentNote,
    MinuteSolicitationPayment,
):
    MinuteSolicitationPayment.objects.all().delete()
    MinuteSolicitationCommitmentNote.objects.all().delete()
    MinuteSolicitationItem.objects.all().delete()
    MinuteSolicitation.objects.all().delete()
    MinuteItem.objects.filter(parent__isnull=False).delete()
    MinuteItem.objects.all().delete()
    MinuteSupervisor.objects.all().delete()
    MinuteAction.objects.all().delete()
    Minute.objects.all().delete()


def reverse_add_users_to_new_group_permissions():
    group_permissions = {
        1: "hiring-minute-financial",
        2: "hiring-minute-manager",
        3: "hiring-minute-supervisor",
        4: "hiring-minute-view-all",
    }
    Group.objects.filter(name__in=group_permissions.values()).delete()


def reverse_data_migration(apps, schema_editor):
    Contrato = apps.get_model("contrato", "Contrato")
    Minute = apps.get_model("contrato", "Minute")
    MinuteAction = apps.get_model("contrato", "MinuteAction")
    MinuteItem = apps.get_model("contrato", "MinuteItem")
    MinuteSolicitation = apps.get_model("contrato", "MinuteSolicitation")
    MinuteSolicitationItem = apps.get_model("contrato", "MinuteSolicitationItem")
    MinuteSolicitationCommitmentNote = apps.get_model(
        "contrato", "MinuteSolicitationCommitmentNote"
    )
    MinuteSolicitationPayment = apps.get_model("contrato", "MinuteSolicitationPayment")
    MinuteSupervisor = apps.get_model("contrato", "MinuteSupervisor")
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("++++++++++++ Initiating rollback of data migration... ++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("reverse_load_choices_fixtures inicio")
    # reverse_load_choices_fixtures(Choice)
    print("reverse_load_choices_fixtures concluido")
    reverse_normalize_process_numbers(Contrato)
    print("reverse_normalize_process_numbers concluido")
    reverse_migrate_agreement_srp_to_minute(
        Minute,
        MinuteAction,
        MinuteSupervisor,
        MinuteItem,
        MinuteSolicitation,
        MinuteSolicitationItem,
        MinuteSolicitationCommitmentNote,
        MinuteSolicitationPayment,
    )
    print("reverse_migrate_agreement_srp_to_minute concluido")
    reverse_add_users_to_new_group_permissions()
    print("reverse_add_users_to_new_group_permissions concluido")

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++++++++++++ Rollback of data migration completed. ++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0016_auto_20180510_1935"),
    ]

    operations = [migrations.RunPython(forwards_data_migration, reverse_data_migration)]
