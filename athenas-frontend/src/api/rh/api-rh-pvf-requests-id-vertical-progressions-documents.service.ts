import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id?: number;
}

export class ApiRhPvfRequestsIdVerticalProgressionsDocumentsItem {
    id: 0;
    description: string;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdVerticalProgressionsDocumentsItem> {}

export async function apiRhPvfRequestsIdVerticalProgressionsDocuments(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/requests/' + payload.id + '/vertical-progressions/documents/',
        payload
    );
    return data;
}
