Ext._define('rh.employee.workplace.ownerlocation.Grid', {
    extend: 'rh.employee.workplace.Grid',
    restWindow: 'rh.employee.workplace.managerbyemployee.Window',
    rest: 'rh.employee.workplace.ownerlocation.Restful',

});

core.RestfulGrid.register(
    'rh.employee.workplace.ownerlocation.Restful',
    'rh.employee.workplace.managerbyemployee.WorkassignmentGrid'
);
