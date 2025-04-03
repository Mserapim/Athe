import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';

export interface Payload extends ListPayload {}

export class ApiAnotacaoPessoalTiposAnotacaoResponseItem {
    value: number;
    label: string;
}

class Response extends ListPaginated<ApiAnotacaoPessoalTiposAnotacaoResponseItem> {}

export async function apiAnotacaoPessoalTiposAnotacao(payload: Payload) {
    const { data } = await useGet<Response>(
        'anotacao-pessoal/tipos-anotacao',
        payload
    );
    return data;
}
