import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    historico_id: number;
}

export class ResponseItem {
    obs: string;
    numero_empenho: number;
    numero_nota_liquidacao: number;
    numero_ordem_bancaria: number;
    qtd_total_diarias_deferido: number;
    acomp_autoridade_deferimento: boolean;
    gedoc: string;
    anexos: any[]
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasHistoricoAnexosInformacoes(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/viagem/detalhe/historico/anexos-informacoes/',
        payload
    );
    return data;
}
