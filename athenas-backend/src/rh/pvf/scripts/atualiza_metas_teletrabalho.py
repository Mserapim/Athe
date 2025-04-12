from rh.pvf.models import SendingTelework


def atualiza_metas():
    """Script que atualiza as metas adicionando o anexo da referencia 2/2024"""
    solicitacoes_teletrabalho = SendingTelework.objects.filter(
        reference_month=2, reference_year=2024
    )
    for solicitacao in solicitacoes_teletrabalho:
        if solicitacao.anexo:
            meta = solicitacao.pvf_request_telework.last()
            if meta:
                meta.anexo = solicitacao.anexo
                meta.save(validate_prevent=False)
                print(f"{meta} - Atualizada com sucesso")
