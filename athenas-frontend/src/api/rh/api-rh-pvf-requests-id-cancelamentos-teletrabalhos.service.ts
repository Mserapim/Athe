import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
}

export class ApiRhPvfRequestsIdCancelamentosTeletrabalhosResponseItem {
    tipo_solicitacao: string;
    referencia: string;
    status: string;
    inicio_plano: string;
    fim_plano: string;
    date: Date;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdCancelamentosTeletrabalhosResponseItem> {}

export async function apiRhPvfRequestsIdCancelamentosTeletrabalhos(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/requests/' + payload.id + '/cancelamentos/teletrabalhos'
    );
    return data;
}
