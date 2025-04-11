/**
 *
 **/
Ext._define('adm.patrimonio.baixa.MudancaClassificacaoWindow', {
    extend: 'adm.patrimonio.baixa.Window',

    rest: 'adm.patrimonio.baixa.MudancaClassificacaoRestful'
});

adm.patrimonio.baixa.Grid.register(
    'nota-mudanca-classificacao',
    'Nota de Mudança de Classificação',
    'icon-patrimonio icon-pat-nota-mudanca-classificacao',
    'adm.patrimonio.baixa.MudancaClassificacaoWindow'
);
