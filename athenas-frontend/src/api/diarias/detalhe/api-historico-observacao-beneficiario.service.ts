import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    beneficiario: number;
    fluxo?: number;
}

export class Response {
    obs: string;
    feedback: string;
    acao_por: string;
}

export async function apiObservacaoHistoricoFluxoBeneficiario(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/viagem/detalhe/historico/observacao/',
        payload
    );
    return data;
}
