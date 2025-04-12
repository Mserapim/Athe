from contrib.utils import getLogger
from rh.models import Servidor
from datetime import datetime
import base64


log = getLogger(__name__)


def get_data_report(params):
    data_dict = {}
    employee = Servidor.objects.get(pk=params["employee"])
    data_dict.update(
        {
            "NOME": employee.pessoa_fisica.nome,
            "MATRICULA": str(employee.matricula),
            "FILIAÇÃO": employee.pessoa_fisica.nome_pai
            + " \n"
            + employee.pessoa_fisica.nome_mae,
            "CPF": employee.pessoa_fisica.cpf,
            "NASCIMENTO": employee.pessoa_fisica.data_nascimento.strftime("%d/%m/%Y"),
            "RG": f"{employee.pessoa_fisica.rg} {employee.pessoa_fisica.rg_orgao}",
            "NATURALIDADE": str(employee.pessoa_fisica.municipio_naturalidade),
            "ALERGIA": "NÃO",
            "DOADOR": "SIM" if employee.pessoa_fisica.doador else "NÃO",
            "SANGUINEO": employee.pessoa_fisica.get_sangue_display()
            + employee.pessoa_fisica.get_fator_rh_display(),
            "EXPEDIÇÃO": datetime.today().date().strftime("%d/%m/%Y"),
            #'FOTO': return_image(employee.pessoa_fisica.foto),
            #'NOME':current_position(employee),
            "CARGO_ATUAL": current_position(employee),
        }
    )

    return data_dict


def current_position(employee):
    if employee.get_posses_ativas().count() > 0:
        if employee.get_is_comissionado():
            possesion = employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="CM"
            ).first()
            return possesion.quadro.cargo.nome
        elif employee.get_is_eletivo():
            possesion = employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="EL"
            ).first()
            return possesion.quadro.cargo.nome
        else:
            return employee.get_posses_ativas().first().quadro.cargo.nome

    return ""


def return_image(photo):
    if photo:
        with open(photo.absolute_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")
    return None
