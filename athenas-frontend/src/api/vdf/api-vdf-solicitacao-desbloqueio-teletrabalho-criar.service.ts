import { usePost } from 'api/@base/use-post';

export interface ApiVdfSolicitacaoDesbloqueioTeletrabalhoCriarPayload {
    anexo_id: number;
    observacao: string;
}

export async function apiVdfSolicitacaoDesbloqueioTeletrabalhoCriar(
    payload: ApiVdfSolicitacaoDesbloqueioTeletrabalhoCriarPayload
) {
    const { data } = await usePost<any>(
        '/vdf/solicitacao-desbloqueio-teletrabalho/criar/',
        payload
    );
    return data;
}
