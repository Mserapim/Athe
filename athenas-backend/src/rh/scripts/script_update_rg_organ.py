# -.- coding: utf-8 -.-
import django
import os

from django.apps import registry

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from rh.models import *
from rh.registration.models import FormInformation

REGISTRY_FORCE = [20799, 42302, 131216, 119065]


def clear_value(value=""):
    value = value.replace(" ", "")
    value = value.replace("-", "")
    value = value.replace("/", "")
    return value


def _update(dde, value="SSP", force=False):
    report = ""
    try:
        registry = REGISTRY_FORCE
        employee = (
            dde.documentos.get().naturalpersons.get().servidor_set.get(ativo=True)
        )
        old_value = dde.valor
        _clear_value = clear_value(old_value)
        changing = (
            _clear_value
            != PessoaFisica.objects.get(pk=employee.pessoa_fisica.pk).rg_orgao
            or _clear_value != FormInformation.objects.get(employee=employee).rg_orgao
            or _clear_value != value
        )
        if (
            (not _clear_value.isalpha() and changing)
            or (employee.matricula in registry and changing)
            or (force and _clear_value != value)
        ):
            DocsDadosEspecificos.objects.filter(pk=dde.pk).update(valor=value)
            DocsDadosEspecificos.objects.get(pk=dde.pk).update_natural_person_cache()
            dde = DocsDadosEspecificos.objects.get(pk=dde.pk)
            FormInformation.objects.filter(employee=employee).update(rg_orgao=dde.valor)
            report += f"Antigo: {old_value} | Novos valores => dde: {DocsDadosEspecificos.objects.get(pk=dde.pk).valor} | pessoafisica: {PessoaFisica.objects.get(pk=employee.pessoa_fisica.pk).rg_orgao} | recadastramento: {FormInformation.objects.get(employee=employee).rg_orgao} === {employee}\n"
    except Servidor.DoesNotExist as err:
        natural_person = dde.documentos.get().naturalpersons.get()
        old_value = dde.valor
        _clear_value = clear_value(old_value)
        changing = (
            _clear_value != PessoaFisica.objects.get(pk=natural_person.pk).rg_orgao
            or _clear_value != value
        )
        if not _clear_value.isalpha() and changing:
            DocsDadosEspecificos.objects.filter(pk=dde.pk).update(valor=value)
            DocsDadosEspecificos.objects.get(pk=dde.pk).update_natural_person_cache()
            dde = DocsDadosEspecificos.objects.get(pk=dde.pk)
            report += f"Antigo: {old_value} | Novos valores: dde: {DocsDadosEspecificos.objects.get(pk=dde.pk).valor} | pessoafisica: {PessoaFisica.objects.get(pk=natural_person.pk).rg_orgao} === {natural_person}\n"
    return report


def verify_employee_cpf():
    report = "\nServidores com problemas em CPF:\n"
    count = 0
    count_tocas = 0
    count_update = 0
    for employee in Servidor.objects.filter(tipo__in=["M", "S"], ativo=True).order_by(
        "pessoa_fisica__nome"
    ):
        cpf_document = employee.pessoa_fisica.cpf_document
        valor = "1"
        if cpf_document:
            valor = clear_value(cpf_document.numero)
        if valor.isalpha():
            report += f"{employee}: {valor}\n"
            count += 1
        cpf_pessoafisica_numero = clear_value(employee.pessoa_fisica.cpf)
        if cpf_pessoafisica_numero.isalpha() and valor.isalpha():
            report += f"{employee}: {cpf_pessoafisica_numero} | {valor}\n"
            count += 1
        if cpf_pessoafisica_numero != valor:
            report += f"{employee}: {cpf_pessoafisica_numero} | {valor}\n"
            count += 1
    report += f"total com possíveis problemas: {count}\n"
    return report


def verify_employee_update():
    report = "\nServidores com problemas atualizados para SSP:\n"
    count = 0
    count_tocas = 0
    count_update = 0
    print("Verificando SERVIDORES com possíveis problemas:")
    for employee in Servidor.objects.filter(tipo__in=["M", "S"], ativo=True).order_by(
        "pessoa_fisica__nome"
    ):
        for dd in employee.pessoa_fisica.documento.filter():
            for dde in dd.dados_especificos.filter(especificidade=13):
                valor = clear_value(dde.valor)
                if not valor.isalpha():
                    report += f"{employee}: {valor}\n"
                    count += 1
                    if dd.estado_expedicao.sigla == "TO":
                        if UPDATE_NATURAL_PERSON_EMPLOYEE_SPP == "s":
                            report += _update(dde)
                            count_update += 1
                        count_tocas += 1

                if employee.matricula in REGISTRY_FORCE:
                    report += _update(dde)
        rg_pessoafisica_valor = clear_value(employee.pessoa_fisica.rg_orgao)
        if not rg_pessoafisica_valor.isalpha() and not valor.isalpha():
            report += f"{employee}: {rg_pessoafisica_valor} | {valor}\n"
            count += 1
    report += f"total com possíveis problemas: {count}\n"
    report += f"total com possíveis problemas do TO: {count_tocas}\n"
    report += f"diferença: {count - count_tocas}\n"
    report += f"total do TO atualizado: {count_update}\n"
    return report


def update_specialized():
    report = "\nServidores atualizados com ordem específica:\n"
    if UPDATE_SPECIFIC == "s":
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7413).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7418).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7424).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7436).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7445).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7446).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7468).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7499).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7502).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7510).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7529).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7543).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=9915).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7576).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7625).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7660).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7668).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7688).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7691).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7700).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7737).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7744).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7749).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7784).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7807).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7822).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7832).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7843).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7865).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7874).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7949).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7959).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7971).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=9544).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8015).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8024).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8038).get(),
            value="SEJSP",
            force=True,
        )  # VALÉRIA BUSO RODRIGUES BORGES | 8038 | SEJSP  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8047).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8051).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8057).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7587).get(),
            value="GEJSPC",
            force=True,
        )  # FERNANDO ANTONIO SENA SOARES | 7587 | GEJSPC  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7388).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7396).get(), value="SESP", force=True
        )  # ALESSANDRA KELLY FONSECA DANTAS | 8038 | SESP  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7434).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7439).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7500).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=17225).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7531).get(),
            value="SESPDGPC",
            force=True,
        )  # DIOGO DOS SANTOS MIRANDA | 7531 | SESPDGPC  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7535).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7536).get(), value="SESP", force=True
        )  # DIVINO HUMBERTO DE SOUZA LIMA | 7536 | SESP  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7540).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7592).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7593).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7599).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=14791).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7692).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7760).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7780).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7788).get(), value="SESP", force=True
        )  # LUIZ FELIPE JARDIM GAMEIRO | 7788 | SESP  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7809).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7882).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=18058).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8020).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8048).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=8049).get(), value="SSP"
        )  ### CONFERIDOS
        report += _update(
            DocsDadosEspecificos.objects.filter(pk=7804).get(), value="SSP"
        )  ### CONFERIDOS
    return report


def verify_natural_person_update():
    # global VERIFY_NATURAL_PERSON
    # global UPDATE_NATURAL_PERSON_SPP
    if VERIFY_NATURAL_PERSON == "s":
        row = 0
        count = 0
        count_update = 0
        count_tocas = 0
        query = PessoaFisica.objects.filter(
            documento__dados_especificos__especificidade=13, servidor__isnull=True
        )
        total = query.count()
        for natural_person in query:
            row += 1
            print(f"{row} of {total}")
            for dd in natural_person.documento.filter(
                dados_especificos__especificidade=13
            ):
                for dde in dd.dados_especificos.filter(especificidade=13):
                    valor = clear_value(dde.valor)
                    if not valor.isalpha():
                        # if dd.estado_expedicao and dd.estado_expedicao.sigla != 'TO':
                        #     print(natural_person)
                        #     print(f'DocsDadosEspecificos.objects.filter(pk={dde.pk}).update(valor=)', valor, f' - ESTADO: {dd.estado_expedicao}')
                        #     print('------------------------------')
                        count += 1
                        if dd.estado_expedicao and dd.estado_expedicao.sigla == "TO":
                            if UPDATE_NATURAL_PERSON_SPP == "s":
                                _update(dde)
                                count_update += 1
                            count_tocas += 1
        print(f"total com possíveis problemas: {count}")
        print(f"total com possíveis problemas do TO: {count_tocas}")
        print(f"diferença: {count - count_tocas}")
        print(f"total do TO atualizado: {count_update}")


def _update_natural_person_rg_issuer():
    report = (
        "\nAtualizando Servidores com problemas: _update_natural_person_rg_issuer\n"
    )
    count_update = 0
    for employee in Servidor.objects.filter(tipo__in=["M", "S"], ativo=True).order_by(
        "pessoa_fisica__nome"
    ):
        for dd in employee.pessoa_fisica.documento.filter():
            dde = None
            for dde in dd.dados_especificos.filter(especificidade=13):
                valor = clear_value(dde.valor)
                if not valor.isalpha():
                    report += f"{employee}: {valor}\n"
        rg_pessoafisica_valor = clear_value(employee.pessoa_fisica.rg_orgao)
        if not rg_pessoafisica_valor.isalpha() and valor.isalpha():
            dde.update_natural_person_cache()
            final_value = PessoaFisica.objects.get(
                pk=employee.pessoa_fisica.pk
            ).rg_orgao
            FormInformation.objects.filter(employee=employee).update(
                rg_orgao=final_value
            )
            if final_value != dde.valor:
                print(f"\ndiffffff {dde.valor} {final_value}\n")
            report += f"{employee}: {rg_pessoafisica_valor} | {dde.valor} | final: {final_value} | recadastramento: {FormInformation.objects.get(employee=employee).rg_orgao}\n"
            count_update += 1
    report += f"atualizados: _update_natural_person_rg_issuer {count_update}\n"
    return report


def check_all():
    report = "\nchecando todos os dados\n"
    count_update = 0
    for employee in Servidor.objects.filter(tipo__in=["M", "S"], ativo=True).order_by(
        "pessoa_fisica__nome"
    ):
        rg_pessoafisica_valor = clear_value(employee.pessoa_fisica.rg_orgao)
        fiv = clear_value(FormInformation.objects.get(employee=employee).rg_orgao)
        rg_document = employee.pessoa_fisica.rg_document
        valor = "1"
        if rg_document and rg_document.rg_issuer:
            valor = clear_value(rg_document.rg_issuer.valor)
            if not valor.isalpha():
                report += f"{employee} - dde {valor} | PessoaFisica.rg_orgao {rg_pessoafisica_valor} | forminformation rg_orgao {fiv}\n"
        if not rg_pessoafisica_valor.isalpha():
            report += f"{employee} - PessoaFisica.rg_orgao {rg_pessoafisica_valor} | forminformation rg_orgao {fiv} | dde {valor}\n"
        if not fiv.isalpha():
            report += f"{employee} - forminformation rg_orgao {fiv} | PessoaFisica.rg_orgao {rg_pessoafisica_valor} | dde {valor}\n"
    return report


if __name__ == "__main__":
    UPDATE_NATURAL_PERSON_EMPLOYEE_SPP = input(
        f"Atualizar SERVIDORES que possuem RG do Tocantins para SSP? (s/N)"
    ).lower()
    UPDATE_SPECIFIC = input("Atualizar os específicos primeiro? (s/N)").lower()
    # VERIFY_NATURAL_PERSON = input('Verificar PESSOA FÍSICA: (s/N)').lower()
    # UPDATE_NATURAL_PERSON_SPP = input('Atualizar PESSOA FÍSICA do Tocantins para SSP: (s/N)').lower()

    report = ""
    # report = update_specialized()
    # report += verify_employee_update()
    # report += verify_employee_cpf()
    # if input('Atualizar rg órgão com dados específicos do documento? (s/N)').lower() == 's':
    #     report += _update_natural_person_rg_issuer()
    report += check_all()
    print(report)
    # verify_natural_person_update()
    # print(_update_natural_person_rg_issuer())
