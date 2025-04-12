# -.- coding: utf-8 -.-
from datetime import datetime
import django
import os

import codecs

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from rh.models import Dependencia, PossessionTrainee, Servidor, Endereco, Telefone
from esocial.models import ItemTable


set_current_user("gustavodettenborn")


def write_file(buff, mode="a+"):
    with codecs.open("rh_problems.txt", mode) as f:
        f.write(buff)


def run_problems():
    buff = "\nServidores sem endereço:\n"
    print(buff)
    for employee in Servidor.objects.filter(ativo=True).exclude(
        type_by_possession__in=["TCR", "VOL", "JCA", "EXT", "MAP", "SAP"]
    ):
        end = Endereco.objects.filter(person__pessoafisica=employee.pessoa_fisica)
        if not end.exists():
            message = f"\n{employee} não possui endereço!"
            print(message)
            buff += message
    write_file(buff)

    buff = "\nCEP com problemas:\n"
    print(buff)
    for end in Endereco.objects.filter(
        person__pessoafisica__servidor__ativo=True,
        person__pessoafisica__servidor__tipo__in=["M", "S"],
    ).order_by("person"):
        employee = end.person.pessoafisica.servidor_set.filter(ativo=True).get()
        cep = end.cep
        msg = ""
        if cep and 8 > len(cep) > 13:
            msg += "menor que 8 ou maior que 13"
        if cep and not cep.isdigit():
            msg += " | não é digíto"
        if msg:
            msg = f"CEP: {cep} => {msg}"

        try:
            ItemTable.objects.by_choice_table(end.tipo_logradouro, "20").code
        except Exception as err:
            print(err)
            msg += f" | Tipo de Logradouro: {end.get_tipo_logradouro_display()} | Diferente dos tipos do eSocial"

        if msg:
            message = f"{employee} | {msg}"
            print(message)
            buff += message + "\n"
    write_file(buff)

    buff = "\nServidores sem Configurações previdenciárias:"
    print(buff)
    for employee in (
        Servidor.objects.active()
        .filter(socialsecurities__isnull=True)
        .exclude(
            type_by_possession__in=["TCR", "VOL", "JCA", "EXT", "EST", "MAP", "SAP"]
        )
    ):
        buff += f"\n{employee}"
    write_file(buff)


def trainee():
    buff = "\nEstagiários:\n"
    print(buff)
    for possession_trainee in PossessionTrainee.objects.filter():
        employee = possession_trainee.servidor
        msg = ""
        if not possession_trainee.employee_supervisor:
            msg += "Não possui supervisor."
        if not possession_trainee.educational_institution:
            msg += "\nNão possui instituto de educação."
        if (
            possession_trainee.educational_institution
            and not possession_trainee.educational_institution.cnpj
        ):
            msg += "\nNão possui cnpj de instituto de educação."
        end = Endereco.objects.filter(
            person__pessoajuridica=possession_trainee.educational_institution
        )
        if not end.exists():
            msg += "\nNão possui endereço de instituto de educação."
        if not possession_trainee.integration_agent:
            msg += "\nNão possui agente de integração."
        if (
            possession_trainee.integration_agent
            and not possession_trainee.integration_agent.cnpj
        ):
            msg += "\nNão possui cnpj de agente de integração."
        if not possession_trainee.nature:
            msg += "\nNão possui natureza."
        if not possession_trainee.level:
            msg += "\nNão possui nível."

        if msg:
            message = f"{employee} | {msg}"
            print(message)
            buff += message + "\n"
    write_file(buff)
    print()


def natural_person():
    buff = "\nPessoa Física de Servidor ativo:\n"
    print(buff)
    for employee in Servidor.objects.filter(ativo=True).exclude(
        type_by_possession__in=["TCR", "VOL", "JCA", "EXT", "MAP", "SAP"]
    ):
        msg = ""
        natural_person = employee.pessoa_fisica
        if not natural_person.sexo:
            msg += "\nNão possui sexo."
        if not natural_person.municipio_naturalidade:
            msg += "\nNão possui naturalidade."
        if not natural_person.nationality_birth:
            msg += "\nNão possui nacionalidade."
        if not natural_person.data_nascimento:
            msg += "\nNão possui data de nascimento."

        if msg:
            message = f"{employee} | {msg}"
            print(message)
            buff += message + "\n"
    write_file(buff)


def fone():
    buff = "\nTelefone:\n"
    print(buff)
    for tel in Telefone.objects.filter(
        person__pessoafisica__servidor__isnull=False
    ).order_by("person"):
        msg = ""
        if tel.person.pessoafisica.servidor_set.filter(ativo=True).exists():
            employee = tel.person.pessoafisica.servidor_set.filter(ativo=True).get()
        else:
            employee = tel.person.pessoafisica.servidor_set.last()

        numero = tel.numero
        if numero and (8 > len(numero) > 13):
            msg += f"\nTamanho {len(numero)} menor que 8 e maior que 13: {numero}."

        if msg:
            message = f"{employee} | {msg}"
            print(message)
            buff += message + "\n"
    write_file(buff)


def dependent():
    buff = "\nDependentes:\n"
    print(buff)
    query_dep = Dependencia.objects.active_in(
        range=NewDateRange(datetime(2021, 11, 1).date())
    ).filter(tipo__in=[1, 3])
    for dep in query_dep.order_by("dependente__pessoa_fisica"):
        msg = ""
        pf = dep.dependente.pessoa_fisica
        if not pf.data_nascimento:
            msg += f"\nnão possui data de nascimento."
        if not pf.sexo:
            msg += f"\nnão possui sexo."

        if msg:
            message = f"{dep.dependente.servidor} | {pf} | {msg}"
            print(message)
            buff += message + "\n"
    write_file(buff)


if __name__ == "__main__":
    write_file("", mode="w")
    run_problems()
    trainee()
    natural_person()
    fone()
    dependent()
