import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    request_id?: string;
    description?: string;
    attachment?: number;
}

export class Response {
    pk: number;
    progression: number;
    description: string;
    attachment: number;
    doc_origin: 32767;
}

export async function apiRhPvfRequestsMovementsVerticalProgressionsDocuments(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        'rh/pvf/requests/movements/vertical-progressions/documents/',
        payload
    );
    return data;
}
