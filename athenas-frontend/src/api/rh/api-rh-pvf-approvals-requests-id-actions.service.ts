import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

export interface ApiRhPvfApprovalsRequestsIdActionsPayload extends ListPayload {
    requestId?: number;
    keyword?: string;
    per_page?: number;
}

export class ApiRhPvfApprovalsRequestsIdActionsResponseItem {
    label: number;
    action: string;
    disabled: boolean;
}

class Response extends ListPaginated<ApiRhPvfApprovalsRequestsIdActionsResponseItem> {}

export async function apiRhPvfApprovalsRequestsIdActions(
    payload: ApiRhPvfApprovalsRequestsIdActionsPayload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/approvals/requests/' + payload.requestId + '/actions',
        payload
    );
    return data;
}
