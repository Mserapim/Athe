Ext._define('rh.employee.registration.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.employee.registration.Window',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        rh.employee.registration.Grid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'rh.employee.registration.Restful',
    'rh.employee.registration.Grid'
);
