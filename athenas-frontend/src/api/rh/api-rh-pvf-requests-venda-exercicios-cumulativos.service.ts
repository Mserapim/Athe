import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    substituicoes_ids: string[];
    observacao: string;
}

class ResponseItem {}

export async function apiRhPvfRequestsVendaExerciciosCumulativos(
    payload: Payload
) {
    const { data } = await usePost<ResponseItem>(
        'rh/pvf/requests/venda/exercicios-cumulativos/',
        payload
    );
    return data;
}
