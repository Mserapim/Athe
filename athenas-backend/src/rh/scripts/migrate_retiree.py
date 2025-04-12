# -*- coding: utf-8 -*-
import django
import os

from django.apps import registry

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from datetime import timedelta
from rh.models import DeclarationActivityRetiree, Retiree, Servidor, BenefitMovement
from contrib.middleware import set_current_user
from django.db import connection

from_to = {"MBR2": "MAP2", "MBR": "MAP", "EFE": "SAP"}

set_current_user("athenas")


def delete_retiree(pk):
    cursor = connection.cursor()
    # table_name = self.model._meta.db_table
    sql = f"DELETE FROM rh_retiree WHERE servidor_ptr_id={pk};"
    cursor.execute(sql)


def migrate_retiree():
    for r in Retiree.objects.all():
        mov = r._get_retirement_drive()
        employee = mov.servidor
        dt = employee.data_desligamento - timedelta(days=1)
        tbp = (
            "MBR2"
            if employee.get_is_procurador(dt)
            else (
                "MBR"
                if employee.get_is_promotor(dt)
                else ("EFE" if employee.get_is_efetivo(dt) else "XXX")
            )
        )
        tbpr = from_to.get(tbp, "XXX")
        Servidor.objects.filter(pk=employee.pk).update(type_by_possession=tbp)
        Servidor.objects.filter(pk=r.pk).update(
            type_by_possession=tbpr, founder_employee_id=employee.pk
        )
        print("------------------------")
        print(
            f"{tbp} PROC:{employee.get_is_procurador(dt)} PROM:{employee.get_is_promotor(dt)} SERV: { employee.get_is_efetivo(dt)} {employee}"
        )
        print(r.type_by_possession, mov.servidor.type_by_possession, r)
        dec_activity = DeclarationActivityRetiree.objects.filter(servidor=r).last()
        benefit, created = BenefitMovement.objects.get_or_create(
            servidor=r,
            data_posse=dec_activity.data_inicio,
            data_exercicio=dec_activity.data_inicio,
            defaults={"publicacao_movimentacao": dec_activity.publicacao_movimentacao},
        )
        print(f"{created} - {benefit}")
        delete_retiree(r.pk)
        s = Servidor.objects.get(pk=r.pk)
        deleted = DeclarationActivityRetiree.objects.filter(servidor=r).delete()
        print(
            f'Retiree {"APAGADO" if not getattr(s, "retiree", False) else "****ERRO****"}'
        )
        print(f'Dec. Ativity {"APAGADO" if deleted[0] else "****ERRO****"}')
        print(deleted)
        print("------------------------")


migrate_retiree()
