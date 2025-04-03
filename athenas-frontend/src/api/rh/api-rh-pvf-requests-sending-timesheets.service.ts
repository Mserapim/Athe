import { usePost } from 'api/@base/use-post';

interface Payload {}

class Response {}

export async function apiRhPvfRequestsSendingTimesheetsService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        `rh/pvf/requests/sending/timesheets/`,
        payload
    );
    return data;
}
