import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id?: number;
    keyword?: number;
    situacao?: number;
}

export class ApiVdfSolicitacaoFolhaPontoAfastamentoItem {
    id: number;
    data_solicitacao: Date;
    tipo_solicitacao: string;
    situacao: string;
    agendamentos: [
        {
            data_inicio: Date;
            data_fim: Date;
        }
    ];
}

export class ApiVdfSolicitacaoFolhaPontoAfastamento extends ListPaginated<ApiVdfSolicitacaoFolhaPontoAfastamentoItem> {}

export async function apiVdfSolicitacaoFolhaPontoAfastamento(payload: Payload) {
    const { data } = await useGet<ApiVdfSolicitacaoFolhaPontoAfastamento>(
        'vdf/solicitacao-folhaponto-afastamentos/',
        payload
    );
    return data;
}
