import { usePost } from 'api/@base/use-post';
import { ColaboradorEventualModelReturn } from '../modelos/colcadorardor-eventual-model';

interface Payload {
    id: number;
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


export async function apiDefinPagamentoColaboradorEventualEditar(
    payload: Payload
) {
    const { data } = await usePost<ColaboradorEventualModelReturn>(
        'rh/defin/pagamento-colaborador/editar/',
        payload
    );

    return data;
}
