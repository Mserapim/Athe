import { usePost } from 'api/@base/use-post';

export interface ApiVdfSolicitacaoAuxCrecheIrPayload {
    pessoa_familia_id: number,
    anexo_id: number,
    dependente_aux_creche?: boolean,
    dependente_ir: boolean,
    capacidade: number,
    tipo_parentesco: number,
    dependente_tipo: number,
    observacao: string;
}

export async function apiVdfSolicitacaoAuxCrecheIrCriar(
    payload: ApiVdfSolicitacaoAuxCrecheIrPayload
) {
    const { data } = await usePost<any>(
        '/vdf/solicitacao-aux-creche-ir/criar/',
        payload
    );
    return data;
}
