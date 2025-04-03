import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    id: number;
}

class ResponseItem {
    pk: number;
    pr_progression_h: number;
    pr_progression_h_str: string;
    description: string;
    attachment: number;
    doc_origin: number;
    doc_origin_display: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfRequestsIdHozirontalProgressionsDocuments(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        `rh/pvf/requests/${payload.id}/horizontal-progressions/documents/`,
        payload
    );
    return data;
}
