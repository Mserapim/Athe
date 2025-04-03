export class PagamentoModelReturn {
    id: number;
    cbo: number;
    cbo_display: string;
    pessoa: number;
    folha: number;
    folha_display: string;
    contra_cheque: number;
    contra_cheque_display: string;
    lotacao: number;
    lotacao_display: string;
    data_pagamento: Date;
    valor_bruto: number;
    valor_inss: number;
    isento_inss: boolean;
    natureza_atividade: number;
    natureza_atividade_display: number;
    contribuicao_parcial: number;
    contribuido: boolean;
    valor_ir: number;
    valor_liquido: number;
    aplicado_folha: boolean;
}
