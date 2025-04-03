import { usePost } from 'api/@base/use-post';

export interface ApiVdfSolicitacaoAuxCrecheIrReenviarPayload {
    id: number,
    pessoa_familia_id: number,
    anexo_id: number,
    dependente_aux_creche?: boolean,
    dependente_ir: boolean,
    capacidade: number,
    tipo_parentesco: number,
    dependente_tipo: number,
    observacao: string;
}

export async function apiVdfSolicitacaoAuxCrecheIrReenviarCriar(
    payload: ApiVdfSolicitacaoAuxCrecheIrReenviarPayload
) {
    const { data } = await usePost<any>(
        '/vdf/solicitacao-aux-creche-ir/reenviar/',
        payload
    );
    return data;
}
