Ext._define('rh.telefone.byUser.Grid', {
    extend: 'rh.telefone.TelefoneGrid',
    restWindow: 'rh.telefone.byUser.Window',
});

core.RestfulGrid.register(
    'rh.telefone.byUser.Restful',
    'rh.telefone.byUser.Grid'
);
