import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    beneficiario_id: number;
}

export class ResponseItem {
    historico_id: number;
    viagem_data_inicio: string;
    viagem_data_fim: string;
    etapa: string;
    situacao: string;
    ação_por: string;
    data_acao: string;
    beneficiario: string;
    tipo_historico: string;
    tem_anexo: boolean;
    tem_informacao: boolean;
    decisao: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasDetalheBeneficiarioHistorico(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/viagem/detalhe/beneficiario/historico',
        payload
    );
    return data;
}
