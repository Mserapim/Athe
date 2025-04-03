import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    keyword?: string;
    servidor_id: number;
}

export class ResponseItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    tipo_conta: number;
    agencia: string;
    conta_completa: string;
    principal: boolean;
    banco: string;
    unicode: string;
    servidor: number;

    agencia_numero: string;
    agencia_dv: string;
    conta_numero: string;
    conta_dv: string;
    
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhDadosBancariosServidorContas(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/dados-bancarios/servidor/contas/',
        payload
    );
    return data;
}
