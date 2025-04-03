import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
}

export class ApiDiariasGrupoAprovadorApagar {
    id: number;
}

export async function apiDiariasGrupoAprovadorApagar(
    payload: Payload
) {
    const { data } = await usePost<ApiDiariasGrupoAprovadorApagar>(
        'diarias/config/grupo-aprovador/apagar/',
        payload
    );

    return data;
}
