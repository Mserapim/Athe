/**
 *
 **/
Ext._define('adm.patrimonio.baixa.SinistroWindow', {
    extend: 'adm.patrimonio.baixa.Window',

    rest: 'adm.patrimonio.baixa.SinistroRestful'
});

adm.patrimonio.baixa.Grid.register(
    'nota-baixa-sinistro',
    'Nota de Sinistro',
    'icon-patrimonio icon-pat-nota-baixa-sinistro',
    'adm.patrimonio.baixa.SinistroWindow'
);
