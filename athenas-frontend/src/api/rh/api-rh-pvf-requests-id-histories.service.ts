import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsIdHistoriesResponseItem {
    pk: number;
    date: Date;
    group: string;
    employee: number;
    action_label: string;
    observation: string;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdHistoriesResponseItem> {}

export async function apiRhPvfRequestsIdHistories(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/requests/' + payload.requestId + '/histories',
        payload
    );
    return data;
}
