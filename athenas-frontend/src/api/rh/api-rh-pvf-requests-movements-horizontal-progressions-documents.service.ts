import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    keyword: string;
    id: number;
    per_page: number;
}

class ResponseItem {
    pk: number;
    pr_progression_h: number;
    pr_progression_h_str: string;
    description: string;
    attachment: number;
    doc_origin: number;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfRequestsMovementsHorizontalProgressionsDocuments(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        `/athenas/api/v2/rh/pvf/requests/movements/horizontal-progressions/documents/`,
        payload
    );
    return data;
}
