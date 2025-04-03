import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
}

export class ApiLimiteDiariasApagar {
    id: number;
}

export async function apiLimiteDiariasApagar(
    payload: Payload
) {
    const { data } = await usePost<ApiLimiteDiariasApagar>(
        'diarias/config/limite-diarias/apagar/',
        payload
    );

    return data;
}