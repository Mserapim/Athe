import { usePost } from 'api/@base/use-post';

interface Payload {
    id: string;
    request_type: number;
    date: Date;
    status: number;
    step_current: number;
    portal_request_type: number;
    request: number;
    employee: number;
    approver: number;
    progression: number;
    config: number;
    publication: number;
}

class Response {
    id: number;
    request_type: number;
    date: Date;
    status: number;
    step_current: number;
    portal_request_type: number;
    request: number;
    employee: number;
    approver: number;
    progression: number;
    config: number;
    publication: number;
}

export async function apiRhPvfRequestsIdSendingProgressionsService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        `rh/pvf/requests/${payload.id}/sending-progressions`,
        payload
    );
    return data;
}
