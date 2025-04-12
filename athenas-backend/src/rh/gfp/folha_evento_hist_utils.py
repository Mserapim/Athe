from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger, comparar_querys

from rh.gfp.models import ContraChequeHistorico, FolhaEventoHistorico

log = getLogger(__name__)


def criar_hist_contracheque(contracheque):
    q_cc_hist = buscar_cc_historico(contracheque)
    if q_cc_hist.exists() is False:
        cc_hist_novo = criar_historico(contracheque)
    else:
        cc_hist = q_cc_hist.order_by("-created_at").first()
        fe_hist = cc_hist.historico_lancamentos.all()

        cc_hist_novo = criar_historico(contracheque)
        fe_hist_novo = cc_hist_novo.historico_lancamentos.all()
        if comparar_querys(fe_hist_novo, fe_hist, ["contracheque_historico_id"]):
            apagar_hist_contracheque(cc_hist_novo)


def criar_historico(contracheque):
    set_current_user(get_current_user())

    cc_hist = ContraChequeHistorico.objects.create(
        contracheque=contracheque,
        contracheque_ref_id=contracheque.pk,
        servidor_ref_id=contracheque.servidor.pk,
        contracheque_ref_ano=contracheque.folha.periodo.ano,
        contracheque_ref_mes=contracheque.folha.periodo.mes,
    )
    criar_hist_folhaevento(cc_hist, contracheque.lancamentos.all())

    return cc_hist


def criar_hist_folhaevento(cc_hist, lancamentos):
    for fe in lancamentos:
        FolhaEventoHistorico.objects.create(
            contracheque_historico=cc_hist,
            evento=fe.evento,
            lancamento=fe.lancamento,
            qnt=fe.qnt,
            qnt_max=fe.qnt_max,
            parcela=fe.parcela,
            prazo=fe.installments_paid,
            pct=fe.pct,
            valor=fe.correct_value,
            valor_base=fe.valor_base,
            patronal=fe.patronal,
            info=fe.info,
            base_previdencia=fe.base_previdencia,
            status=fe.status,
            json_calc_vars=fe.json_calc_vars,
            automated=fe.automated,
            insertion_type=fe.insertion_type,
        )


def buscar_cc_historico(contracheque):
    return ContraChequeHistorico.objects.filter(
        contracheque__folha__periodo__ano=contracheque.folha.periodo.ano,
        contracheque__folha__periodo__mes=contracheque.folha.periodo.mes,
    )


def apagar_hist_contracheque(cc_hist):
    cc_hist.historico_lancamentos.filter().delete()
    cc_hist.delete()
