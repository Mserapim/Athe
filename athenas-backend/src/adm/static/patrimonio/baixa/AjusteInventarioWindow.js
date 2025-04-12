/**
 *
 **/
Ext._define('adm.patrimonio.baixa.AjusteInventarioWindow', {
    extend: 'adm.patrimonio.baixa.Window',

    rest: 'adm.patrimonio.baixa.AjusteInventarioRestful'
});

adm.patrimonio.baixa.Grid.register(
    'nota-baixa-ajuste-inventario',
    'Nota de Ajuste de Inventário',
    'icon-patrimonio icon-pat-nota-baixa-ajuste-inventario',
    'adm.patrimonio.baixa.AjusteInventarioWindow'
);
