import { usePost } from 'api/@base/use-post';

interface Payload {
    slug: string;
    path: string;
    title: string;
    description: string;
    name_object: string;
    typeof: string;
}

class Response {
    id: number;
    slug: string;
    path: string;
    title: string;
    description: string;
    name_object: string;
    typeof: string;
}

export async function apiPainelControleClasscodeCriar(payload: Payload) {
    const { data } = await usePost<Response>('adm/classcode/criar/', payload);
    return data;
}
