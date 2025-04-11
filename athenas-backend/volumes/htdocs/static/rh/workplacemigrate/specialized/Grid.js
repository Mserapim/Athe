Ext._define('rh.workplacemigrate.specialized.Grid', {
    extend: 'rh.workplacemigrate.Grid',

    restWindow: 'rh.workplacemigrate.specialized.Window',
});

core.RestfulGrid.register(
    'rh.workplacemigrate.specialized.Restful',
    'rh.workplacemigrate.specialized.Grid'
);

