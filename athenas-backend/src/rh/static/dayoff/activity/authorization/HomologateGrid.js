Ext._define('rh.dayoff.activity.authorization.HomologateGrid', {
    extend: 'rh.dayoff.activity.Grid',
    rest: 'rh.dayoff.activity.authorization.HomologateRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.activity.authorization.HomologateRestful',
    'rh.dayoff.activity.authorization.HomologateGrid'
);

