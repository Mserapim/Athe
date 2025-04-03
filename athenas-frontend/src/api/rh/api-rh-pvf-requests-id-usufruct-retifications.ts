import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    requestId?: number;
}

export class ApiRhPvfRequestsIdUsufructRetificationsResponseItem {
    pk: number;
    start: Date;
    end: Date;
    title: string;
    eventType: string;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdUsufructRetificationsResponseItem> {}

export async function apiRhPvfRequestsIdUsufructRetificationsService(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        '/rh/pvf/requests/' + payload.requestId + '/usufruct-retifications',
        payload
    );
    return data;
}
