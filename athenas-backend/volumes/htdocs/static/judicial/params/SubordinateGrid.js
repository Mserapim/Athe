Ext._define('judicial.params.SubordinateGrid', {
    extend: 'rh.employee.Grid',

    restWindow: 'judicial.params.SubordinateWindow'
});

core.RestfulGrid.register(
    'judicial.params.SubordinateRestful',
    'judicial.params.SubordinateGrid'
);
