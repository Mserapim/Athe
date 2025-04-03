import { usePost } from 'api/@base/use-post';

interface Payload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

class Response {
    label: string;
    value: number;
}

export async function apiRhPvfConfigRequestsTeleworksTargetSituationsService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        `rh/pvf/config/requests/teleworks/target-situations`,
        payload
    );
    return data;
}
