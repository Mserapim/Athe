# -*- coding: utf-8 -*-
from contrib.decorator import ilru_cache
from rh.models import Lotacao, Servidor, ServidorLotacao

from contrib.utils import getLogger


log = getLogger(__name__)


@ilru_cache()
def my_replacement_substitute_vacation(
    self, date=None, owner=True, employee=None, workplace=None
):
    """
    :py:function:: my_replacement_substitute_vacation(self, date=None, owner=True)

    This method verifies substitutes that are at ExecutionOrgan.
    Considers EmployeeWorkplace.owner(ONLY) to True and date validity.

    :param date date - default is datetime.now().date()
    :param bool owner - default is True
    :param Employee employee:
    :param Workplace workplace:

    :return: QuerySet of Replacement
    :rtype: QuerySet
    """
    return self.my_replacement_substitute(
        date=date, owner=owner, employee=employee, workplace=workplace
    )


def my_replacement_employee_workplace_vacation(self):
    """
    :py:function:: my_replacement_employee_workplace_vacation(self)

    This method returns a ServidorLotacao QuerySet from my_replacement_substitute_vacation method.

    :return: QuerySet of EmployeeWorkplace
    :rtype: QuerySet
    """
    pks = (
        self.my_replacement_substitute_vacation()
        .values_list("substitute__servidores_lotacao__pk", flat=True)
        .distinct()
    )
    return ServidorLotacao.objects.filter(pk__in=pks, ativo=True)


def my_substitute_employee_vacation(self):
    """
    :py:function:: my_substitute_employee_vacation(self)

    This method returns a Servidor QuerySet from my_replacement_substitute_vacation method.

    :return: QuerySet of Servidor
    :rtype: QuerySet
    """
    registry = (
        reg
        for reg in self.my_replacement_substitute_vacation()
        .values_list("substitute__servidores_lotacao__servidor__matricula", flat=True)
        .distinct()
    )
    return Servidor.objects.filter(matricula__in=registry)


def my_substitute_workplace_vacation(self):
    """
    :py:function:: my_substitute_workplace_vacation(self)

    This method returns Workplace querset that substitutes a Employee according the replacement table.

    :return: queryset of Workplace
    :rtype: queryset of Workplace
    """
    pks = (
        pk
        for pk in self.my_replacement_substitute_vacation()
        .values_list("substitute__pk", flat=True)
        .distinct()
    )
    return Lotacao.objects.filter(pk__in=pks)


@ilru_cache()
def where_replacement_substitute_vacation(
    self, date=None, owner=True, employee=None, workplace=None
):
    """
    :py:function:: where_replacement_substitute_vacation(self, date=None, owner=True, employee=None, workplace=None)

    This method verifies substitutes that are at ExecutionOrgan.
    Considers EmployeeWorkplace.owner(ONLY) to True and date validity.

    :param date date: default is datetime.now().date()
    :param bool owner: default is True
    :param Employee employee:
    :param Workplace workplace:

    :return: QuerySet of Replacement
    :rtype: QuerySet
    """

    return self.where_replacement_substitute(
        date=date, owner=owner, employee=employee, workplace=workplace
    )


def where_substitute_employee_workplace_vacation(self):
    """
    :py:function:: where_substitute_employee_workplace_vacation(self)

    This method returns a ServidorLotacao QuerySet from where_replacement_substitute_vacation method.

    :return: QuerySet of EmployeeWorkplace
    :rtype: QuerySet
    """
    # return ServidorLotacao.objects.filter(
    #     pk__in=self.where_replacement_substitute_vacation().values('replaced__servidores_lotacao__pk'),
    #     ativo=True  # TODO: OBSERVAR SE O ATIVO PODE SER TRUE
    # ).distinct()

    query = self.where_replacement_substitute_vacation()
    employee_workplace = {}
    for q in query.order_by(
        "-replaced__servidores_lotacao__ativo", "-replaced__servidores_lotacao__owner"
    ).values(
        "replaced__servidores_lotacao__lotacao__pk",
        "replaced__servidores_lotacao__pk",
        "replaced__servidores_lotacao__owner",
    ):
        if q.get("replaced__servidores_lotacao__lotacao__pk") not in employee_workplace:
            employee_workplace.update(
                {
                    q.get("replaced__servidores_lotacao__lotacao__pk"): q.get(
                        "replaced__servidores_lotacao__pk"
                    )
                }
            )

    return ServidorLotacao.objects.exclude(servidor=self).filter(
        pk__in=employee_workplace.values(),
        ativo=True,  # TODO: OBSERVAR SE O ATIVO PODE SER TRUE
    )


def where_substitute_employee_vacation(self):
    """
    :py:function:: where_substitute_employee_vacation(self)

    This method returns a Servidor QuerySet from where_replacement_substitute_vacation method.

    :return: QuerySet of Servidor
    :rtype: QuerySet
    """
    # return Servidor.objects.filter(
    #     matricula__in=self.where_replacement_substitute_vacation().values('replaced__servidores_lotacao__servidor__matricula')
    # )
    return Servidor.objects.filter(
        matricula__in=self.where_substitute_employee_workplace_vacation().values(
            "servidor__matricula"
        )
    )


def where_substitute_workplace_vacation(self):
    """
    :py:function:: where_substitute_workplace_vacation(self)

    This method returns Workplace queryset where Employee substitutes according the replacement table.

    :return: queryset of Workplace
    :rtype: queryset of Workplace
    """
    return Lotacao.objects.filter(
        pk__in=self.where_replacement_substitute_vacation().values("replaced__pk")
    )


Servidor.my_replacement_substitute_vacation = my_replacement_substitute_vacation
Servidor.my_replacement_employee_workplace_vacation = (
    my_replacement_employee_workplace_vacation
)
Servidor.my_substitute_employee_vacation = my_substitute_employee_vacation
Servidor.my_substitute_workplace_vacation = my_substitute_workplace_vacation

Servidor.where_replacement_substitute_vacation = where_replacement_substitute_vacation
Servidor.where_substitute_employee_workplace_vacation = (
    where_substitute_employee_workplace_vacation
)
Servidor.where_substitute_employee_vacation = where_substitute_employee_vacation
Servidor.where_substitute_workplace_vacation = where_substitute_workplace_vacation
