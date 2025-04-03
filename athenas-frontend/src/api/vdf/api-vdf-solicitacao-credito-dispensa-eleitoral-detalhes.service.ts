import { useGet } from 'api/@base/use-get';

interface Payload {
    id: number;
}

export class VdfSolicitacaoCreditoEleitoralDetalhes {
    id: number;
    dias: string;
    tipo_solicitacao_display: string;
    solicitante_display: string;
    data_inicio: string;
    data_fim: string;
    observacao: string;
    nome_anexo: string;
    obs_aprovador: string;
    anexo: number;
}

export async function apiVdfSolicitacaoCreditoEleitoralDetalhes(payload: Payload) {
    const { data } = await useGet<VdfSolicitacaoCreditoEleitoralDetalhes>(
        '/vdf/solicitacao-dispensa-eleitoral/',
        payload
    );
    return data;
}
