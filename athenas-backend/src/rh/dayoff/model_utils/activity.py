from contrib.utils import getLogger

log = getLogger(__name__)


def set_pagamento_usufruto_retificado_suspensao(
    usufruto, existe_pagamento, periodo=False, usufruto_anterior=False
):
    if existe_pagamento and not periodo:
        usufruto.payment_month = None
        usufruto.payment_year = None
        usufruto.save_base()
    set_pagamento_de_competencia_baseado_em_periodo(
        periodo, usufruto, usufruto_anterior
    )


def set_pagamento_usufruto_futuro(usufruto):
    """
    Usufruto com data futura: Competência de pagamento do
    Usufruto será 1 mês antes do usufruto e abono no mês de usufruto
    """
    parcela_de_pagamento = usufruto.payment_installments
    if parcela_de_pagamento == 1:
        usufruto.payment_month = usufruto.start_date.month - 1
        usufruto.payment_year = usufruto.start_date.year

        if usufruto.start_date.month == 1:
            usufruto.payment_month = 12
            usufruto.payment_year = usufruto.start_date.year - 1
    elif parcela_de_pagamento == 2:
        usufruto.payment_month = usufruto.start_date.month
        usufruto.payment_year = usufruto.start_date.year

    usufruto.save_base()


def set_pagamento_de_competencia_baseado_em_periodo(
    periodo, usufruto, usufruto_anterior=False
):
    """
    Função para setar pagamento da competencia baseada no periodo utilizando
    a data corte ferias, onde a data de solicitacao é a data de criação
    do usufruto.
    """

    data_solicitacao = usufruto.created_at.date()
    data_corte = periodo.data_corte_ferias

    if data_corte >= data_solicitacao:
        usufruto.payment_year = data_solicitacao.year
        usufruto.payment_month = data_solicitacao.month
    elif data_solicitacao > data_corte:
        usufruto.payment_year = data_solicitacao.year
        usufruto.payment_month = data_solicitacao.month + 1

        if data_solicitacao.month == 12:
            usufruto.payment_year = data_solicitacao.year + 1
            usufruto.payment_month = 1

    if usufruto_anterior:
        usufruto_anterior.payment_year = None
        usufruto_anterior.payment_month = None
        usufruto_anterior.save_base()

    usufruto.save_base()
