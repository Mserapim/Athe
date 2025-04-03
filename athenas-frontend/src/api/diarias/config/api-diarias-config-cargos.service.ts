import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasConfigCargosPayload extends ListPayload {
    id?: number;
    nome?: string;
    palava_chave?: string;
}

export class ApiDiariasConfigCargosItem {
    id?: number;
    nome?: string;
}

export class ApiDiariasConfigCargos extends ListPaginated<ApiDiariasConfigCargosItem> {}

export async function apiDiariasConfigCargos(
    payload: ApiDiariasConfigCargosPayload
) {
    const { data } = await useGet<ApiDiariasConfigCargos>(
        'diarias/config/cargos/',
        payload
    );

    return data;
}
