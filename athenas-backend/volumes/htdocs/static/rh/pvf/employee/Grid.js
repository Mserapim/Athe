Ext._define('rh.pvf.employee.Grid', {
    extend: 'rh.employee.Grid',

    restWindow: 'rh.pvf.employee.Window',

    keywordFieldWidth: 180,


});    

core.RestfulGrid.register(
    'rh.pvf.employee.Restful',
    'rh.pvf.employee.Grid'
);    