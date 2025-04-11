/**
 *
 **/
Ext._define('adm.patrimonio.localizacao.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.localizacao.Window',

    getToolbar: function() { return []; }
});

// core.RestfulGrid.register(
//     'adm.patrimonio.localizacao.Restful',
//     'adm.patrimonio.localizacao.Grid'
// );
