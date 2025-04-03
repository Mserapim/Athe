import { DateTime } from 'luxon';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    beneficiario: number;
}

export class ResponseItem {
    id: number;
    beneficiario: number;
    titulo: string;
    data_inicio: Date;
    data_fim: Date;
    destinos: any[];
    created_at: DateTime;
    modified_at: DateTime;
    created_by: number;
    modified_by: number;
    unicode: string;

}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasEventos(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/viagem/eventos/',
        payload
    );
    return data;
}
