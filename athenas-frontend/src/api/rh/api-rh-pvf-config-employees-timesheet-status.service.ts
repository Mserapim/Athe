import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    page: number;
}

export class ApiRhPvfConfigEmployeesTimesheetStatusResponseItem {
    timesheet_pending: boolean;
    timesheet_id: number;
    active_workplan: boolean;
}

export async function apiRhPvfConfigEmployeesTimesheetStatus(payload: Payload) {
    const { data } =
        await useGet<ApiRhPvfConfigEmployeesTimesheetStatusResponseItem>(
            '/rh/pvf/config/employees/timesheet/status/',
            payload
        );
    return data;
}
