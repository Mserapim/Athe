import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    extension: 'XLS' | 'PDF';
}

class ResponseItem {
    uuid: string;
}

export async function apiReportRhPvfApprovers(payload: Payload) {
    const { data } = await usePost<ResponseItem>(
        'report/rh/pvf/approvers/',
        payload
    );
    return data;
}
