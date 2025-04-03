import { usePost } from 'api/@base/use-post';

interface Payload {
    viagem: number;
    nome: string;
    cpf: string;
    email: string;
    data_nasc: Date;
    cargo: number;
    tipo_conta: number;
    banco: number;
    agencia_numero: string;
    agencia_dv: string;
    conta_numero: string;
    conta_dv: string;
}

export class ResponseItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    servidor: number;
    viagem: number;
    conta_bancaria_pgto: number;
    agencia_numero: string;
    agencia_dv: string;
    conta_numero: string;
    conta_dv: string;
}

export async function apiDiariasColaboradorEventualCriar(
    payload: Payload
) {
    const { data } = await usePost<ResponseItem>(
        'diarias/colaborador-eventual/criar/',
        payload
    );

    return data;
}
