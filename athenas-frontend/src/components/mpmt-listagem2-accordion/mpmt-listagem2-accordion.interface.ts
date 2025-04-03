export type MpmtListagem2Ordenacao = {
    order_by?: string;
};

export type MpmtListagem2Paginacao = Record<string, any> & {
    per_page?: number;
    page?: number;
};

export type MpmtListagem2Linha = Record<string, any>;

export type MpmtListagem2Coluna = {
    codigo: string;
    titulo?: string;
    lista?: boolean;
    tipo?:
        | 'TEXTO'
        | 'LISTA'
        | 'NUMERO'
        | 'MOEDA'
        | 'CPF'
        | 'BOLEANO'
        | 'BOLEANO_ICONE'
        | 'IMAGE'
        | 'ICONE'
        | 'LINK'
        | 'DATA'
        | 'DATA_HORA'
        | 'BOTAO_PRIMARIO'
        | 'BOTAO_CONTORNO'
        | 'VER_MAIS'
        | 'ACOES'
        | 'VALOR_E_ACAO';
    visivel?: boolean;
    ordenavel?: boolean;
    /** Permite alterar/formatar o valor a ser exibido na celula */
    transformarValor?: (linha: MpmtListagem2Linha) => string | Date | number | string[];
    /** Ação ao clicar sobre a celula */
    aoClicar?: (linha: MpmtListagem2Linha) => void;
    /** Define se o valor da celula será ou não exibido */
    exibirSe?: (linha: MpmtListagem2Linha) => boolean;
    acoes?: {
        titulo?: string;
        icone?: string;
        /** Ação ao clicar sobre a celula */
        aoClicar?: (linha: MpmtListagem2Linha) => void;
        /** Define se o valor da celula será ou não exibido */
        exibirSe?: (linha: MpmtListagem2Linha) => boolean;
        requerPermissao?: 'criar' | 'editar' | 'ver' | 'apagar' | string;
    }[];
};
