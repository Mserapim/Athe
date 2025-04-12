def get_paycheck(employee, payroll):
    """Busca o ContraCheque do Servidor de acordo com a Folha enviada.
    Caso não encontre, cria-se um ContraCheque na Folha enviada.

    Arguments:
        employee -- object Servidor
        payroll -- object Folha

    Returns:
        object ContraCheque
    """

    q_paycheck = employee.paychecks.filter(folha=payroll)
    if q_paycheck.exists():
        return q_paycheck.first()
    else:
        return employee.paychecks.create(folha=payroll)


def create_entry(paycheck, event, **kwargs):
    """Utilizando o ContraCheque e o Evento enviados, cria-se um novo registro de FolhaEvento.
    E após a criação o ContraCheque é recalculado.

    Arguments:
        paycheck -- object ContraCheque
        event -- object Evento
        kwargs:
            qtd {float} -- quantidade
            qtd_max {float} -- quantidade máxima
            installments_paid {int} -- parcela
            installments {int} -- prazo
            pct {float} -- percentual
            value {float} -- valor
            base_value {float} -- valor base
            employer_value {float} -- patronal
            info {string} -- informações
            ref_year {int} -- ano de referência
            ref_month {int} -- mês de referência
            contribution_base {float} -- base previdenciária
            insertion_tipe {int} -- standard.models.Choice object id
    """

    paycheck.lancamentos.create(
        evento=event,
        qnt=kwargs.get("qtd", 0),
        qnt_max=kwargs.get("qtd_max", 0),
        parcela=kwargs.get("installments_paid", 0),
        installments_paid=kwargs.get("installments_paid", 0),
        prazo=kwargs.get("installments", 0),
        pct=kwargs.get("pct", 0),
        valor=kwargs.get("value", 0),
        correct_valor=kwargs.get("value", 0),
        valor_base=kwargs.get("base_value", 0),
        patronal=kwargs.get("employer_value", 0),
        correct_patronal=kwargs.get("employer_value", 0),
        info=kwargs.get("info", ""),
        reference_year=kwargs.get("ref_year", None),
        reference_month=kwargs.get("ref_month", None),
        base_previdencia=kwargs.get("contribution_base", 0),
        correct_base_previdencia=kwargs.get("contribution_base", 0),
        correct_value=kwargs.get("value", 0),
        correct_employer_contribution=kwargs.get("employer_value", 0),
        correct_qnt=kwargs.get("qtd", 0),
        correct_qnt_max=kwargs.get("qtd_max", 0),
        correct_pct=kwargs.get("pct", 0),
        correct_base_value=kwargs.get("base_value", 0),
        insertion_type=kwargs.get("insertion_type"),
    )
    paycheck.recalculate()
