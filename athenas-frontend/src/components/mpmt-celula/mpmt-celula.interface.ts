export type MpmtOrdenacao = {
    order_by?: string;
};

export type MpmtPaginacao = Record<string, any> & {
    per_page?: number;
    page?: number;
};

export type MpmtLinha = Record<string, any>;

export type MpmtColuna = {
    codigo: string;
    titulo?: string;
    tipo?:
        | 'TEXTO'
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
        | 'VALOR_E_ACAO'
        | 'CHECKBOX'
        | 'RADIO';
    visivel?: boolean;
    ordenavel?: boolean;
    /** Permite alterar/formatar o valor a ser exibido na celula */
    transformarValor?: (linha: MpmtLinha) => string | Date | number;
    /** Ação ao clicar sobre a celula */
    aoClicar?: (linha: MpmtLinha) => void;
    /** Define se o valor da celula será ou não exibido */
    exibirSe?: (linha: MpmtLinha) => boolean;
    acoes?: {
        titulo?: string;
        icone?: string;
        requerPermissao?: 'criar' | 'editar' | 'ver' | 'apagar' | string;
        /** Ação ao clicar sobre a celula */
        aoClicar?: (linha: MpmtLinha) => void;
        /** Define se o valor da celula será ou não exibido */
        exibirSe?: (linha: MpmtLinha) => boolean;
    }[];
};
