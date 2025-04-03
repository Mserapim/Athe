import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
}

export class ApiRhPvfRequestsIdExerciciosCumulativosDiasConsolidadosResponseItem {
    dias_consolidados: number;
}

class Response extends ApiRhPvfRequestsIdExerciciosCumulativosDiasConsolidadosResponseItem {}

export async function apiRhPvfRequestsIdExerciciosCumulativosDiasConsolidados(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/requests/' +
            payload.id +
            '/exercicios-cumulativos/dias-consolidados/'
    );
    return data;
}
