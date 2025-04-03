import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id?: number;
    palavra_chave?: string;
    status?: boolean;
}

export class ApiDiariasUsuariosItem {
    id: number;
    matricula: number;
    nome: string;
    username: string;
    status: boolean;
    unicode: string;
    grupos_aprovadores_viagens: string[];
}

export class ApiDiariasUsuarios extends ListPaginated<ApiDiariasUsuariosItem> {}

export async function apiDiariasUsuarios(payload: Payload) {
    const { data } = await useGet<ApiDiariasUsuarios>(
        'diarias/config/usuarios/',
        payload
    );

    return data;
}
