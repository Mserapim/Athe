import { usePost } from 'api/@base/use-post';

interface Payload {
    tipo_conta: number;
    principal?: boolean;
    banco: number;
    servidor: number;

    agencia_numero: string;
    agencia_dv: string;
    conta_numero: string;
    conta_dv: string;
}

export class ResponseItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    tipo_conta: number;
    agencia: string;
    conta_corrente_completa: string;
    principal: boolean;
    banco: number;
    unicode: string;
    servidor: number;

    agencia_numero: string;
    agencia_dv: string;
    conta_numero: string;
    conta_dv: string;
    
}

export async function apiRhDadosBancariosServidorContaCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'rh/dados-bancarios/servidor/conta/criar/',
        payload
    );
    return data.data;
}
