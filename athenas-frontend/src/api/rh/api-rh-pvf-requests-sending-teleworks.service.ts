import { usePost } from 'api/@base/use-post';

interface Payload {}

class Response {}

export async function apiRhPvfRequestsSendingTeleworksService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        `rh/pvf/requests/sending/teleworks/`,
        payload
    );
    return data;
}
