import { DateTime } from 'luxon';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    id: number;
    beneficiario: number;
    titulo: string;
    data_inicio: Date | string;
    data_fim: Date | string;
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

export async function apiDiariasEventoEditar(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        'diarias/viagem/evento/editar/',
        payload
    );
    return data;
}
