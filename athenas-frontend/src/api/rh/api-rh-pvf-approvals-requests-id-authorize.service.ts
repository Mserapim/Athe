import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
    action: string;
    observation?: string;
    publication?: number;
    documents?: {
        name: string;
        attachment_id: number;
    }[];
}

class Response {}

export async function apiRhPvfApprovalsRequestsIdAuthorize(payload: Payload) {
    const { data } = await usePost<Response>(
        '/rh/pvf/approvals/requests/' + payload.requestId + '/authorize/',
        payload
    );
    return data;
}
