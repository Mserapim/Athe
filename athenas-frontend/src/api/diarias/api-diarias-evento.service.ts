import { DateTime } from 'luxon';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    id: number;
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

export async function apiDiariasEvento(
    payload: Payload
) {
    const { data } = await useGet<ResponseItem>(
        'diarias/viagem/evento/',
        payload
    );
    return data;
}
