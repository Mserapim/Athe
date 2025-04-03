import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
    keyword?: number;
    per_page?: number;
}

export class ApiRhPvfRequestsIdTeleworksTargetsItem {
    id: number;
    total_completed: number;
    mark_situation: number;
    observation: string;
    mark_plan: { meta: number };
    request: number;
    mark_situation_label: string;
    anexo_id: null;
    saldo_devedor: number;
    qtde_dias_afastamento_mes: number;
    qtde_dias_mes: number;
    meta_mes: number;
    qtde_dias_mes_proporcional: number;
    observation_required?: boolean;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdTeleworksTargetsItem> {}

export async function apiRhPvfRequestsIdTeleworksTargets(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/requests/' + payload.requestId + '/teleworks/targets/',
        payload
    );
    return data;
}
