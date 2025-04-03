import { useGet } from 'api/@base/use-get';

export interface ApiDetalheSolicitacaoAuxilioCrecheIRPayload {
    id: number;
}

export class ApiVdfSolicitacaoAuxilioCrecheIrResponse {
    pk: number;
    dependente_id: number;
    dependente_name: string;
    anexo_id: number;
    dependente_aux_creche: boolean;
    dependente_ir: boolean;
    capacidade: number;
    tipo_parentesco: number;
    tipo_parentesco_name: string;
    dependente_tipo: number;
    dependente_tipo_name: string;
    observacao: string
}

export async function apiVdfDetalhesSolicitacaoAuxilioCrecheIr(
    payload: ApiDetalheSolicitacaoAuxilioCrecheIRPayload
) {
    const { data } =
        await useGet<ApiVdfSolicitacaoAuxilioCrecheIrResponse>(
            '/vdf/solicitacao-aux-creche-ir/',
            payload
        );
    return data;
}
