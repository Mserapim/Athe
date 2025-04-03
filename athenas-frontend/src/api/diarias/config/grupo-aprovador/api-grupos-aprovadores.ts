import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasGruposAprovadoresPayload extends ListPayload {
}

export class ApiDiariasGruposAprovadoresItem {
    id: number;
    nome: string;
    quantidade_grupos: number;
    quantidade_servidores: number;
    criado_por_username: string;
    created_at: Date;
    modificado_por_username: string;
    modified_at: Date;
}

export class ApiDiariasGruposAprovadores extends ListPaginated<ApiDiariasGruposAprovadoresItem> {}

export async function apiDiariasGruposAprovadores(
    payload: ApiDiariasGruposAprovadoresPayload
) {
    const { data } = await useGet<ApiDiariasGruposAprovadores>(
        'diarias/config/grupos-aprovadores/',
        payload
    );

    return data;
}
