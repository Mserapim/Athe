import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiLimiteDiariasPayload extends ListPayload {
    id: number;
}

export class ApiLimiteDiarias {
    id: number;
    tipo: string;
    referencia: string;
    motivos_viagem: number[];
    limite: number;
    dt_inicio_vigencia: string;
}

export async function apiLimiteDiarias(
    payload: ApiLimiteDiariasPayload
) {
    const { data } = await useGet<ApiLimiteDiarias>(
        'diarias/config/limite-diarias/',
        payload
    );

    return data;
}
