import { usePost } from 'api/@base/use-post';

interface Payload {
    id: string;
    slug: string;
    path: string;
    title: string;
    description: string;
    name_object: string;
    typeof: string;
}

class Response {
    id: string;
    slug: string;
    path: string;
    title: string;
    description: string;
    name_object: string;
    typeof: string;
}

export async function apiPainelControleClasscodeEditar(payload: Payload) {
    const { data } = await usePost<Response>('adm/classcode/editar/', payload);
    return data;
}
