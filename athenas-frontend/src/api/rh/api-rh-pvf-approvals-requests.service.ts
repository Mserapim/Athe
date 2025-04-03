import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

export interface ApiRhPvfApprovalsRequestsPayload extends ListPayload {
    page?: number;
    approvals?: number[];
    employe_types?: number[];
    keyword?: string;
    request_type?: number[];
    status?: number[];
    pending_request?: boolean;
}

export class ApiRhPvfApprovalsRequestsResponseItem {
    pk: number;
    portal_request_type: number;
    type_of_request: string;
    date: Date;
    employee: number;
    employee_name: string;
    status: number;
    status_name: string;
    step_current: number;
    step_current_name: string;
    approver: number;
    approver_name: string;
    parcel_number: number;
    acquisitive_period: string;
    days_awaiting_approval: string;
    reference: string;
}

class Response extends ListPaginated<ApiRhPvfApprovalsRequestsResponseItem> {}

export async function apiRhPvfApprovalsRequests(
    payload: ApiRhPvfApprovalsRequestsPayload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/approvals/requests/',
        payload || {}
    );
    return data;
}
