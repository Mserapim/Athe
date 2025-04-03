import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasConfigValoresPayload extends ListPayload {
    id?: number;
    valor_estado?: number;
    valor_fora_estado?: number;
    valor_exterior?: number;
    dt_inicio_vigencia?: Date;
    dt_fim_vigencia?: Date;
}

export class ApiDiariasConfigValoresItem {
    id?: number;
    valor_estado?: number;
    valor_fora_estado?: number;
    valor_exterior?: number;
    dt_inicio_vigencia?: Date;
    dt_fim_vigencia?: Date;
}

export class ApiDiariasConfigValores extends ListPaginated<ApiDiariasConfigValoresItem> {}

export async function apiDiariasConfigValores(
    payload: ApiDiariasConfigValoresPayload
) {
    const { data } = await useGet<ApiDiariasConfigValores>(
        'diarias/config/valores/',
        payload
    );

    return data;
}
