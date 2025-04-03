import { usePost } from 'api/@base/use-post';

interface Payload {
    viagem: number;
    beneficiario: number;
    numero_ordem_bancaria: number;
    data_pagamento?: string;
    anexos: any[];
}

export class ApiAnaliseDefinOrdemBancariaCriar {
    viagem: number;
    beneficiario: number;
    numero_ordem_bancaria: number;
    data_pagamento?: string;
    anexos: any[];
}

export async function apiAnaliseDefinOrdemBancariaCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-ordem-bancaria-defin/criar/',
        payload
    );
    return data.data;
}