Ext._define('rh.dependent.byUser.Grid', {
    extend: 'rh.dependente.DependenteGrid',
    restWindow: 'rh.dependent.byUser.Window',
});

core.RestfulGrid.register(
    'rh.dependent.byUser.Restful',
    'rh.dependent.byUser.Grid'
);
