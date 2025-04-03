import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
    nome?: string;
}

export class ApiDiariasConfigCargoApagar {
    id: number;
    nome: string;
}

export async function apiDiariasConfigCargoApagar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiDiariasConfigCargoApagar>(
            'diarias/config/cargo/apagar/',
            payload
        );

    return data;
}
