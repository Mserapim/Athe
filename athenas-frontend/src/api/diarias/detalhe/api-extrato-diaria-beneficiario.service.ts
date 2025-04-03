import { DateTime } from 'luxon';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    beneficiario_id: number;
}

export class ResponseItem {
    base_calculo: any[];
    consolidado: any[];
    excedente: any[];
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasExtrato(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/viagem/detalhe/beneficiario/destinos-detalhado',
        payload
    );
    return data;
}
