from rh.dayoff.const import CONF_DUTTY
from rh.dayoff.models import AcquisitionPeriod
from rh.pvf.const import USUFRUTO_PLANTAO_COMPENSATORIAS
from datetime import datetime


def get_period_aquisitivos_ordernados(periodos_acquisitivos):
    """
    Retorna os períodos aquisitivos ordenados
    Args:
        periodos_acquisitivos:queryset
    Returns:
        list: periodos_acquisitivos
    """
    return sorted(
        periodos_acquisitivos,
        key=lambda obj: (
            -datetime.combine(
                obj.start_date_acquisition, datetime.min.time()
            ).timestamp(),
            -datetime.combine(
                obj.end_date_acquisition, datetime.min.time()
            ).timestamp(),
            obj.get_saldo_venda,
            obj.days_not_booked_cache,
        ),
    )


def e_plantao_compensatoria(tipo_usufruto):
    if tipo_usufruto in USUFRUTO_PLANTAO_COMPENSATORIAS:
        return True
    return False


def ajustar_venda_plantoes(usufrutos, servidor):
    """
    Ajusta os usufrutos de venda de plantões
    Args:
        usufrutos: list
        servidor: instancia
    Returns:
        list:usufrutos
    """
    usufruto = usufrutos["usufructs_in"][0]
    if usufruto["sale_usufruct"] > 0:
        dias_vendidos = sum(usu.get("days", 0) for usu in usufrutos["usufructs_in"])
        usufrutos["usufructs_in"] = []
        periodos_acquisitivos = AcquisitionPeriod.objects.filter(
            group_period__configuration__type_of_usufruct=CONF_DUTTY,
            employee=servidor,
            days_not_booked_cache__gt=0,
        )
        period_acquisitivo_ordenados = get_period_aquisitivos_ordernados(
            periodos_acquisitivos
        )

        for periodo_aquisitivo in period_acquisitivo_ordenados[::-1]:
            saldo_dia_venda = dias_vendidos
            if dias_vendidos > periodo_aquisitivo.get_saldo_venda:
                saldo_dia_venda = periodo_aquisitivo.get_saldo_venda

            dias_vendidos = dias_vendidos - saldo_dia_venda
            if saldo_dia_venda > 0:
                usufrutos["usufructs_in"].append(
                    {
                        "days": saldo_dia_venda,
                        "sale_usufruct": usufruto["sale_usufruct"],
                    }
                )
    return usufrutos
