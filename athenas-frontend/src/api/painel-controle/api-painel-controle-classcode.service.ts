import { useGet } from 'api/@base/use-get';

interface Payload {
    id: number | string;
}

export class Response {
    id: number;
    slug: string;
    path: string;
    title: string;
    description: string;
    name_object: string;
    typeof: string;
}

export async function apiPainelControleClasscode(payload: Payload) {
    const { data } = await useGet<Response>('adm/classcode/', payload);
    return data;
}
