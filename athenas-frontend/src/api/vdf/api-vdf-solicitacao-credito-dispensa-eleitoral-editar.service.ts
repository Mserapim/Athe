import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number,
    data_inicio: string;
    data_fim: string;
    observacao: string;
    anexo: number;
}

class Response {
    data_inicio: string;
    data_fim: string;
    observacao: string;
    anexo: number;
}

export async function apiVdfSolicitacaoCreditoEleitoralEditarService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
            '/vdf/solicitacao-dispensa-eleitoral/editar/',
        payload
    );
    return data;
}
