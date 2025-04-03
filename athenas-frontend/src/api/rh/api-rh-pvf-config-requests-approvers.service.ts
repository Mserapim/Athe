import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

export interface ApiRhPvfApprovalsRequestsPayload extends ListPayload {
    page?: number;
    keyword?: string;
}

export class ApiRhPvfConfigRequestsApproversResponseItem {
    value: number;
    label: string;
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsApproversResponseItem> {}

export async function apiRhPvfConfigRequestsApprovers(
    payload: ApiRhPvfApprovalsRequestsPayload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/requests/approvers/',
        payload
    );
    return data;
}
