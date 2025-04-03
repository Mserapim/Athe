import { ListPayload } from 'api/@base/list-payload';
import { useDelete } from 'api/@base/use-delete';

interface Payload extends ListPayload {
    id: number;
}

class Response {
    pk: number;
    pr_progression_h: number;
    pr_progression_h_str: string;
    description: string;
    attachment: number;
    doc_origin: number;
}

export async function apiRhPvfRequestsMovementsHorizontalProgressionsDocumentsDelete(
    payload: Payload
) {
    const { data } = await useDelete<Response>(
        `/athenas/api/v2/rh/pvf/requests/movements/horizontal-progressions/documents/${payload.id}`,
        payload
    );
    return data;
}
