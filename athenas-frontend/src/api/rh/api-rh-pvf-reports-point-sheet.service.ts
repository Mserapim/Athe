import { usePost } from 'api/@base/use-post';

interface Payload {
    month?: number;
    year?: number;
}

class Response {
    message: string;
    success: boolean;
    uuid: string;
}

export async function apiRhPvfReportsPointSheet(payload: Payload) {
    const { data } = await usePost<Response>(
        'report/rh/pvf/folha-ponto/',

        payload
    );
    return data;
}
