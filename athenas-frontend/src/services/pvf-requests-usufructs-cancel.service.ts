import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    usufructs_id: number;
    observation: string;
}

class Response {}

export async function pvfRequestsUsufructsCancelService(payload: Payload) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/usufructs/cancel/',
        payload
    );
    return data;
}
