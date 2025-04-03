import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    nome: string;
}

export class ApiDiariasConfigCargoEditar {
    id: number;
    nome: string;
}

export async function apiDiariasConfigCargoEditar(
    payload: Payload
) {
    const { data } = await usePost<ApiDiariasConfigCargoEditar>(
        'diarias/config/cargo/editar/',
        payload
    );

    return data;
}
