import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiLimitesDiariasPayload extends ListPayload {
}

export class ApiLimitesDiariasItem {
    id: number;
    tipo: string;
    tipo_display: string;
    referencia: string;
    referencia_display: string;
    motivos_viagem: number[];
    motivos_viagem_display: string;
    limite: number;
    dt_inicio_vigencia: Date;
    criado_por_username: string;
    created_at: Date;
    modificado_por_username: string;
    modified_at: Date;
}

export class ApiLimitesDiarias extends ListPaginated<ApiLimitesDiariasItem> {}

export async function apiLimitesDiarias(
    payload: ApiLimitesDiariasPayload
) {
    const { data } = await useGet<ApiLimitesDiarias>(
        'diarias/config/limites-diarias/',
        payload
    );

    return data;
}
