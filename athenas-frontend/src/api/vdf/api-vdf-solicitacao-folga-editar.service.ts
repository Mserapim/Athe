import { usePost } from 'api/@base/use-post';

export interface ApiVdfSolicitacaoFolgaEditarPayload {
    data_inicio: Date;
    data_fim: Date;
    id:number;
    tipo_folga:number,
    observation: string;
}

class Response {
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver: number;
    status_name: string;
}

export async function apiVdfSolicitacaoFolgaEditarService(
    payload: ApiVdfSolicitacaoFolgaEditarPayload
) {
    const { data } = await usePost<Response>(
        '/vdf/solicitacao-folga/editar/',
        payload
    );
    return data;
}
