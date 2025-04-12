# -*- coding: utf-8 -*-
"""
    Este script atualiza as informações pendentes nos campos DigitalDocument.employee e DigitalDocument.person.
"""

import django
import os
import time

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from rh.models import DigitalDocument, Servidor


def run():
    print(
        """
        Este script atualiza as informações pendentes nos campos DigitalDocument.employee e DigitalDocument.person.
    """
    )
    time.sleep(5)
    updated = 0
    documents_not_employee = DigitalDocument.objects.filter(employee=None).exclude(
        person=None
    )
    documents_not_person = DigitalDocument.objects.filter(person=None).exclude(
        employee=None
    )
    total = documents_not_employee.count() + documents_not_person.count()
    print(f"DigitalDocument without person: {documents_not_person.count()}")
    for document in documents_not_person:
        person = document.employee.pessoa_fisica
        if person:
            DigitalDocument.objects.filter(pk=document.pk).update(person=person)
            updated += 1
            print(f"DigitalDocument UPDATED:  {updated} -> {total} | {person}")
        else:
            print(f"{document.employee} não possui pessoa física!")

    print(f"DigitalDocument without employee: {documents_not_employee.count()}")
    for document in documents_not_employee:
        employee = Servidor.objects.filter(
            pessoa_fisica=document.person.pessoafisica, ativo=True
        ).last()
        if not employee:
            employee = Servidor.objects.filter(
                pessoa_fisica=document.person.pessoafisica
            ).last()

        if employee:
            DigitalDocument.objects.filter(pk=document.pk).update(employee=employee)
            updated += 1
            print(f"DigitalDocument UPDATED: {updated} -> {total} | {employee}")
        else:
            print(f"{document.person.pessoafisica} não possui servidor!")

    print(f"DigitalDocument UPDATED: {updated} -> {total}")


if __name__ == "__main__":
    run()
