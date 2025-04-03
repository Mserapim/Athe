export type MpmtListagem2Ordenacao = {
    order_by?: string;
};

export type MpmtListagem2Paginacao = Record<string, any> & {
    per_page?: number;
    page?: number;
};

export type MpmtListagem2Linha = Record<string, any>;

export type MpmtListagem2Coluna = {
    quebrarPalavra?: boolean;
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
        | 'VER_MAIS_DESTACADO'
        | 'ACOES'
        | 'ACAO_OU_ACOES_COM_DESTAQUE'
        | 'LISTA'
        | 'VALOR_E_ACAO'
        | 'EXECUCAO';
    visivel?: boolean;
    ordenavel?: boolean;
    width?: string;
    /** Permite alterar/formatar o valor a ser exibido na celula */
    transformarValor?: (linha: MpmtListagem2Linha) => string | Date | number;
    /** Ação ao clicar sobre a celula */
    aoClicar?: (linha: MpmtListagem2Linha) => void;
    /** Define se o valor da celula será ou não exibido */
    exibirSe?: (linha: MpmtListagem2Linha) => boolean;
    tooltip?: (linha: MpmtListagem2Linha) => string;
    construirEstilo?: (linha: MpmtListagem2Linha) => string;
    acoes?: {
        titulo?: string;
        icone?: string;
        icone_linha?: boolean;
        requerPermissao?: 'criar' | 'editar' | 'ver' | 'apagar' | string;
        cor?: (linha: MpmtListagem2Linha) => string;
        /** Ação ao clicar sobre a celula */
        aoClicar?: (linha: MpmtListagem2Linha) => void;
        /** Define se o valor da celula será ou não exibido */
        exibirSe?: (linha: MpmtListagem2Linha) => boolean;
    }[];
};
