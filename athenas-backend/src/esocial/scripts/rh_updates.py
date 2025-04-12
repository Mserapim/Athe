# -.- coding: utf-8 -.-
import django
import os
import time

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.db.models import Q, query
from datetime import datetime
from dateutil.relativedelta import relativedelta
from contrib.middleware import set_current_user
from rh.models import (
    Cargo,
    CargoQuadro,
    Cbo,
    ConfigJobPosition,
    Dependencia,
    PessoaJuridica,
    Servidor,
    Endereco,
    PessoaFisica,
    Localidade,
    Pais,
    Estado,
    SocialSecurityEmployee,
    Telefone,
    Trainee,
    UnidadeAdministrativa,
)
from esocial.const import TYPE_STREET_MAP


set_current_user("gustavodettenborn")


def format_str(value):
    if value and (value.isspace() or len(value) == 0):
        value = None
    if value:
        value = " ".join(value.split())
    return value


def create_address(person):
    defaults = {
        "tipo_endereco": 1,
        "tipo_logradouro": 1,
        "municipio": Localidade.objects.get(pk=12178),
        "cep": "77006356",
        "logradouro": "1",
        "numero": "1",
        "bairro": "plano diretor",
        "complemento": None,
        "country": Pais.objects.last(),
    }
    return Endereco.objects.get_or_create(person=person, defaults=defaults)


def fix_address():
    for end in Endereco.objects.filter(person__pessoafisica__servidor__isnull=False):
        # print(end)
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

    print("Resolvendo Servidores sem endereço:")
    for employee in Servidor.objects.filter(
        type_by_possession__in=[
            "EFE",
            "ECM",
            "EFC",
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
            "CMS",
            "REQ",
            "RCM",
            "RFC",
            "EST",
            "MAP",
            "SAP",
            "BFP",
        ]
    ):
        end = Endereco.objects.filter(person__pessoafisica=employee.pessoa_fisica)
        if not end.exists():
            create_address(employee.pessoa_fisica)
    print()

    print("\nResolvendo CEP com menos de 8 caracteres:")
    for end in Endereco.objects.filter(
        person__pessoafisica__servidor__isnull=False
    ).order_by("person"):
        if end.person.pessoafisica.servidor_set.filter(ativo=True).exists():
            employees = end.person.pessoafisica.servidor_set.filter(ativo=True)
        else:
            employees = end.person.pessoafisica.servidor_set.filter()

        for employee in employees:
            cep = end.cep
            if cep and len(cep) < 8:
                print(f"{employee}\nEndereço: {end}\nCEP: {cep} | tamanho({len(cep)})")
                Endereco.objects.filter(pk=end.pk).update(
                    cep=f"{cep}%s" % ("0" * (8 - len(cep)))
                )
            if cep and len(cep) > 8:
                print(f"{employee}\nEndereço: {end}\nCEP: {cep} | tamanho({len(cep)})")
                Endereco.objects.filter(pk=end.pk).update(cep=f"{cep[0:7]}")
            if cep and not cep.isdigit():
                cep = "".join(cep.replace(".", "").replace("-", "").split())
                print(f"{employee}\nEndereço: {end}\nCEP: {cep}")
                Endereco.objects.filter(pk=end.pk).update(cep=cep)
            if not end.numero:
                Endereco.objects.filter(pk=end.pk).update(numero="1")
    print()

    print("\nResolvendo Tipo de logradouro diferente dos tipos do eSocial:")
    for end in Endereco.objects.filter(
        person__pessoafisica__servidor__isnull=False
    ).order_by("person"):
        if TYPE_STREET_MAP.get(end.tipo_logradouro, None) is None:
            if end.person.pessoafisica.servidor_set.filter(ativo=True).exists():
                employee = end.person.pessoafisica.servidor_set.filter(ativo=True).get()
            else:
                employee = end.person.pessoafisica.servidor_set.last()
            print(
                f"{employee}\nEndereço: {end}\nTipo de Logradouro: {end.get_tipo_logradouro_display()}"
            )
            print()
            Endereco.objects.filter(pk=end.pk).update(tipo_logradouro=1)
    print()


def generate_cpf():
    import requests

    url = "https://www.4devs.com.br/ferramentas_online.php"
    myobj = {"acao": "gerar_cpf", "pontuacao": "S", "cpf_estado": ""}
    try:
        x = requests.post(url, data=myobj)
        return x.text.replace(".", "").replace("-", "")
    except Exception as err:
        print(err)
    return None


def fix_cpf_dependent():
    query_dep = Dependencia.objects.filter(
        tipo__in=[1, 3]
    )  # .filter(Q(data_fim__gt=datetime(2017, 2, 1).date()) | Q(data_fim=None))
    for dep in query_dep.order_by("dependente__pessoa_fisica"):
        pf = dep.dependente.pessoa_fisica
        if pf.cpf and pf.cpf.isspace() or not pf.cpf:
            cpf = generate_cpf()
            if cpf:
                print(pf, cpf)
                PessoaFisica.objects.filter(pk=pf.pk).update(cpf=cpf)
            time.sleep(5)
        if not pf.data_nascimento:
            PessoaFisica.objects.filter(pk=pf.pk).update(
                data_nascimento=datetime.now().date() - relativedelta(years=5)
            )
        if not pf.sexo:
            PessoaFisica.objects.filter(pk=pf.pk).update(sexo="M")


def fix_social_security():
    rs = (
        Servidor.objects.filter(
            type_by_possession__in=[
                "EFE",
                "ECM",
                "EFC",
                "MBR",
                "MEL",
                "MCM",
                "MEC",
                "MBR2",
                "MEL2",
                "MCM2",
                "MEC2",
                "MAP",
                "SAP",
            ]
        )
        .filter(social_security=None)
        .update(social_security=3)
    )
    Servidor.objects.filter(matricula=121006).update(social_security=3)
    print(f"Atualização de Soicial Security. ({rs})")


def fix_trainee():
    print("Resolvendo Estagiários:")
    for employee in Trainee.objects.filter():
        if not employee.employee_supervisor:
            Trainee.objects.filter(pk=employee.pk).update(
                employee_supervisor=Servidor.objects.filter(ativo=True).last()
            )
        if not employee.educational_institution or (
            employee.educational_institution
            and not employee.educational_institution.cnpj
        ):
            Trainee.objects.filter(pk=employee.pk).update(
                educational_institution=PessoaJuridica.objects.exclude(
                    cnpj__isnull=True
                )
                .exclude(cnpj="")
                .last()
            )
        end = Endereco.objects.filter(
            person__pessoajuridica=employee.educational_institution
        )
        if not end.exists():
            create_address(employee.educational_institution)

        if not employee.integration_agent or (
            employee.integration_agent and not employee.integration_agent.cnpj
        ):
            Trainee.objects.filter(pk=employee.pk).update(
                integration_agent=PessoaJuridica.objects.exclude(cnpj__isnull=True)
                .exclude(cnpj="")
                .exclude(
                    pk=Trainee.objects.get(pk=employee.pk).educational_institution.pk
                )
                .last()
            )
        if not employee.nature:
            Trainee.objects.filter(pk=employee.pk).update(nature=1)
        if not employee.level:
            Trainee.objects.filter(pk=employee.pk).update(level=1)
    print()


def fix_natural_person():
    print("Resolvendo Pessoa Física:")
    for employee in Servidor.objects.filter():
        natural_person = employee.pessoa_fisica
        if not natural_person.sexo:
            PessoaFisica.objects.filter(pk=natural_person.pk).update(sexo="M")
        if not natural_person.municipio_naturalidade:
            PessoaFisica.objects.filter(pk=natural_person.pk).update(
                municipio_naturalidade=Localidade.objects.last()
            )
        if not natural_person.nationality_birth:
            PessoaFisica.objects.filter(pk=natural_person.pk).update(
                nationality_birth=Pais.objects.last()
            )
        if not natural_person.data_nascimento:
            PessoaFisica.objects.filter(pk=natural_person.pk).update(
                data_nascimento=datetime.now().date() - relativedelta(years=18)
            )


def fix_administrative_unit():
    print("Resolvendo Unidades Administrativas:")
    for au in UnidadeAdministrativa.objects.filter(pessoa_juridica__isnull=True):
        UnidadeAdministrativa.objects.filter(pk=au.pk).update(
            pessoa_juridica=PessoaJuridica.objects.filter(cnpj__isnull=False).last()
        )


def fix_cbo():
    print("\nResolvendo CBO:")
    CargoQuadro.objects.filter(cbo__isnull=True).update(
        cbo=Cbo.objects.get(codigo=242235)
    )
    CargoQuadro.objects.filter(cbo__codigo=1).update(cbo=Cbo.objects.get(codigo=242235))


def fix_fone():
    print("\nResolvendo Telefone:")
    for tel in Telefone.objects.filter(
        person__pessoafisica__servidor__isnull=False
    ).order_by("person"):
        if tel.person.pessoafisica.servidor_set.filter(ativo=True).exists():
            employee = tel.person.pessoafisica.servidor_set.filter(ativo=True).get()
        else:
            employee = tel.person.pessoafisica.servidor_set.last()

        numero = tel.numero
        if numero and len(numero) < 10:
            print(
                f"{employee}\nTelefone: {tel}\nNÚMERO: {numero} | tamanho({len(numero)})"
            )
            Telefone.objects.filter(pk=tel.pk).update(
                numero=f"{numero}%s" % ("0" * (10 - len(numero)))
            )
    print()


def fix_ss_employee_req():
    for employee in Servidor.objects.filter(
        type_by_possession__in=("REQ", "RCM", "RFC")
    ):
        Servidor.objects.filter(pk=employee.pk).update(
            exercise_date=employee.data_exercicio,
            termination_date=employee.data_desligamento,
        )
        SocialSecurityEmployee.objects.filter(
            employee=employee, start_validity__gt=employee.data_exercicio
        ).update(start_validity=employee.data_exercicio)


if __name__ == "__main__":
    rs = input(
        f"!!!!!NÃO EXECUTAR EM PRODUÇÃO!!!!!. \n VOCÊ DESEJA ATUALIZAR INFORMAÇÕES IMPORTANTES DO SERVIDOR? (s/N)"
    ).lower()
    if rs == "s":
        fix_address()
        # fix_social_security()
        # fix_cpf_dependent()
        # fix_trainee()
        fix_natural_person()
        # fix_administrative_unit()
        # fix_fone()
        # fix_cbo()
        # fix_ss_employee_req()
