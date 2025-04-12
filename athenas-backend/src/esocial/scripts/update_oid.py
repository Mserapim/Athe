# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from esocial.models import S1070, S2200, S2205, S2206, S2300, S2306, Event
from django.db.models import F


def run():

    acronyms = ["s1070", "s2200", "s2205", "s2206", "s2300", "s2306"]

    print(f"Atualizando oid de {acronyms}.")

    print("Atualizando oid de S1070.")
    for event in S1070.objects_all.exclude(oid=F("ide_processo_nr_proc")):
        oid = event.oid
        print(f"{oid} -> {event.ide_processo_nr_proc} | {event}", end="")
        if event.ide_processo_nr_proc is not None:
            ups = S1070.objects_all.filter(pk=event.pk).update(
                oid=event.ide_processo_nr_proc
            )
            print(f"({ups}) -> OK")
        else:
            print(f"({ups}) -> => não possui número do processo!")

    print("Atualizando oid de S2200 - OID.")
    for event in S2200.objects_all.exclude():
        oid = event.oid
        print(f"{oid} -> {event.vinculo_matricula} | {event}", end="")
        if event.vinculo_matricula is not None:
            ups = S2200.objects_all.filter(pk=event.pk).update(
                oid=event.vinculo_matricula, registry_employee=event.vinculo_matricula
            )
            print(f"({ups}) -> OK")
        else:
            print(f"({ups}) -> => não possui matrícula!")

    print("Atualizando oid de S2200 - START VALIDITY.")
    for event in S2200.objects_all.exclude(
        info_estatutario_dt_exercicio__isnull=False,
        start_validity=F("info_estatutario_dt_exercicio"),
    ):
        print(
            f"{event.start_validity} -> {event.info_estatutario_dt_exercicio} | {event}",
            end="",
        )
        ups = S2200.objects_all.filter(pk=event.pk).update(
            start_validity=event.info_estatutario_dt_exercicio,
            registry_employee=event.vinculo_matricula,
        )
        print(f"({ups}) -> OK")

    print("Atualizando oid de S2205.")
    for event in S2205.objects_all.exclude():
        oid = event.oid
        s2200 = S2200.objects_all.filter(
            trabalhador_cpf_trab=event.ide_trabalhador_cpf_trab
        )
        if s2200.exists():
            registry_employee = s2200.last().vinculo_matricula
            print(f"{oid} -> {registry_employee} | {event}", end="")
            if registry_employee is not None:
                ups = S2205.objects_all.filter(pk=event.pk).update(
                    oid=registry_employee
                )
                print(f"({ups}) -> OK")
            else:
                print(f"({ups}) -> ERRO => não possui matrícula!")

        else:
            print(
                f"{oid} {event.ide_trabalhador_cpf_trab} -> {event} -> ERRO => S2200 não encontrado!"
            )

    print("Atualizando oid de S2206.")
    for event in S2206.objects_all.exclude():
        oid = f"{event.ide_vinculo_matricula}-{event.alt_contratual_dt_alteracao}-{event.alt_contratual_dt_alteracao}"

        print(f"{event.oid} -> {oid} | {event}", end="")
        if event.ide_vinculo_matricula is not None:
            ups = S2206.objects_all.filter(pk=event.pk).update(
                oid=oid, registry_employee=event.ide_vinculo_matricula
            )
            print(f"({ups}) -> OK")
        else:
            print(f"({ups}) -> ERRO => não possui matrícula!")

    print("Atualizando oid de S2300.")
    for event in S2300.objects_all.exclude():
        oid = event.oid
        print(f"{oid} -> {event.info_tsv_inicio_matricula} | {event}", end="")
        if event.info_tsv_inicio_matricula is not None:
            ups = S2300.objects_all.filter(pk=event.pk).update(
                oid=event.info_tsv_inicio_matricula,
                registry_employee=event.info_tsv_inicio_matricula,
            )
            print(f"({ups}) -> OK")
        else:
            print(f"({ups}) -> ERRO => não possui matrícula!")

    print("Atualizando oid de S2306.")
    for event in S2306.objects_all.exclude():
        oid = event.oid
        print(f"{oid} -> {event.ide_trab_sem_vinculo_matricula} | {event}", end="")
        if event.ide_trab_sem_vinculo_matricula is not None:
            ups = S2306.objects_all.filter(pk=event.pk).update(
                oid=event.ide_trab_sem_vinculo_matricula,
                registry_employee=event.ide_trab_sem_vinculo_matricula,
            )
            print(f"({ups}) -> OK")
        else:
            print(f"({ups}) -> ERRO => não possui matrícula!")


if __name__ == "__main__":
    run()
