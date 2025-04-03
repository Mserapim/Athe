import { usePost } from 'api/@base/use-post';

interface Payload {
    id:number;
    conta_bancaria_pgto: number;
}

export class ResponseItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    servidor: number;
    viagem: number;
    conta_bancaria_pgto: number;
    qtd_destinos: number;
}

export async function apiDiariasBeneficiarioEditar(
    payload: Payload
) {
    const { data } = await usePost<ResponseItem>(
        'diarias/minhas-diarias/beneficiario/editar/',
        payload
    );

    return data;
}
