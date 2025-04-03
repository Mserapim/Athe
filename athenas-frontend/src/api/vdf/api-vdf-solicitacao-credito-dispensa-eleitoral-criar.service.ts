import { usePost } from 'api/@base/use-post';

interface Payload {
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

export async function apiVdfSolicitacaoCreditoEleitoralCriarService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
            '/vdf/solicitacao-dispensa-eleitoral/criar/',
        payload
    );
    return data;
}
