import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasConfigValorPayload extends ListPayload {
    id?: number;
    valor_estado?: number;
    valor_fora_estado?: number;
    valor_exterior?: number;
    dt_inicio_vigencia?: string;
    dt_fim_vigencia?: string;
}

export class ApiDiariasConfigValor {
    id?: number;
    valor_estado?: number;
    valor_fora_estado?: number;
    valor_exterior?: number;
    dt_inicio_vigencia?: string;
    dt_fim_vigencia?: string;
}

export async function apiDiariasConfigValor(
    payload: ApiDiariasConfigValorPayload
) {
    const { data } = await useGet<ApiDiariasConfigValor>(
        'diarias/config/valor/',
        payload
    );

    return data;
}
