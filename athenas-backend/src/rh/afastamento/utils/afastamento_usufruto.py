from contrib.utils import getLogger
from rh.pvf.models import PortalRequestUsufruct

from rh.const import CANCELED, SCHEDULED

from rh.afastamento.models import (
    FolgaAniversario,
    FolgaEleitoral,
    Recesso,
)

from rh.dayoff.models import (
    Usufruct,
)
from standard.models import Choice

log = getLogger(__name__)


def criar_afastamento_usufruto(usufruto):
    """
    Cria ou associa um afastamento ao usufruto fornecido.

    Esta função verifica se já existe um afastamento associado ao servidor e à data de início do usufruto.
    Caso não exista, cria um novo afastamento com base na configuração do usufruto e atualiza o registro
    do usufruto para associá-lo ao afastamento criado. Se já existir um afastamento, apenas associa o
    usufruto ao afastamento existente.

    Args:
        usufruto (Usufruct): Objeto de usufruto que será utilizado para criar ou associar o afastamento.

    Comportamento:
        - Verifica se já existe um afastamento para o servidor e a data de início do usufruto.
        - Se não existir, cria um novo afastamento com os dados fornecidos pelo objeto `usufruto`.
        - Atualiza o campo `departure` do objeto `Usufruct` para associá-lo ao afastamento criado ou existente.

    Observações:
        - Para tipos específicos de afastamento, como `FolgaEleitoral`, `Recesso` e `FolgaAniversário`,
          são adicionados campos adicionais ao registro do afastamento.
        - O campo `origin_register` é definido com base na existência de uma solicitação no modelo
          `PortalRequestUsufruct`.

    Raises:
        Exception: Nenhuma exceção explícita é levantada, mas erros podem ocorrer caso os dados fornecidos
        estejam incompletos ou inconsistentes.

    Returns:
        None
    """

    _klass = usufruto.configuration.departure_class
    afastamentos = _klass.objects.filter(
        servidor=usufruto.employee, data_inicio=usufruto.start_date
    ).exclude(estado=CANCELED)

    if not afastamentos.exists():
        if PortalRequestUsufruct.objects.filter(activity=usufruto.activity).exists():
            origin_register = 1  # Vida Funcional
        else:
            origin_register = 4  # Gerenciador Admin
        _kargs = {
            "servidor": usufruto.employee,
            "data_inicio": usufruto.start_date,
            "data_prevista": usufruto.end_date,
            "data_fim": usufruto.end_date,
            "publicacao_movimentacao": None,
            "estado": SCHEDULED,
            "origin_register": origin_register,
        }
        if _klass == FolgaEleitoral:
            _kargs.update(
                {"ano": usufruto.acquisition_period.group_period.year_reference}
            )
            if Choice.objects.filter(
                app_label="rh",
                name="TURNO_ELEITORAL",
                value=usufruto.acquisition_period.group_period.period,
            ).exists():
                _kargs.update(
                    {"turno": usufruto.acquisition_period.group_period.period}
                )
        elif _klass == Recesso:
            _kargs.update(
                {"ano": usufruto.acquisition_period.group_period.year_reference}
            )
        elif _klass == FolgaAniversario:
            _kargs.update(
                {
                    "ano": usufruto.acquisition_period.group_period.year_reference,
                    "data_referencia": usufruto.acquisition_period.start_date_acquisition,
                }
            )

        afastamento = _klass.objects.create(**_kargs)

        log.info(
            f"Afastamento criado: {afastamento.pk} | {afastamento.__str_restful__()}"
        )

        Usufruct.objects.filter(pk=usufruto.pk).update(departure=afastamento)
    else:
        afastamento = afastamentos.last()
        log.info(
            f"Já possui afastamento({afastamentos.count()}): {afastamento.pk} | {afastamento.__str_restful__()}"
        )

        usufruto = Usufruct.objects.filter(pk=usufruto.pk).first()
        log.info(
            f"O  afastamento: {afastamento.__str_restful__()}, foi vinculado ao usufruto: {usufruto.__str__()}"
        )

        Usufruct.objects.filter(pk=usufruto.pk).update(departure=afastamento)
