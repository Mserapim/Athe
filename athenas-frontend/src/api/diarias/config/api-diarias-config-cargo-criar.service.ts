import { usePost } from 'api/@base/use-post';

interface Payload {
    nome: string;
}

export class ApiDiariasConfigCargoCriar {
    pk: number;
    nome: string;
}

export async function apiDiariasConfigCargoCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiDiariasConfigCargoCriar>(
        'diarias/config/cargo/criar/',
        payload
    );

    return data;
}
