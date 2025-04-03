import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    keyword?: string;
    id: number;
}

class ApiRhPvfRequestsMovementsHorizontalProgressionsDocumentsIdItem {
    pk: number;
    pr_progression_h: number;
    pr_progression_h_str: string;
    description: string;
    attachment: number;
    doc_origin: number;
}

class Response extends ListPaginated<ApiRhPvfRequestsMovementsHorizontalProgressionsDocumentsIdItem> {}

export async function apiRhPvfRequestsMovementsHorizontalProgressionsDocumentsId(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        `/rh/pvf/requests/movements/horizontal-progressions/documents/${payload.id}`,
        payload
    );
    return data;
}
