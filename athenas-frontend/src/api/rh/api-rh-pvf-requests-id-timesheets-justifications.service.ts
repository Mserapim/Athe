import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    page?: number;
    per_page?: number;
    cancelado?: boolean;
}

export class ApiRhPvfRequestsIdTimesheetsJustificationsItem {
    pk: number;
    reason_type: number;
    number_hours: string;
    start_date: Date;
    end_date: Date;
    observation: string;
    attachment: number;
    canceled: boolean;
    request: number;
    origem: number;
}

export class ApiRhPvfRequestsIdTimesheetsJustificationsResponse extends ListPaginated<ApiRhPvfRequestsIdTimesheetsJustificationsItem> {}

export async function apiRhPvfRequestsIdTimesheetsJustifications(
    payload: Payload
) {
    const { data } =
        await useGet<ApiRhPvfRequestsIdTimesheetsJustificationsResponse>(
            '/rh/pvf/requests/' + payload.id + '/timesheets/justifications/',
            payload
        );
    return data;
}
