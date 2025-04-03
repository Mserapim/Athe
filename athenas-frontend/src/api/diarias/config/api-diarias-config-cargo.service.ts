import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasConfigCargoPayload extends ListPayload {
    id?: number;
    nome?: string;
}

export class ApiDiariasConfigCargo {
    id?: number;
    nome?: string;
}

export async function apiDiariasConfigCargo(
    payload: ApiDiariasConfigCargoPayload
) {
    const { data } = await useGet<ApiDiariasConfigCargo>(
        'diarias/config/cargo/',
        payload
    );

    return data;
}
