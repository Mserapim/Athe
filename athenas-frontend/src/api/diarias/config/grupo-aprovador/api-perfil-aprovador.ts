import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasPerfilAprovadorPayload extends ListPayload {
    id?: number;
}
export class ApiDiariasPerfilAprovadorItem {
    id: number;
    matricula: number;
    nome: string;
    unicode: string;
    grupos: string[];
    etapas_aprovador: number[];
    etapas_aprovador_obj: any[];
}

export async function apiDiariasPerfilAprovador(
    payload: ApiDiariasPerfilAprovadorPayload
) {
    const { data } = await useGet<ApiDiariasPerfilAprovadorItem>(
        'diarias/config/perfil-aprovador/',
        payload
    );

    return data;
}
