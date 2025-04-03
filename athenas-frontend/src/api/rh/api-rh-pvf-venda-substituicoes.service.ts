import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    total_days?: number;
    type_usufruct: TypeUsufructEnum;
}

export class ApiRhPvfVendaSubstituicoesResponseItem {
    serv_substituto: string;
    serv_substituido: string;
    data_inicio: Date;
    data_fim: Date;
    cumulativa: string;
    able_to_pay: boolean;
    pay_month: number;
    pay_year: number;
    paid_out: boolean;
}

class Response extends ListPaginated<ApiRhPvfVendaSubstituicoesResponseItem> {}

export async function apiRhPvfVendaSubstituicoes(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/venda-substituicoes',
        payload
    );
    return data;
}
