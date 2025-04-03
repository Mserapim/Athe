import { usePost } from 'api/@base/use-post';

export interface ApiVdfSolicitacaoFolgaPayload {
    data_inicio: Date;
    data_fim: Date;
    tipo_folga:number,
    anexo: number;
    observation: string;
}

class Response {
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver: number;
    status_name: string;
}

export async function apiVdfSolicitacaoFolgaService(
    payload: ApiVdfSolicitacaoFolgaPayload
) {
    const { data } = await usePost<Response>(
        '/vdf/solicitacao-folga/criar/',
        payload
    );
    return data;
}
