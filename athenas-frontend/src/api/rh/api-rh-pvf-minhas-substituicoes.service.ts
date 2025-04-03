import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface ApiRhPvfMinhasSolicitacoesPayload extends ListPayload {
    keyword?: string;
    dt_fim?: string;
    dt_inicio?: string;
}

export class ApiRhPvfMinhasSolicitacoesResponseItem {
    serv_substituto: string;
    serv_substituido: string;
    data_inicio: Date;
    data_fim: Date;
    titularidade: string;
    able_to_pay: boolean;
    cumulativa: string;
    paid_out: boolean;
    pay_month: string | null;
    pay_year: string | null;
}

class Response extends ListPaginated<ApiRhPvfMinhasSolicitacoesResponseItem> {}

export async function apiRhPvfMinhasSolicitacoes(
    payload: ApiRhPvfMinhasSolicitacoesPayload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/minhas-substituicoes/',
        payload
    );
    return data;
}
