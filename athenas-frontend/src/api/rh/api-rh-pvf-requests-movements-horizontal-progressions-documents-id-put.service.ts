import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { usePut } from 'api/@base/use-put';

interface Payload extends ListPayload {
    id: number;
    pr_progression_h: number;
    description: string;
    attachment: number;
    doc_origin: number;
}

class Response {
    pk: number;
    pr_progression_h: number;
    pr_progression_h_str: string;
    description: string;
    attachment: number;
    doc_origin: number;
}

export async function apiRhPvfRequestsMovementsHorizontalProgressionsDocumentsPut(
    payload: Payload
) {
    const { data } = await usePut<Response>(
        `/athenas/api/v2/rh/pvf/requests/movements/horizontal-progressions/documents/${payload.id}`,
        payload
    );
    return data;
}
