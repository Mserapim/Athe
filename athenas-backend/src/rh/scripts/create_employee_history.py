# -.- coding: utf-8 -.-
"""
    Este script criar NaturalPersonHistory.
"""

import os
from datetime import date

import django

from rh.const import TYPE_PHONE_EMERGENCY

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from contrib.middleware import set_current_user
from rh.models import Endereco, NaturalPersonHistory, Servidor, Telefone

_fill_from_instance_original = NaturalPersonHistory._fill_from_instance
_values_from_instance_original = NaturalPersonHistory._values_from_instance
_when_original = NaturalPersonHistory._when


def _values_from_instance(instance):
    values = {}
    for f in instance._meta.fields:
        values.update({f.name: (getattr(instance, f.name),)})
    return values


def _when(*args):
    # employee = None
    # if isinstance(args[0], (Endereco, Telefone)):
    #     employee = args[0].person.pessoafisica.servidor_set.filter(ativo=True).last()
    # if isinstance(args[0], PessoaFisica):
    #     employee = args[0].servidor_set.filter(ativo=True).last()
    # return employee.exercise_date if employee else date.today()
    # return datetime(2022, 5, 26).date()
    return date.today()


def _fill_from_instance(instance):
    values = _fill_from_instance_original(instance)
    values.update({"when": NaturalPersonHistory._when(instance)})
    return values


def _create_address(natural_person, setup=True):
    """address"""
    _set_up(setup=setup)
    address = Endereco.objects.filter(person__pessoafisica=natural_person).last()
    if address:
        NaturalPersonHistory.write_history(address)
    _tear_down(setup=setup)


def _create_phone(natural_person, setup=True):
    """phone"""
    _set_up(setup=setup)
    phone = Telefone.objects.filter(
        person__pessoafisica=natural_person, main=True
    ).last()
    if phone:
        NaturalPersonHistory.write_history(phone)

    phone = Telefone.objects.filter(
        person__pessoafisica=natural_person, tipo_telefone=TYPE_PHONE_EMERGENCY
    ).last()
    if phone:
        NaturalPersonHistory.write_history(phone)
    _tear_down(setup=setup)


def _create_natural_person(natural_person, setup=True):
    """natural_person"""
    _set_up(setup=setup)
    NaturalPersonHistory.write_history(natural_person)
    _tear_down(setup=setup)


def create_natural_person_history(natural_person, setup=True):

    _create_address(natural_person, setup=setup)
    _create_phone(natural_person, setup=setup)
    _create_natural_person(natural_person, setup=setup)


def _set_up(setup=True):
    if setup:
        NaturalPersonHistory._fill_from_instance = _fill_from_instance
        NaturalPersonHistory._values_from_instance = _values_from_instance
        NaturalPersonHistory._when = _when


def _tear_down(setup=True):
    if setup:
        NaturalPersonHistory._fill_from_instance = _fill_from_instance_original
        NaturalPersonHistory._values_from_instance = _values_from_instance_original
        NaturalPersonHistory._when = _when_original


def run():
    NaturalPersonHistory.objects.filter(
        natural_person__servidor__type_by_possession__in=("MAP", "SAP")
    ).delete()
    query = Servidor.objects.filter(type_by_possession__in=("MAP", "SAP"), ativo=True)
    for employee in query:
        try:
            print(employee)
            create_natural_person_history(employee.pessoa_fisica)
        except Exception as err:
            print(employee.pessoa_fisica)
            print(err)

    for nph in NaturalPersonHistory.objects.all():
        print(nph)


if __name__ == "__main__":
    set_current_user("athenas")
    run()
