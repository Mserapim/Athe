import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

interface Payload {
    id_solicitacao: number;
}

export class ApiVdfSolicitacaoHistoricoAnexosResponseItem {
    id: string | number;
    nome_arquivo: string;
    origem: string;
}

export class ApiVdfSolicitacaoHistoricoAnexosResponse extends ListPaginated<ApiVdfSolicitacaoHistoricoAnexosResponseItem> {}

export async function apiVdfSolicitacaoHistoricoAnexos(payload: Payload) {
    const { data } = await useGet<ApiVdfSolicitacaoHistoricoAnexosResponse>(
        'vdf/solicitacao-historico-anexos',
        payload
    );
    return data;
}
