import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

export interface Payload extends ListPayload {
    palavra_chave?: string;
    status?: string[];
    data_pgto_inicio?: Date;
    data_pgto_fim?: Date;
}

export class ApiDiariasPagamentosResponseItem {
    id:number;
    beneficiario: string;
    status: string;
    status_display: string;
    data_inicio_viagem: Date;
    servidor: string; 
    servidor_id: number; 
    info_conta_bancaria: string;
    valor_liquido_viagem: number;
    valor_liquido_deferido_viagem: number;
    data_pgto: string;
    cnab: string;
    assinado_por: string;
    assinado_em: DateTime;
    criado_por: number;
    created_at: DateTime;
    modificado_por: number;
    modified_at: DateTime;
}

class Response extends ListPaginated<ApiDiariasPagamentosResponseItem> {}

export async function apiDiariasPagamentos(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/pagamentos/',
        payload
    );
    return data;
}
