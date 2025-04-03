import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
}

export class ApiRhPvfRequestsIdExerciciosCumulativosSubstituicoesResponseItem {
    id: number;
    serv_substituto: string;
    serv_substituido: string;
    data_inicio: Date;
    data_fim: Date;
    cumulativa: string;
    able_to_pay: boolean;
    pay_month: number;
    pay_year: number;
    paid_out: boolean;
    dias_consolidados: number;
    indeferido: boolean;
    status_label: string;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdExerciciosCumulativosSubstituicoesResponseItem> {}

export async function apiRhPvfRequestsIdExerciciosCumulativosSubstituicoes(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/requests/' +
            payload.id +
            '/exercicios-cumulativos/substituicoes/',
        payload
    );
    return data;
}
