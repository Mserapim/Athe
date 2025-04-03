import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsIdResponse {
    pk?: number;
    portal_request_type?: number;
    type_of_request?: string;
    date?: Date;
    employee?: number;
    employee_name?: string;
    status?: number;
    status_name?: string;
    step_current?: number;
    reference?: string;
    step_current_name?: string;
    approver?: number;
    approver_name?: string;
    metas_saldo_devedor?: {
        saldo_devedor: number;
        descricao: string;
        descricacao: string;
    }[];
    parcel_number?: number;
    acquisitive_period?: string;
    days_awaiting_approval?: string;
    plan_work_id?: number;
    start_work_plan?: string;
    end_work_plan?: string;
    lotacao_teletrabalho?: string;
    total_consolidado?: number;
    anexo_id?: number;
    anexo?: number;
    anexo_name?: string;
    termo_aceite?: boolean;
    classe_atual?: string;
    classe_progredir?: string;
}

export async function apiRhPvfRequestsId(payload: Payload) {
    const { data } = await useGet<ApiRhPvfRequestsIdResponse>(
        'rh/pvf/requests/' + payload.requestId + '/'
    );
    return data;
}
