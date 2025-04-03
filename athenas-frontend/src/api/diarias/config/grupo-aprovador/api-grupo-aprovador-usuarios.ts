import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface PayloadGrupoDiarias extends ListPaginated<any> {
    id?: number;
    palavra_chave?: string;
    grupo_id?: number;
    status?: boolean;
}

export class ApiDiariasGrupoAprovadorUsuariosItem {
    id: number;
    matricula: number;
    nome: string;
    username: string;
    status: boolean;
    unicode: string;
    grupos_aprovadores_viagens: string[];
}

export class ApiDiariasGrupoAprovadorUsuarios extends ListPaginated<ApiDiariasGrupoAprovadorUsuariosItem> {}

export async function apiDiariasGrupoAprovadorUsuarios(payload: PayloadGrupoDiarias) {
    const { data } = await useGet<ApiDiariasGrupoAprovadorUsuarios>(
        'diarias/config/grupo-aprovador/usuarios/',
        payload
    );

    return data;
}
