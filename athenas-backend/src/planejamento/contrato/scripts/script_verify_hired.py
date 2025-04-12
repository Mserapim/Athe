import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from planejamento.contrato.models import Contrato
from planejamento.contrato.models import Hired


def create_hired():

    contratos_sem_pessoa = Contrato.objects.filter(pessoa__isnull=True)

    """ Caso 1 - Contrato não tem pessoa, mas tem Hired. """

    for contrato in contratos_sem_pessoa:
        for contrato_hired in contrato.hired.all():
            if contrato_hired.person is not None:
                contrato.pessoa.add(contrato_hired.person)
            # Copiar "hired" (person) pro contrato (pessoa).


def create_pessoa():

    contratos_com_pessoa = Contrato.objects.filter(
        pessoa__isnull=False
    )  # Selecionando apenas os contratos que possuem uma pessoa

    """ Caso 2 - Contrato tem pessoa, mas não tem Hired. """

    for contrato in contratos_com_pessoa:
        if not contrato.hired.exists():
            for pessoa in contrato.pessoa.all():
                data_inicio = contrato.data_inicio
                data_fim = contrato.data_vencimento
                hired = Hired(
                    agreement=contrato,
                    person=pessoa,
                    start_date=data_inicio,
                    end_date=data_fim,
                )
                hired.save()
                # Copiar "contrato" (pessoa) pro hired (person).


def remove_pessoa():

    contratos_com_pessoa = Contrato.objects.filter(
        pessoa__isnull=False
    )  # Selecionando apenas os contratos que possuem uma pessoa

    """ Caso 3 - Contrato tem pessoa, tem Hired, mas em quantidades diferentes. """

    for contrato in contratos_com_pessoa:
        hired_persons = []
        for hired in contrato.hired.all():
            hired_persons.append(hired.person)

        pessoas = contrato.pessoa.all()
        for pessoa in pessoas:
            if pessoa not in hired_persons:
                contrato.pessoa.remove(pessoa)
                # Atualizar a lista de pessoas.


if __name__ == "__main__":
    create_hired()
    create_pessoa()
    remove_pessoa()
