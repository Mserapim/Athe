
Ext._define('common.saci.params.WorkplaceGrid', {
    extend: 'rh.workplace.Grid',

    restWindow: 'common.saci.params.WorkplaceWindow'
});

core.RestfulGrid.register(
    'common.saci.params.WorkplaceRestful',
    'common.saci.params.WorkplaceGrid'
);
