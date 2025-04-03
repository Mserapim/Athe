import { usePost } from 'api/@base/use-post';

interface Payload {
    nome: string;
    grupos: number[];
}

export class ApiDiariasGrupoAprovadorCriar {
    id: number;
    nome: string;
    grupos: number[];
}

export async function apiDiariasGrupoAprovadorCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiDiariasGrupoAprovadorCriar>(
        'diarias/config/grupo-aprovador/criar/',
        payload
    );

    return data;
}