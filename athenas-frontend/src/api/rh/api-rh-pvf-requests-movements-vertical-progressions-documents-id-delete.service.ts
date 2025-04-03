import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';
import { useDelete } from 'api/@base/use-delete';

interface Payload {
    id?: number;
}

export class Response {}

export async function apiRhPvfRequestsMovementsVerticalProgressionsDocumentsDelete(
    payload: Payload
) {
    const { data } = await useDelete<Response>(
        'rh/pvf/requests/movements/vertical-progressions/documents/' +
            payload.id,
        payload
    );
    return data;
}
