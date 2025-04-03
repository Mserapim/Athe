import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

export interface ApiRhPvfRequestsSendingTimesheetsJustificationPayload {
    reason_type: number;
    number_hours: string;
    start_date: Date;
    end_date: Date;
    observation: string;
    attachment: number;
    request: number;
    origem: number;
}

export class ApiRhPvfRequestsSendingTimesheetsJustificationItem {
    value_key: number;
    name: string;
}

export class ApiRhPvfRequestsSendingTimesheetsJustificationResponse extends ListPaginated<ApiRhPvfRequestsSendingTimesheetsJustificationItem> {}

export async function apiRhPvfRequestsSendingTimesheetsJustifications(
    payload: ApiRhPvfRequestsSendingTimesheetsJustificationPayload
) {
    const { data } =
        await usePost<ApiRhPvfRequestsSendingTimesheetsJustificationResponse>(
            'rh/pvf/requests/sending/timesheets/justifications/',
            payload
        );
    return data;
}
