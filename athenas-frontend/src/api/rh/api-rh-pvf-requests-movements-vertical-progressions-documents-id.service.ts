import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';
import { useDelete } from 'api/@base/use-delete';

interface Payload extends ListPayload {
    id?: string;
}

export class Response {}

export async function apiRhPvfRequestsMovementsVerticalProgressionsDocuments(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/requests/movements/vertical-progressions/documents/' +
            payload.id,
        payload
    );
    return data;
}
