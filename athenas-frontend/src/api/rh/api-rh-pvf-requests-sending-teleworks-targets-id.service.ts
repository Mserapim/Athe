import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    total_completed: number;
    mark_situation: number;
    observation: string;
    request: number;
}

class ResponseItem {
    id: number;
    total_completed: number;
    mark_situation: number;
    observation: string;
    mark_plan: number;
    request: 0;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfRequestsSendingTeleworksTargetsId(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        '/rh/pvf/requests/sending/teleworks/targets/' + payload.id,
        payload
    );
    return data;
}
