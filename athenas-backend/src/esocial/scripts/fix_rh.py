# -.- coding: utf-8 -.-
from datetime import timedelta
import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from rh.models import Cbo, Endereco, RequestMove, Servidor, SocialSecurityEmployee

set_current_user("gustavodettenborn")


def format_str(value):
    if value and (value.isspace() or len(value) == 0):
        value = None
    if value:
        value = " ".join(value.split())
    return value


def fix_address():
    for end in Endereco.objects.filter(person__pessoafisica__servidor__isnull=False):
        cep = format_str(end.cep)
        cep = cep.replace("-", "").replace("/", "").replace(".", "")
        if cep != end.cep:
            print(cep, "||", end.cep)

        logradouro = format_str(end.logradouro)
        if logradouro != end.logradouro:
            print(logradouro, "||", end.logradouro)

        bairro = format_str(end.bairro)
        if bairro != end.bairro:
            print(bairro, "||", end.bairro)

        complemento = format_str(end.complemento)
        if complemento != end.complemento:
            print(complemento, "||", end.complemento)

        Endereco.objects.filter(pk=end.pk).update(
            cep=cep, logradouro=logradouro, bairro=bairro, complemento=complemento
        )


def fix_ss_employee_req():
    print(
        "Atualizando start_validity de SocialSecurity quando start_validity for maior que exercise_date:"
    )
    count = 0
    for employee in Servidor.objects.filter(
        type_by_possession__in=("REQ", "RCM", "RFC")
    ):
        count += SocialSecurityEmployee.objects.filter(
            employee=employee, start_validity__gt=employee.exercise_date
        ).update(start_validity=employee.exercise_date)
    print(f"Realizados: {count}")


def fix_rex():
    print("Atualizando RequestMove de policiais militares EXT para REX:")
    query = RequestMove.objects.filter(
        servidor__type_by_possession="EXT", job_position_origin__icontains="MILITAR"
    )
    for mr in query:
        print(mr.servidor, mr)
    print(
        Servidor.objects.filter(pk__in=query.values_list("servidor", flat=True)).update(
            type_by_possession="REX"
        )
    )

    print("Atualizando RequestMove de servidores EXT para REQ:")
    query = RequestMove.objects.filter(servidor__type_by_possession="EXT")
    for mr in query:
        print(mr.servidor, mr)
    print(
        Servidor.objects.filter(pk__in=query.values_list("servidor", flat=True)).update(
            type_by_possession="REQ"
        )
    )

    print(
        "Solicita atualização de exercise_date de servidores que possuem data_exercicio diferente de exercise_date:"
    )
    for employee in Servidor.objects.filter():
        Servidor.objects.filter(pk=employee.pk).update(
            exercise_date=employee.data_exercicio,
            termination_date=employee.data_desligamento,
        )

    print(
        "Atualiza possession_origin_date de RequestMove quando não for preenchida ou for maior que exercise_date do servidor:"
    )
    query = RequestMove.objects.filter()
    for mr in query.order_by("servidor"):
        if (
            not mr.possession_origin_date
            or mr.possession_origin_date >= mr.servidor.exercise_date
        ):
            print(mr.servidor, mr)
            print(
                query.filter(pk=mr.pk).update(
                    possession_origin_date=mr.servidor.exercise_date - timedelta(days=1)
                )
            )


if __name__ == "__main__":
    fix_rex()
    fix_address()
    fix_ss_employee_req()

    for cbo in Cbo.objects.filter():
        if len(cbo.codigo) < 6:
            print(f"{cbo} - atual: {cbo.codigo} => novo: {cbo.codigo.zfill(6)}")
            Cbo.objects.filter(pk=cbo.pk).update(codigo=cbo.codigo.zfill(6))
