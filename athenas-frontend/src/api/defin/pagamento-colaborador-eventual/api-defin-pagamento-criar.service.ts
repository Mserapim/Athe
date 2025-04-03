import { usePost } from 'api/@base/use-post';
import { PagamentoModelReturn } from '../modelos/pagamento-model';

interface Payload {
    cbo: number;
    lotacao: number;
    natureza_atividade: number;
    data_pagamento: Date;
    valor_bruto: number;
    contribuicao_parcial: number;
    isento_inss: boolean;
    contribuido: boolean;
    pessoa: number;
}


export async function apiDefinPagamentoColaboradorEventualCriar(
    payload: Payload
) {
    const { data } = await usePost<PagamentoModelReturn>(
        'rh/defin/pagamento-colaborador/criar/',
        payload
    );

    return data;
}
