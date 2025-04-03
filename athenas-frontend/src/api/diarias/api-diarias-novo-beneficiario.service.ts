import { usePost } from 'api/@base/use-post';

interface Payload {
    servidor: number;
    viagem: number;
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

export async function apiDiariasBeneficiarioCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/minhas-diarias/beneficiario/criar/',
        payload
    );

    return data.data;
}
