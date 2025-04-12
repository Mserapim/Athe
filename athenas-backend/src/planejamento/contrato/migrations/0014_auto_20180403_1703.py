# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from contrib.middleware import set_current_user, get_current_user
from planejamento.contrato.models import (
    Contrato,
    AgreementSupervisor,
    SupervisorClassification,
    AcaoContrato,
    NotaEmpenho,
    EnvioNEFornecedor,
)
from contrib.utils import employee_from_user
from django.db import migrations
from django.db.models import Q
from django.core.management import call_command
from django.contrib.auth.models import Group, Permission
from standard.models import Choice
from rh.models import Servidor
import os

# Relação das antigas permissões de contrato
old_agreement_permissions = Permission.objects.filter(
    content_type__app_label="contrato"
)

# Mapa com os novos grupos de permissões
group_permissions = {
    1: "hiring-agreement-supervisor",
    2: "hiring-agreement-view-all",
    3: "hiring-agreement-manager",
    4: "hiring-agreement-supervisor",
    5: "hiring-agreement-financial",
}

# Profiles e Choices para os fiscais
fixtures_files = (
    (
        "00-choices.json",
        "Não foi possível carregar os choices para classificação e tipo de fiscal.",
    ),
    ("01-profiles.json", "Não foi possível carregar as permissões de perfis."),
)

# Caminhos até o diretório dos fixtures
migration_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.dirname(migration_dir)
fixture_dir = os.path.join(module_dir, "fixtures")


def remove_old_permissions():
    try:
        for oap in old_agreement_permissions:
            oap.group_set.clear()
    except Exception:
        print("Erro ao tentar remover a permissão %s de um de seus grupos" % oap)


def load_choices_and_permissions_fixtures():
    try:
        for fixture_file, err_message in fixtures_files:
            filepath = os.path.join(fixture_dir, fixture_file)
            call_command("loaddata", filepath)
    except Exception:
        print("ERR: %s" % err_message)

    Contrato.objects.filter(status=0).update(status=100)
    AcaoContrato.objects.filter(tipo=0).update(tipo=100)
    NotaEmpenho.objects.filter(reforco_estorno=0).update(reforco_estorno=100)
    EnvioNEFornecedor.objects.filter(prorrogacao=0).update(prorrogacao=100)


def create_supervisor_classifications():
    count = Choice.objects.filter(
        app_label="contrato", name__icontains="SUPERVISOR_CLASSIFICATION"
    ).count()
    for i in range(1, count + 1):
        SupervisorClassification.objects.get_or_create(
            kind=i,
            active=True,
            created_by=get_current_user(),
            modified_by=get_current_user(),
        )


def migrate_agreement_data_to_supervisor():
    for c in Contrato.objects.filter().order_by("pk"):
        print("Iniciando migração de Fiscal: " + str(c.pk))
        st, created = AgreementSupervisor.objects.get_or_create(
            kind=1,
            employee=employee_from_user(c.gestor.user, only_active=False),
            begin=c.data_inicio,
            publication_document_date=c.data_publicacao_fiscal,
            agreement=c,
        )
        for sc in SupervisorClassification.objects.filter(kind__in=[1, 2]):
            st.classifications.add(sc)

        for r in c.responsaveis.filter():
            ss, created = AgreementSupervisor.objects.get_or_create(
                employee=employee_from_user(r.user, only_active=False),
                kind=2,
                begin=c.data_inicio,
                publication_document_date=c.data_publicacao_fiscal,
                agreement=c,
            )
            for sc in SupervisorClassification.objects.filter(kind__in=[1, 2]):
                ss.classifications.add(sc)
        print("Encerrando migração de Fiscal: " + str(c.pk))


def add_user_to_new_group_permissions():
    # Adicionando antigos gestores e também servidores atualmente ativos a algum grupo de permissões do sistema de contratações
    try:
        group = None
        basic_group = Group.objects.get(name="hiring-agreement-supervisor")
        for srv in Servidor.objects.filter(
            ~Q(user__como_gestor=None)
            | Q(Q(tipo__in=["S", "M"]), Q(ativo=True), ~Q(user=None))
        ):
            if hasattr(srv.user, "como_gestor"):
                kind = srv.user.como_gestor.tipo
                group = Group.objects.get(name=group_permissions.get(kind))
                srv.user.groups.add(group)
            srv.user.groups.add(basic_group)
            print("Adicionando usuário: %s" % srv.user)
    except Exception:
        print("Não foi possível adicionar o usuário %s ao grupo %s" % (srv.user, group))


# Execução da migração
def forwards_supervisor_data_migration(apps, schema_editor):
    set_current_user("athenas")
    remove_old_permissions()
    load_choices_and_permissions_fixtures()
    create_supervisor_classifications()
    migrate_agreement_data_to_supervisor()
    add_user_to_new_group_permissions()


# Rollback da migração
def reverse_supervisor_data_migration(apps, schema_editor):
    print("\nRevertendo migração...")

    # Revertendo choices novos para antigos
    Contrato.objects.filter(status=100).update(status=0)
    AcaoContrato.objects.filter(tipo=100).update(tipo=0)
    NotaEmpenho.objects.filter(reforco_estorno=100).update(reforco_estorno=0)
    EnvioNEFornecedor.objects.filter(prorrogacao=100).update(prorrogacao=0)

    # Removendo choices de classificação e tipo para fiscal
    Choice.objects.filter(app_label="contrato", name__icontains="SUPERVISOR_").delete()

    # Removendo os usuários dos grupos de permissões
    Group.objects.filter(name__in=group_permissions.values()).delete()

    # Removendo classificações e fiscais
    AgreementSupervisor.objects.filter().delete()
    SupervisorClassification.objects.filter().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0013_auto_20180403_1702"),
    ]

    operations = [
        migrations.RunPython(
            forwards_supervisor_data_migration, reverse_supervisor_data_migration
        )
    ]
