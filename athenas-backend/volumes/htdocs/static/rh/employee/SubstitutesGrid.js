/**
 *
 **/
Ext._define('rh.employee.SubstitutesGrid', {
    extend: 'rh.employee.Grid',
    rest: 'rh.employee.SubstitutesRestful',
});

core.RestfulGrid.register(
    'rh.employee.SubstitutesRestful',
    'rh.employee.SubstitutesGrid'
);

