# -*- coding: utf-8 -*-

from rh.models import Servidor as Employee, Endereco as Address
from contrib.utils import DateUtils


def get_employee_job_position(employee):
    possessions = employee.posses_ativas

    job_position = possessions.last()
    if possessions.filter(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"]).exists():
        job_position = possessions.filter(
            quadro__cargo__tipo_lei_cargo__in=["CM", "FC"]
        ).last()
    job_position = job_position.quadro if job_position else "Cargo não encontrado"

    return job_position


def get_employee_exercise_date(employee):
    possessions = employee.posses_ativas

    job_position = possessions.last()
    if possessions.filter(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"]).exists():
        job_position = possessions.filter(
            quadro__cargo__tipo_lei_cargo__in=["CM", "FC"]
        ).last()

    exercise_date = "Data não encontrada"
    if job_position:
        exercise_date = job_position.data_exercicio
        exercise_date = DateUtils.date_to_str(exercise_date)

    return exercise_date


def get_employee_number(employee):
    """Retorna a matrícula do servidor."""
    if employee.matricula is not None:
        result = employee.matricula
    elif employee.matricula_origem is not None:
        result = employee.matricula_origem
    else:
        result = "Matrícula não encontrada"

    return str(result)


def get_employee_birth_date(employee):
    """Retorna a data de nascimento do servidor."""
    result = employee.pessoa_fisica.data_nascimento

    if result is not None:
        result = DateUtils.date_to_str(result)
    else:
        result = "Data não encontrada"

    return result


def get_employee_cpf(employee):
    """Retorna o CPF do servidor."""
    result = employee.pessoa_fisica.cpf

    if result is None:
        result = "CPF não encontrado"

    return result


def get_employee_rg(employee):
    """Retorna o número do RG do servidor."""
    result = employee.pessoa_fisica.rg

    if result is None:
        result = "RG não encontrado"

    return result


def get_employee_rg_origin(employee):
    """Retorna o orgão do RG do servidor."""
    result = employee.pessoa_fisica.rg_orgao

    if result is None:
        result = "Orgão não encontrado"

    return result


def get_employee_rg_date(employee):
    """Retorna a data de expedição do RG do servidor."""
    result = employee.pessoa_fisica.rg_data_expedicao

    if result is not None:
        result = DateUtils.date_to_str(result)
    else:
        result = "Data não encontrada"

    return result


def get_employee_father_name(employee):
    """Retorna o nome do pai do servidor."""
    result = employee.pessoa_fisica.nome_pai

    if result is None:
        result = "Nome não encontrado"

    return result


def get_employee_mother_name(employee):
    """Retorna o nome da mãe do servidor."""
    result = employee.pessoa_fisica.nome_mae

    if result is None:
        result = "Nome não encontrado"

    return result


def get_employee_blood(employee):
    """Retorna Tipo Sanguíneo + Fator Rh."""

    result = "{}{}".format(
        employee.pessoa_fisica.get_sangue_display(),
        "-" if employee.pessoa_fisica.fator_rh == 1 else "+",
    )

    return result


def get_employee_donor(employee):
    """Retorna SIM se servidor é doador, e NÃO caso contrário."""

    return "SIM" if employee.pessoa_fisica.doador else "NÃO"


def get_employee_address(employee):
    """Retorna o endereço mais recente do servidor público"""
    try:
        return employee.pessoa_fisica.address.latest("modified_at", "created_at")
    except Address.DoesNotExist:
        return "Não encontrado"


def get_employee_work_email(employee):
    """Retorna o email institucional do servidor público"""
    if employee.user.email and "@mpto.mp.br" in employee.user.email:
        return employee.user.email

    return "Não encontrado"
