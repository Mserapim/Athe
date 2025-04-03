import { ListPayload } from 'api/@base/list-payload';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

export interface Payload extends ListPayload {
    id: number;
}


class Response extends ListPaginated<any> {}

export async function apiDiariasDestinoApagar(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        'diarias/viagem/destino/apagar/',
        payload
    );
    return data;
}