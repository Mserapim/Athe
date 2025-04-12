# -.- coding: utf-8 -.-
"""
    Este script corrige o type_by_possession dos servidores que estão com XXX.
"""

import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from rh.models import RequestMove, Servidor


def run():
    query = Servidor.objects.filter(type_by_possession="XXX")
    for employee in query:
        print(employee)
        print(employee.posses)
        if RequestMove.objects.filter(servidor=employee).exists():
            type_by_possession = "REQ"
            if RequestMove.objects.filter(
                servidor=employee, job_position_origin__icontains="MILITAR"
            ).exists():
                type_by_possession = "REX"
            if employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="CM"
            ).exists():
                type_by_possession = "RCM"
            if employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="FC"
            ).exists():
                type_by_possession = "RFC"
            print(
                f"Modificando type_by_possession {employee.type_by_possession} para {type_by_possession}."
            )
            Servidor.objects.filter(pk=employee.pk).update(
                type_by_possession=type_by_possession
            )

        if employee.posses.filter(quadro__cargo__tipo_lei_cargo="EF").exists():
            print(
                f"Modificando type_by_possession {employee.type_by_possession} para EFE."
            )
            type_by_possession = "EFE"
            if employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="CM"
            ).exists():
                type_by_possession = "ECM"
            if employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="FC"
            ).exists():
                type_by_possession = "EFC"
            Servidor.objects.filter(pk=employee.pk).update(
                type_by_possession=type_by_possession
            )

        if employee.posses.filter(quadro__cargo__tipo_lei_cargo="ES").exists():
            print(
                f"Modificando type_by_possession {employee.type_by_possession} para EST."
            )
            Servidor.objects.filter(pk=employee.pk).update(type_by_possession="EST")
        if employee.posses.filter(quadro__cargo__tipo_lei_cargo="TE").exists():
            print(
                f"Modificando type_by_possession {employee.type_by_possession} para TCR."
            )
            Servidor.objects.filter(pk=employee.pk).update(type_by_possession="TCR")
        if employee.posses.filter(quadro__cargo__tipo_lei_cargo="VL").exists():
            print(
                f"Modificando type_by_possession {employee.type_by_possession} para VOL."
            )
            Servidor.objects.filter(pk=employee.pk).update(type_by_possession="VOL")
        if employee.posses.filter(quadro__cargo__tipo_lei_cargo="JC").exists():
            print(
                f"Modificando type_by_possession {employee.type_by_possession} para JCA."
            )
            Servidor.objects.filter(pk=employee.pk).update(type_by_possession="JCA")
        print()


if __name__ == "__main__":
    run()
