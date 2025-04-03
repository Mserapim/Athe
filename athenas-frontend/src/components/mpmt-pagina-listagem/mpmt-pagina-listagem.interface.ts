export type MpmtPaginaListagemOrdenacao = {
    order_by?: string;
};

export type MpmtPaginaListagemPaginacao = Record<string, any> & {
    per_page?: number;
    page?: number;
};

export type MpmtPaginaListagemLinha = Record<string, any>;

export type MpmtPaginaListagemAcao = {
    titulo?: string;
    icone?: string;
    requerPermissao?: 'criar' | 'editar' | 'ver' | 'apagar' | string;
    aoClicar?: (
        linha: MpmtPaginaListagemLinha
    ) => void /** Ação ao clicar sobre a celula */;
    visivelSe?: (
        linha: MpmtPaginaListagemLinha
    ) => boolean /** Define se o valor da celula será ou não exibido */;
}

export type MpmtPaginaListagemColuna = {
    codigo: string;
    titulo?: string;
    tipo?: 'TEXTO' | 'BOLEANO' | 'NUMERICO' | 'DATA' | 'DATA_HORA' | 'OBJETO' | 'ACOES' | 'BOLEANO_ICONE';
    visivel?: boolean;
    ordenavel?: boolean;
    largura?: string;
    limitar_caracteres?: boolean;
    construirEstilo?: (linha: MpmtPaginaListagemLinha) => string;
    transformarValor?: (
        linha: MpmtPaginaListagemLinha
    ) =>
        | string
        | Date
        | number /** Permite alterar/formatar o valor a ser exibido na celula */;
    aoClicar?: (
        linha: MpmtPaginaListagemLinha
    ) => void /** Ação ao clicar sobre a celula */;
    visivelSe?: (
        linha: MpmtPaginaListagemLinha
    ) => boolean /** Define se o valor da celula será ou não exibido */;
    tooltip?: (linha: MpmtPaginaListagemLinha) => string;

};
