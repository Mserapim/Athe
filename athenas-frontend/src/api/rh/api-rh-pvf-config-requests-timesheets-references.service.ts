import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    page?: number;
}

export class ApiRhPvfConfigRequestsTimesheetsReferencesResponseItem {
    reference: string;
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsTimesheetsReferencesResponseItem> {}

export async function apiRhPvfConfigRequestsTimesheetsReferences(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/timesheets/references/',
        payload
    );
    return data;
}
