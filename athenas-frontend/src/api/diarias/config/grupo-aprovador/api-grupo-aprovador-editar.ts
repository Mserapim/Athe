import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    nome?: string;
    grupos?: number[];
    servidores?: any[];
}

export class ApiDiariasGrupoAprovadorEditar {
    id: number;
    nome: string;
    grupos: number[];
    servidores?: any[];
}

export async function apiDiariasGrupoAprovadorEditar(
    payload: Payload
) {
    const { data } = await usePost<ApiDiariasGrupoAprovadorEditar>(
        'diarias/config/grupo-aprovador/editar/',
        payload
    );

    return data;
}