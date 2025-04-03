import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

interface Payload {}

export class ApiVdfInfosTeletrabalhoBloqueadoServiceResponseItem {
    referencia: string;
    vigencia: string;
    motivo: string;
}

export class ApiVdfInfosTeletrabalhoBloqueadoServiceResponse extends ListPaginated<ApiVdfInfosTeletrabalhoBloqueadoServiceResponseItem> {}

export async function apiVdfInfosTeletrabalhoBloqueadoService(
    payload: Payload
) {
    const { data } =
        await useGet<ApiVdfInfosTeletrabalhoBloqueadoServiceResponse>(
            'vdf/infos-teletrabalho-bloqueado',
            payload
        );
    return data;
}
