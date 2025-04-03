import { ListPaginated } from 'api/@base/list-paginated';
import { useDelete } from 'api/@base/use-delete';
import { usePost } from 'api/@base/use-post';

export interface ApiRhPvfRequestsSendingTimesheetsJustificationDeletePayload {
    id: number;
}

export class Response {}

export async function apiRhPvfRequestsSendingTimesheetsJustificationsDelete(
    payload: ApiRhPvfRequestsSendingTimesheetsJustificationDeletePayload
) {
    const { data } = await useDelete<Response>(
        'rh/pvf/requests/sending/timesheets/justifications/' + payload.id + '/'
    );
    return data;
}
