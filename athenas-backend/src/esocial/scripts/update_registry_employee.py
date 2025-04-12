# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from esocial.models import S2200, S2205, S2206


print(f"Atualizando registry_employee de S2200, S2205 e S2206.")

for s in S2200.objects.filter():
    S2200.objects.filter(pk=s.pk).update(registry_employee=s.vinculo_matricula)
    c05 = S2205.objects.filter(ide_trabalhador_cpf_trab=s.trabalhador_cpf_trab).update(
        registry_employee=s.vinculo_matricula
    )
    c06 = S2206.objects.filter(ide_vinculo_matricula=s.vinculo_matricula).update(
        registry_employee=s.vinculo_matricula
    )
    print(f"{s} | S2205({c05}) | S2206({c06})")
