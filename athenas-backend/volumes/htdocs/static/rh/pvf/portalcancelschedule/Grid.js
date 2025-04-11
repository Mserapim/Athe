Ext._define('rh.pvf.portalcancelschedule.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pvf.portalcancelschedule.Window',


});


core.RestfulGrid.register(
    'rh.pvf.portalcancelschedule.Restful',
    'rh.pvf.portalcancelschedule.Grid'
);    