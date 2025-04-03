import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface ApiRhPvfMinhasAnotacoesPayload extends ListPayload {
    keyword?: string;
}

export class ApiRhPvfMinhasAnotacoesResponseItem {
    pk: number;
    texto?: string;
    tipo_label?: string;
    documento_tipo_label?: string;
    publicacao_label?: string;
    data_publicacao?: Date;
    documento_numero?: string;
    documento_ano?: number;
    documento_data?: Date;
    data_efeito_inicio?: Date;
    data_efeito_fim?: string;
    gedoc_numero?: string;
}

class Response extends ListPaginated<ApiRhPvfMinhasAnotacoesResponseItem> {}

export async function apiRhPvfMinhasAnotacoes(
    payload: ApiRhPvfMinhasAnotacoesPayload
) {
    const { data } = await useGet<Response>(
        'anotacao-pessoal/minhas-anotacoes/',
        payload
    );
    return data;
}
