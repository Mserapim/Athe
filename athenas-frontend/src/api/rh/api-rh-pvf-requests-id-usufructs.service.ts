import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';
import { ListPayload } from 'api/@base/list-payload';

interface Payload extends ListPayload {
    requestId: number;
}

export class ApiRhPvfRequestsIdUsufructsResponseItem {
    pk: number;
    start_date: Date;
    end_date: Date;
    days: number;
    type_usufruct: number;
    payment_competence: string;
    payment_installments: number;
    numero_parcela: number;
}

export class ApiRhPvfRequestsIdUsufructsPayloadItem {
    requestId: number;
    pk: number;
    start_date: Date;
    end_date: Date;
    days: number;
    type_usufruct: number;
    payment_competence: string;
    payment_installments: number;
    numero_parcela: number;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdUsufructsResponseItem> {}

export async function apiRhPvfRequestsIdUsufructs(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/requests/' + payload.requestId + '/usufructs',
        payload
    );
    return data;
}

export async function apiPOSTRhPvfRequestsIdUsufructs(
    payload: ApiRhPvfRequestsIdUsufructsPayloadItem
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/' + payload.requestId + '/payment/',
        payload
    );
    return data;
}
