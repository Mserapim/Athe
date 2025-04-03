import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
}

class Response {}

export async function apiRhPvfRequestsIdSendingTimesheetsService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        `rh/pvf/requests/${payload.id}/sending-timesheets/`,
        payload
    );
    return data;
}
