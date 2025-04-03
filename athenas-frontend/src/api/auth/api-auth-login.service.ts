import { usePost } from 'api/@base/use-post';

interface Payload {
    app: string;
}

class Response {}

export async function authLoginService(payload: Payload) {
    const { data } = await usePost<Response>('/auth/login/', payload);
    return data;
}
