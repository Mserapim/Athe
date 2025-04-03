import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasGrupoAprovadorPayload extends ListPayload {
    id: number;
}

export class ApiDiariasGrupoAprovador {
    id: number;
    nome: string;
    grupos: number[];
}


export async function apiDiariasGrupoAprovador(
    payload: ApiDiariasGrupoAprovadorPayload
) {
    const { data } = await useGet<ApiDiariasGrupoAprovador>(
        'diarias/config/grupo-aprovador/',
        payload
    );

    return data;
}
