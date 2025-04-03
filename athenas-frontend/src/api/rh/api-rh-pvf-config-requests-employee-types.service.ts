import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

export interface ApiRhPvfConfigRequestsEmployeeTypesPayload
    extends ListPayload {
    page?: number;
    keyword?: string;
}

export class ApiRhPvfConfigRequestsEmployeeTypesResponseItem {
    label: string;
    value: string;
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsEmployeeTypesResponseItem> {}

export async function apiRhPvfConfigRequestsEmployeeTypes(
    payload: ApiRhPvfConfigRequestsEmployeeTypesPayload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/requests/employee-types/',
        payload || {}
    );
    return data;
}
