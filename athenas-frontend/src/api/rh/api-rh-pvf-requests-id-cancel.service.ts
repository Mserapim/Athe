import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

class Response {}

export async function apiRhPvfRequestsIdCancelService(payload: Payload) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/' + payload.requestId + '/cancel/',
        payload
    );
    return data;
}
