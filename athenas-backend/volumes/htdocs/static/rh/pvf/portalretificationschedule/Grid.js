Ext._define('rh.pvf.portalretificationschedule.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pvf.portalretificationschedule.Window',


});


core.RestfulGrid.register(
    'rh.pvf.portalretificationschedule.Restful',
    'rh.pvf.portalretificationschedule.Grid'
);    